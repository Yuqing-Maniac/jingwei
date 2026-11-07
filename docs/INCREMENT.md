# 增量升级包

桌面版标题栏「增量升级」选择一个 zip。程序按标记覆盖应用目录里的约定文件，完成后提示重启。网页版没有这一入口。

zip 根目录有 `jingwei-patch.json`：

```json
{
  "format": "jingwei-patch",
  "version": 1,
  "from": "3.3.14",
  "to": "3.3.15",
  "files": ["resources/app.asar"]
}
```

`files` 是相对应用目录的路径（Windows 绿色版、安装目录，或麒麟免安装目录、`/opt/jingwei-zhitu`）。路径不能以盘符或 `/` 开头，也不能含 `..`。列出的每个路径都要在 zip 里有同名文件。未列出的文件不会被改。

3.3.15 的增量包只带 `resources/app.asar`（界面与主进程）。Electron 运行时不在包里。基线是 3.3.14。
