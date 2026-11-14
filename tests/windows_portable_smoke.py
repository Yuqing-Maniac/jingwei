#!/usr/bin/env python3
"""Exercise the final Windows portable ZIP, including its native launcher.

Run on Windows: python tests/windows_portable_smoke.py --archive <zip-or-directory>
Requires only websocket-client in addition to Python's standard library. Linux
can check syntax/help but deliberately cannot claim a successful startup test.
Artifacts (including failures) go to _work/windows-startup-smoke by default.
"""
import argparse
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import traceback
import urllib.request
import uuid
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def error_info(exc):
    return {"type": type(exc).__name__, "message": str(exc),
            "winerror": getattr(exc, "winerror", None), "errno": getattr(exc, "errno", None),
            "traceback": traceback.format_exc()}


class Win32:
    """Pointer-width-correct native APIs; never loads an executable as code."""
    def __init__(self):
        self.k = ctypes.WinDLL("kernel32", use_last_error=True)
        self.u = ctypes.WinDLL("user32", use_last_error=True)
        self.callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        declarations = [
            (self.k, "LoadLibraryExW", [wintypes.LPCWSTR, wintypes.HANDLE, wintypes.DWORD], wintypes.HMODULE),
            (self.k, "FreeLibrary", [wintypes.HMODULE], wintypes.BOOL),
            (self.k, "FindResourceW", [wintypes.HMODULE, ctypes.c_void_p, ctypes.c_void_p], wintypes.HANDLE),
            (self.k, "SizeofResource", [wintypes.HMODULE, wintypes.HANDLE], wintypes.DWORD),
            (self.k, "LoadResource", [wintypes.HMODULE, wintypes.HANDLE], wintypes.HANDLE),
            (self.k, "LockResource", [wintypes.HANDLE], ctypes.c_void_p),
            (self.k, "ReleaseActCtx", [wintypes.HANDLE], None),
            (self.k, "CreateToolhelp32Snapshot", [wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            (self.k, "CloseHandle", [wintypes.HANDLE], wintypes.BOOL),
            (self.u, "EnumWindows", [self.callback, wintypes.LPARAM], wintypes.BOOL),
            (self.u, "EnumChildWindows", [wintypes.HWND, self.callback, wintypes.LPARAM], wintypes.BOOL),
            (self.u, "GetWindowThreadProcessId", [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),
            (self.u, "GetWindowTextLengthW", [wintypes.HWND], ctypes.c_int),
            (self.u, "GetWindowTextW", [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
            (self.u, "PostMessageW", [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM], wintypes.BOOL),
            (self.u, "GetDlgItem", [wintypes.HWND, ctypes.c_int], wintypes.HWND),
            (self.u, "SendMessageTimeoutW", [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM, wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t)], wintypes.LPARAM),
        ]
        for lib, name, args, result in declarations:
            fn = getattr(lib, name)
            fn.argtypes, fn.restype = args, result

    def manifests(self, exe, dest):
        # LOAD_LIBRARY_AS_DATAFILE avoids executing DllMain or loading imports.
        module = self.k.LoadLibraryExW(str(exe), None, 0x00000002)
        if not module:
            raise ctypes.WinError(ctypes.get_last_error())
        resource = None
        try:
            # Standard CREATEPROCESS_MANIFEST_RESOURCE_ID is 1. Electron and
            # the portable launcher both embed their application manifest here.
            resource = self.k.FindResourceW(module, ctypes.c_void_p(1), ctypes.c_void_p(24))
            if not resource:
                raise ctypes.WinError(ctypes.get_last_error())
            size = self.k.SizeofResource(module, resource)
            loaded = self.k.LoadResource(module, resource)
            pointer = self.k.LockResource(loaded) if loaded else None
            if not size or not pointer:
                raise ctypes.WinError(ctypes.get_last_error())
            data = ctypes.string_at(pointer, size)
            (dest / "RT_MANIFEST-1.xml").write_bytes(data)
        finally:
            self.k.FreeLibrary(module)

        class ACTCTXW(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.ULONG), ("dwFlags", wintypes.DWORD),
                        ("lpSource", wintypes.LPCWSTR), ("wProcessorArchitecture", wintypes.WORD),
                        ("wLangId", wintypes.WORD), ("lpAssemblyDirectory", wintypes.LPCWSTR),
                        ("lpResourceName", ctypes.c_void_p), ("lpApplicationName", wintypes.LPCWSTR),
                        ("hModule", wintypes.HMODULE)]
        create = self.k.CreateActCtxW
        create.argtypes, create.restype = [ctypes.POINTER(ACTCTXW)], wintypes.HANDLE
        context = ACTCTXW()
        context.cbSize = ctypes.sizeof(context)
        context.dwFlags = 0x00000008 | 0x00000004  # RESOURCE_NAME_VALID | ASSEMBLY_DIRECTORY_VALID
        context.lpSource, context.lpAssemblyDirectory = str(exe), str(exe.parent)
        context.lpResourceName = 1
        ctypes.set_last_error(0)
        handle = create(ctypes.byref(context))
        code = ctypes.get_last_error()
        passed = handle not in (None, ctypes.c_void_p(-1).value)
        result = {"exe": str(exe), "manifestResourceId": 1, "manifestBytes": len(data),
                  "CreateActCtxW": passed, "winerror": 0 if passed else code}
        save_json(dest / "activation-context.json", result)
        if not passed:
            raise ctypes.WinError(code)
        self.k.ReleaseActCtx(handle)
        return result

    def process_table(self):
        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                        ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                        ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                        ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                        ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]
        first, nxt = self.k.Process32FirstW, self.k.Process32NextW
        for fn in (first, nxt):
            fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
            fn.restype = wintypes.BOOL
        snapshot = self.k.CreateToolhelp32Snapshot(2, 0)
        if snapshot in (None, ctypes.c_void_p(-1).value):
            raise ctypes.WinError(ctypes.get_last_error())
        result = []
        try:
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(entry)
            valid = first(snapshot, ctypes.byref(entry))
            while valid:
                result.append({"pid": entry.th32ProcessID, "parent": entry.th32ParentProcessID,
                               "name": entry.szExeFile})
                valid = nxt(snapshot, ctypes.byref(entry))
        finally:
            self.k.CloseHandle(snapshot)
        return result

    def dialog_texts(self, pid):
        found = []

        def text(hwnd):
            buf = ctypes.create_unicode_buffer(self.u.GetWindowTextLengthW(hwnd) + 1)
            self.u.GetWindowTextW(hwnd, buf, len(buf))
            return buf.value

        def top(hwnd, _):
            owner = wintypes.DWORD()
            self.u.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value == pid:
                parts = [text(hwnd)]

                def child(ch, _param):
                    parts.append(text(ch))
                    return True

                self.u.EnumChildWindows(hwnd, self.callback(child), 0)
                found.append((hwnd, "\n".join(parts)))
            return True

        self.u.EnumWindows(self.callback(top), 0)
        return found


class Run:
    def __init__(self, native, dest, exe, args, env):
        self.native, self.dest = native, dest
        dest.mkdir(parents=True, exist_ok=True)
        self.pids, self.process, self.cdp = set(), None, None
        self.stdout = (dest / "stdout.log").open("wb")
        self.stderr = (dest / "stderr.log").open("wb")
        self.record = {"command": [str(exe), *map(str, args)], "cwd": str(dest),
                       "startupLog": env.get("JW_STARTUP_LOG"), "processes": []}
        try:
            self.process = subprocess.Popen(self.record["command"], cwd=dest, env=env,
                                            stdout=self.stdout, stderr=self.stderr)
            self.pids.add(self.process.pid)
            self.record["pid"] = self.process.pid
        except OSError as exc:
            self.record["PopenError"] = error_info(exc)
            self.finish()
            raise

    def track(self):
        table = self.native.process_table()
        changed = True
        while changed:
            changed = False
            for proc in table:
                if proc["parent"] in self.pids and proc["pid"] not in self.pids:
                    self.pids.add(proc["pid"])
                    self.record["processes"].append(proc)
                    changed = True
        return table

    def finish(self):
        # The native launcher exits immediately after CreateProcessW; its
        # successful exit does NOT establish that Electron started or survived.
        if self.process:
            self.record["exitCodeBeforeCleanup"] = self.process.poll()
            try:
                table = self.track()
                live = {p["pid"] for p in table}
                if self.cdp:
                    try:
                        self.cdp.evaluate("window.jwDesk && window.jwDesk.closeNow()", timeout=3)
                    except Exception:
                        pass
                    self.cdp.close()
                    until = time.monotonic() + 5
                    while time.monotonic() < until:
                        live = {p["pid"] for p in self.native.process_table()}
                        if not self.pids.intersection(live):
                            break
                        time.sleep(0.2)
                cleanup = []
                for pid in sorted(self.pids.intersection(live)):
                    # Only PIDs originating from this test process tree.
                    result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                                            capture_output=True, timeout=15)
                    cleanup.append({"pid": pid, "exitCode": result.returncode,
                                    "stdout": result.stdout.decode("utf-8", "replace"),
                                    "stderr": result.stderr.decode("utf-8", "replace")})
                self.record["cleanup"] = cleanup
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
                self.record["exitCode"] = self.process.returncode
                self.record["exitCodeHex"] = hex(self.process.returncode & 0xffffffff)
            except Exception as exc:
                self.record["cleanupError"] = error_info(exc)
        self.stdout.close()
        self.stderr.close()
        save_json(self.dest / "process.json", self.record)
        for name in ("stderr.log", "startup.log"):
            log = self.dest / name
            if log.exists():
                print("DIAGNOSTIC " + self.dest.name + "/" + name + ":", flush=True)
                print(log.read_text(encoding="utf-8", errors="replace")[-16000:], flush=True)


class CDP:
    def __init__(self, url):
        import websocket
        self.ws = websocket.create_connection(url, timeout=5, suppress_origin=True,
                                              http_proxy_host=None)
        self.serial, self.events = 0, []

    def call(self, method, params=None, timeout=10):
        self.serial += 1
        ident = self.serial
        self.ws.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            self.ws.settimeout(max(0.1, end - time.monotonic()))
            message = json.loads(self.ws.recv())
            if message.get("id") == ident:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message.get("result", {})
            if "method" in message:
                self.events.append(message)
        raise TimeoutError("CDP " + method)

    def evaluate(self, expression, timeout=10):
        result = self.call("Runtime.evaluate", {"expression": expression, "awaitPromise": True,
                                               "returnByValue": True}, timeout)
        if result.get("exceptionDetails"):
            raise RuntimeError(result["exceptionDetails"])
        return result.get("result", {}).get("value")

    def screenshot(self, path):
        result = self.call("Page.captureScreenshot", {"format": "png"}, timeout=15)
        path.write_bytes(base64.b64decode(result["data"]))

    def close(self):
        self.ws.close()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def environment(dest):
    env = dict(os.environ)
    for key in ("ELECTRON_RUN_AS_NODE", "JW_TEST_OPEN", "JW_TEST_PATCH", "JW_TEST_PATCH_ROOT"):
        env.pop(key, None)
    env["JW_TEST_DIR"] = str(dest)
    env["JW_STARTUP_LOG"] = str(dest / "startup.log")
    return env


def node_probe(native, dest, exe):
    dest.mkdir(parents=True, exist_ok=True)
    marker, script = dest / "node 回执 marker.json", dest / "node 参数 probe.js"
    argument = '参数 with spaces 中文 "quoted" 尾部\\'
    script.write_text("const fs=require('fs'); fs.writeFileSync(process.env.JW_NODE_MARKER,"
                      "JSON.stringify({argv:process.argv.slice(2),execPath:process.execPath,"
                      "platform:process.platform,arch:process.arch,pid:process.pid,"
                      "electron:process.versions.electron}), 'utf8');\n", encoding="utf-8")
    env = environment(dest)
    env.update(ELECTRON_RUN_AS_NODE="1", JW_NODE_MARKER=str(marker))
    run = Run(native, dest, exe, [str(script), argument], env)
    try:
        end = time.monotonic() + 120
        while time.monotonic() < end:
            run.track()
            if marker.exists():
                try:
                    data = json.loads(marker.read_text(encoding="utf-8"))
                except (ValueError, OSError):
                    time.sleep(0.1)
                    continue
                save_json(dest / "node-result.json", data)
                assert data["argv"] == [argument], data
                assert data["platform"] == "win32" and data["arch"] == "x64", data
                assert data.get("electron"), data
                assert Path(data["execPath"]).name == "JingWeiZhiTu.exe", data
                assert str(exe.parent if exe.parent.name == "JingWeiZhiTu" else exe.parent / "JingWeiZhiTu").casefold() == str(Path(data["execPath"]).parent).casefold(), data
                return data
            # Outer exit 0 is expected and its child can still be starting.
            if run.process.poll() not in (None, 0):
                raise RuntimeError("Node loader exited: " + str(run.process.returncode))
            time.sleep(0.2)
        raise TimeoutError("120s: no Node-mode marker from " + str(exe))
    finally:
        run.finish()


STATE_JS = r"""(async () => {
  const info = window.jwDesk ? await window.jwDesk.info() : null;
  const icons = typeof ICON_LIB === 'undefined' ? [] : ICON_LIB;
  const required = ['#jw-start','#jw-home','#jw-go','#jw-ver','#palette','#props','#svg','#b-help'];
  return {info, title:document.title, url:location.href, ready:document.readyState,
    generic:icons.length, countries:icons.reduce((n,i)=>n+Object.keys(i.countries||{}).length,0),
    missing:required.filter(s=>!document.querySelector(s)),
    homeVisible:!!document.querySelector('#jw-start.on'),
    countryOptions:Array.from(document.querySelectorAll('#pal-appearance option')).map(x=>x.value),
    homeCards:document.querySelectorAll('#jw-start [data-a]').length};
})()"""


def app_probe(native, dest, exe, version, extra_args=None):
    port = free_port()
    env = environment(dest)
    run = Run(native, dest, exe, ["--remote-debugging-address=127.0.0.1",
              "--remote-debugging-port=" + str(port), "--remote-allow-origins=*",
              "--user-data-dir=" + str(dest / "独立 user data"), *(extra_args or [])], env)
    last = None
    try:
        end = time.monotonic() + 120
        while time.monotonic() < end:
            table = run.track()
            live = {p["pid"] for p in table}
            if len(run.pids) > 1 and not run.pids.intersection(live):
                raise RuntimeError("Electron child exited before showing a window; see startup.log")
            if run.process.poll() not in (None, 0):
                raise RuntimeError("Electron launcher exited: " + str(run.process.returncode))
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as response:
                    targets = json.load(response)
                save_json(dest / "cdp-targets.json", targets)
                target = next((t for t in targets if t.get("type") == "page"
                               and "/app/index.html" in t.get("url", "").replace("\\", "/")), None)
                if target:
                    if run.cdp is None:
                        run.cdp = CDP(target["webSocketDebuggerUrl"])
                        run.cdp.call("Runtime.enable")
                        run.cdp.call("Log.enable")
                    state = run.cdp.evaluate(STATE_JS, timeout=min(10, max(0.5, end-time.monotonic())))
                    save_json(dest / "renderer-state.json", state)
                    info = (state or {}).get("info") or {}
                    if info.get("windowVisible") is True and state.get("ready") == "complete" and not state.get("missing"):
                        break
            except Exception as exc:
                last = error_info(exc)
                save_json(dest / "last-cdp-error.json", last)
            time.sleep(0.3)
        else:
            raise TimeoutError("120s: no visible ready application; last CDP error: " + str(last))
        run.cdp.screenshot(dest / "home.png")
        assert info["version"] == version, state
        assert info["platform"] == "win32" and info["arch"] == "x64", state
        assert info["windowVisible"] is True, state
        assert state["generic"] == 667 and state["countries"] == 621, state
        assert state["homeVisible"] and state["homeCards"] >= 6, state
        assert set(state["countryOptions"]) == {"generic", "cn", "us"}, state
        startup = dest / "startup.log"
        assert startup.is_file(), "Main process did not write JW_STARTUP_LOG"
        startup_text = startup.read_text(encoding="utf-8", errors="replace")
        assert "main process started" in startup_text and "main window loaded" in startup_text, startup_text
        canvas = run.cdp.evaluate("""(() => {
          document.querySelector('#jw-go').click(); clearSel(); render();
          return {homeVisible:document.querySelector('#jw-start').classList.contains('on'),
            missing:['#svg','#palette','#props','#gd-size','#gd-font','#gd-page','#pal-appearance']
              .filter(s=>!document.querySelector(s)),
            editing:{selection:!!window.JwSelectionBounds,labels:!!window.JwIconLabels,
              coverage:!!window.Coverage,layers:typeof layerSelection==='function',
              coveragePresets:SHAPES.filter(s=>s.k.indexOf('coverage-')===0).length}};
        })()""")
        save_json(dest / "canvas-options.json", canvas)
        run.cdp.screenshot(dest / "canvas-options.png")
        assert not canvas["homeVisible"] and not canvas["missing"], canvas
        assert all(canvas["editing"][key] for key in ("selection", "labels", "coverage", "layers")), canvas
        assert canvas["editing"]["coveragePresets"] == 4, canvas
        fatal = [e for e in run.cdp.events if e.get("method") == "Runtime.exceptionThrown"]
        assert not fatal, fatal
        return state
    finally:
        if run.cdp:
            try:
                save_json(dest / "cdp-events.json", run.cdp.events)
                if not (dest / "home.png").exists():
                    run.cdp.screenshot(dest / "failure.png")
            except Exception as exc:
                save_json(dest / "screenshot-error.json", error_info(exc))
        run.finish()


def missing_asar_probe(native, dest, outer):
    # Rename only the extracted test copy; restore even after errors/timeouts.
    asar = outer.parent / "JingWeiZhiTu" / "resources" / "app.asar"
    backup = asar.with_name("app.asar.smoke-" + uuid.uuid4().hex)
    asar.rename(backup)
    run = None
    try:
        run = Run(native, dest, outer, [], environment(dest))
        end, matched = time.monotonic() + 120, None
        while time.monotonic() < end:
            for hwnd, text in native.dialog_texts(run.process.pid):
                save_json(dest / "dialog.json", {"hwnd": hwnd, "text": text})
                if "程序资源不完整" in text and "重新解压" in text:
                    matched = text
                    # Exercise the actual OK button instead of relying on a synthetic menu command.
                    button = native.u.GetDlgItem(hwnd, 1)
                    response = ctypes.c_size_t()
                    if button:
                        native.u.SendMessageTimeoutW(button, 0x00F5, 0, 0, 2, 5000, ctypes.byref(response))
                    else:
                        native.u.PostMessageW(hwnd, 0x0010, 0, 0)
                    break
            if matched:
                run.process.wait(timeout=min(10, max(0.1, end-time.monotonic())))
                assert run.process.returncode == 2, run.process.returncode
                return {"message": matched, "exitCode": run.process.returncode}
            if run.process.poll() is not None:
                raise RuntimeError("Missing-asar launcher exited without expected dialog: " + str(run.process.returncode))
            time.sleep(0.2)
        raise TimeoutError("120s: missing-asar native error dialog was not observed")
    finally:
        if run:
            run.finish()
        backup.rename(asar)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="Final portable ZIP, or directory containing exactly one ZIP")
    parser.add_argument("--version", default=None, help="Expected application version; defaults to desktop/package.json")
    parser.add_argument("--original-exe", type=Path, default=None,
                        help="Optional pristine Electron EXE (or directory containing one EXE), copied beside the packaged inner EXE for a diagnostic control; never changes the normal-startup verdict")
    parser.add_argument("--output", type=Path, default=ROOT / "_work/windows-startup-smoke")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {"platform": sys.platform, "archive": str(args.archive.resolve()), "tests": [],
              "diagnostics": [], "diagnosticsAffectVerdict": False}
    if sys.platform != "win32":
        report["status"] = "skipped"
        report["reason"] = "Requires real Windows APIs and Electron on Windows; no startup validation performed."
        save_json(output / "report.json", report)
        print("SKIP: " + report["reason"])
        return 0
    try:
        import websocket  # noqa: F401; fail before launching if CI dependency is absent
        version = args.version or json.loads((ROOT / "desktop/package.json").read_text(encoding="utf-8"))["version"]
        report["expectedVersion"] = version
        archive = args.archive.resolve()
        if archive.is_dir():
            files = [p for p in archive.iterdir() if p.is_file() and p.suffix.lower() == ".zip"]
            if len(files) != 1:
                raise ValueError("--archive directory must contain exactly one ZIP: " + str(files))
            archive = files[0]
        extracted = output / ("中文 解压 path " + uuid.uuid4().hex[:8])
        extracted.mkdir()
        with zipfile.ZipFile(archive) as package:
            for item in package.infolist():
                target = (extracted / item.filename).resolve()
                if not target.is_relative_to(extracted) or "\\" in item.filename:
                    raise ValueError("Unsafe ZIP member: " + item.filename)
            package.extractall(extracted)
        outer, inner = extracted / "JingWeiZhiTu.exe", extracted / "JingWeiZhiTu/JingWeiZhiTu.exe"
        for path in (outer, inner, inner.parent / "resources/app.asar"):
            if not path.is_file():
                raise FileNotFoundError(path)
        report["extracted"] = str(extracted)
        native = Win32()

        def check(name, fn, diagnostic=False):
            dest = output / name
            dest.mkdir(parents=True, exist_ok=True)
            item = {"name": name, "diagnosticOnly": diagnostic}
            prefix = "DIAGNOSTIC " if diagnostic else ""
            started = time.monotonic()
            try:
                item["result"] = fn(dest)
                item["status"] = "passed"
                print(prefix + "PASS " + name, flush=True)
            except Exception as exc:
                item.update(status="failed", error=error_info(exc))
                save_json(dest / "failure.json", item["error"])
                print(prefix + "FAIL " + name + ": " + str(exc), flush=True)
            item["seconds"] = round(time.monotonic() - started, 2)
            report["diagnostics" if diagnostic else "tests"].append(item)
            save_json(output / "report.json", report)
            return item

        inner_result = None
        for label, exe in (("outer", outer), ("inner", inner)):
            check(label + "-manifest", lambda dest, exe=exe: native.manifests(exe, dest))
            check(label + "-node", lambda dest, exe=exe: node_probe(native, dest, exe))
            result = check(label + "-app", lambda dest, exe=exe: app_probe(native, dest, exe, version))
            if label == "inner":
                inner_result = result
        if inner_result["status"] == "failed":
            # Diagnostic successes never replace either unmodified app launch.
            # Each app_probe gets its own directory, profile, port, logs and the
            # exact same visibility/IPC/catalog/DOM assertions as normal startup.
            matrix = [
                ("no-software-rasterizer", ["--disable-gpu", "--disable-software-rasterizer"]),
                ("no-gpu-sandbox", ["--disable-gpu", "--disable-gpu-sandbox"]),
                ("in-process-gpu", ["--disable-gpu", "--in-process-gpu"]),
                ("no-sandbox", ["--disable-gpu", "--no-sandbox"]),
            ]
            for name, flags in matrix:
                check("diagnostic-inner-" + name,
                      lambda dest, flags=flags: app_probe(native, dest, inner, version, extra_args=flags),
                      diagnostic=True)
        if args.original_exe is not None:
            def original_control(dest):
                source = args.original_exe.resolve()
                if source.is_dir():
                    candidates = [p for p in source.iterdir() if p.is_file() and p.suffix.lower() == ".exe"]
                    if len(candidates) != 1:
                        raise ValueError("--original-exe directory must contain exactly one EXE: " + str(candidates))
                    source = candidates[0]
                if not source.is_file():
                    raise FileNotFoundError(source)
                target = inner.with_name("electron-original.exe")
                if target.exists():
                    raise FileExistsError("Refusing to overwrite extracted original-control path: " + str(target))
                shutil.copy2(source, target)
                save_json(dest / "original-control.json", {
                    "source": str(source), "copiedTo": str(target),
                    "runtimeDirectory": str(inner.parent), "extraArgs": [],
                    "diagnosticOnly": True, "normalExecutablesUnchanged": True})
                # Resources and DLLs stay in the same directory as the packaged
                # inner EXE. The pristine EXE alone is the changed variable.
                return app_probe(native, dest, target, version)
            check("diagnostic-original-electron-app", original_control, diagnostic=True)
        check("missing-asar", lambda dest: missing_asar_probe(native, dest, outer))
        # Only mandatory tests determine success. In particular, a successful
        # --no-sandbox control cannot conceal a failing normal Windows launch.
        report["status"] = "passed" if all(t["status"] == "passed" for t in report["tests"]) else "failed"
    except Exception as exc:
        report.update(status="failed", error=error_info(exc))
        print("FAIL setup: " + str(exc), flush=True)
    save_json(output / "report.json", report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
