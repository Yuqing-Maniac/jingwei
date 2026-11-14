# 中美外形参考图标

306 项国别筛选任务由 `*-tasks.json` 定义，通用 656 项图标的稳定 key 保持不变。中国外形默认红色，美国外形默认蓝色，用户仍可独立选择原色、红色、蓝色。

`batches/` 记录生成图册、格位、公开来源和限制；`masters/` 保留可复建的生成素材，`icons/` 是运行时 256×256 透明 WebP。原始生成 PNG 路径仅作追溯；路径不存在时构建器使用已入库的同名 master。带 `repair` 的批次覆盖同 key/country 的原批次，不改变原始记录。

`reference-reviewed` 表示已查看公开外形来源，图标仍是艺术参考，不能视为测绘、精确结构或真实性认证。`illustrative-configuration` 表示借用公开平台/组件进行的任务示意，不能据此声称真实型号具备该载荷；具体限制见每项 notes、geometryChecks 和批次 qualityNotes。中美成对表示相同图标用途，不表示性能、代际或编制相当。

构建与预览：

```sh
node build/icons/package_country.cjs
node build/icons/country_atlas.cjs
python3 build/build_web.py --desk
python3 -m http.server 8766 --directory .
```

浏览器打开 `http://127.0.0.1:8766/assets/country-variants/`；单文件离线对照图册在 `_work/country-atlas.html`。数量、待补项与自动检查结果以 `catalog.json` 为准。自动检查只验证资产/涂装等技术问题，不替代逐图外形校对。来源照片不作为重绘图标发布。
