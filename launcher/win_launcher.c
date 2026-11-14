/* 压缩包顶层的 JingWeiZhiTu.exe。程序本体在旁边的 JingWeiZhiTu 文件夹里。 */
#define INITGUID
#include <windows.h>
#include <shlobj.h>
#include <shobjidl.h>
#include <objbase.h>
#include <propkey.h>
#include <stdio.h>

static const PROPERTYKEY kAumid = {
    {0x9F4C2855, 0x9F79, 0x4B39, {0xA8, 0xD0, 0xE1, 0xD4, 0x2D, 0xE1, 0xD5, 0xF3}},
    5
};

static void strip_file(wchar_t *path) {
    wchar_t *slash = wcsrchr(path, L'\\');
    if (slash) *slash = 0;
}

static const wchar_t *skip_arg0(const wchar_t *cmd) {
    if (*cmd == L'"') {
        cmd++;
        while (*cmd && *cmd != L'"') cmd++;
        if (*cmd == L'"') cmd++;
    } else {
        while (*cmd && *cmd != L' ' && *cmd != L'\t') cmd++;
    }
    while (*cmd == L' ' || *cmd == L'\t') cmd++;
    return cmd;
}

static void append_quoted(wchar_t *dst, size_t cap, const wchar_t *src) {
    size_t n = wcslen(dst);
    if (n + 3 >= cap) return;
    dst[n++] = L'"';
    while (*src && n + 3 < cap) {
        if (*src == L'"' && n + 4 < cap) dst[n++] = L'\\';
        dst[n++] = *src++;
    }
    dst[n++] = L'"';
    dst[n] = 0;
}

static void save_link(const wchar_t *dir, const wchar_t *target, const wchar_t *work) {
    wchar_t lnk[MAX_PATH];
    IShellLinkW *link = NULL;
    IPersistFile *file = NULL;
    IPropertyStore *store = NULL;
    PROPVARIANT pv;
    if (!dir || !dir[0]) return;
    CreateDirectoryW(dir, NULL);
    _snwprintf(lnk, MAX_PATH, L"%ls\\经纬织图.lnk", dir);
    lnk[MAX_PATH - 1] = 0;
    if (FAILED(CoCreateInstance(&CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, &IID_IShellLinkW, (void **)&link))) return;
    link->lpVtbl->SetPath(link, target);
    link->lpVtbl->SetWorkingDirectory(link, work);
    link->lpVtbl->SetIconLocation(link, target, 0);
    link->lpVtbl->SetDescription(link, L"经纬织图");
    if (SUCCEEDED(link->lpVtbl->QueryInterface(link, &IID_IPropertyStore, (void **)&store))) {
        memset(&pv, 0, sizeof(pv));
        pv.vt = VT_LPWSTR;
        pv.pwszVal = L"cn.ycq.jingwei-zhitu";
        store->lpVtbl->SetValue(store, &kAumid, &pv);
        store->lpVtbl->Commit(store);
        store->lpVtbl->Release(store);
    }
    if (SUCCEEDED(link->lpVtbl->QueryInterface(link, &IID_IPersistFile, (void **)&file))) {
        file->lpVtbl->Save(file, lnk, TRUE);
        file->lpVtbl->Release(file);
    }
    link->lpVtbl->Release(link);
}

static void shortcuts(const wchar_t *launcher, const wchar_t *work) {
    wchar_t desktop[MAX_PATH];
    wchar_t programs[MAX_PATH];
    HRESULT hr = CoInitialize(NULL);
    desktop[0] = 0;
    programs[0] = 0;
    if (SUCCEEDED(SHGetFolderPathW(NULL, CSIDL_DESKTOPDIRECTORY, NULL, 0, desktop)))
        save_link(desktop, launcher, work);
    if (SUCCEEDED(SHGetFolderPathW(NULL, CSIDL_PROGRAMS, NULL, 0, programs)))
        save_link(programs, launcher, work);
    if (SUCCEEDED(hr)) CoUninitialize();
}

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, PWSTR cmdline, int show) {
    wchar_t self[32768];
    wchar_t app[32768];
    wchar_t args[32768];
    wchar_t work[32768];
    wchar_t appdir[32768];
    wchar_t resource[32768];
    const wchar_t *rest;
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    DWORD n;
    (void)inst; (void)prev; (void)cmdline; (void)show;
    n = GetModuleFileNameW(NULL, self, 32768);
    if (n == 0 || n >= 32767) return 1;
    wcscpy(work, self);
    strip_file(work);
    _snwprintf(app, 32768, L"%ls\\JingWeiZhiTu\\JingWeiZhiTu.exe", work);
    app[32767] = 0;
    if (GetFileAttributesW(app) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL,
            L"请把 JingWeiZhiTu.exe 和旁边的 JingWeiZhiTu 文件夹放在一起，不要只拷走这一个文件。",
            L"经纬织图", MB_OK | MB_ICONINFORMATION);
        return 1;
    }
    _snwprintf(resource, 32768, L"%ls\\JingWeiZhiTu\\resources\\app.asar", work);
    resource[32767] = 0;
    if (GetFileAttributesW(resource) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL,
            L"程序资源不完整。请将完整程序包重新解压；如果下载了两个 ZIP，请将两个包都解压到同一个文件夹，再启动。",
            L"经纬织图", MB_OK | MB_ICONERROR);
        return 2;
    }
    shortcuts(self, work);
    rest = skip_arg0(GetCommandLineW());
    args[0] = 0;
    append_quoted(args, 32768, app);
    if (rest && rest[0]) {
        if (wcslen(args) + wcslen(rest) + 2 < 32768) {
            wcscat(args, L" ");
            wcscat(args, rest);
        }
    }
    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);
    memset(&pi, 0, sizeof(pi));
    wcscpy(appdir, app);
    strip_file(appdir);
    if (!CreateProcessW(app, args, NULL, NULL, FALSE, 0, NULL, appdir, &si, &pi)) {
        DWORD error = GetLastError();
        wchar_t reason[1024] = L"";
        wchar_t message[1600];
        FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
            NULL, error, 0, reason, 1024, NULL);
        _snwprintf(message, 1600, L"无法启动经纬织图（Windows 错误 %lu）。\n%ls\n请确认程序包已完整解压。", error, reason);
        message[1599] = 0;
        MessageBoxW(NULL, message, L"经纬织图", MB_OK | MB_ICONERROR);
        return 1;
    }
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return 0;
}
