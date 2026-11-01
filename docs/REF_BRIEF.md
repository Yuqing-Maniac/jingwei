# v2.5 brief — shared context (参照生成 + 信息系统视图)

App: 「鸿图体系绘图」, single-file offline HTML diagram editor in /home/claude/drawtool. Build: `python3 build.py` → offline.html (all libs inlined; JSZip, pptxgenjs, milsymbol are globals). Tests: `python3 test.py` must print `ERR []`. Work autonomously; never ask questions. Backup of the current state: /home/claude/drawtool_v24_backup (do not touch).

Model (globals in app.js): `doc = {name, theme, statusLabels, custom:{id:{name,uri,aspect?}}, meta, showCodes, pages:{id:{id,name,nodes,links,view,cam}}}`; `mkNode(o)` → `{id,type,x,y,w,h,text,status:'base'|'new'|'key',parent,size,bold,align,icon,noBox,sub, fill?, stroke?}`; node types: band (wide horizontal layer with title strip on the left), lane (row inside a band), group (titled container), rect + 30 shapes (ellipse, diamond, cylinder, cloud, hexagon, document, …see GEO in app.js), equip (icon card; icon = 'lib:<key>' or 'cu:<customId>'), text, note, legend, tblock. Containment = `parent` id. Links: `{id, from, to, dir:'one'|'both'|'none', kind:'plain'|'data'|'ctrl'|'wired'|'radio'|'sat', route:'ortho', label, code?, attrs?}`. `uid()`, `beautify(page)`, `render()`, `fit()`, `loadDoc(d)`, `P()` current page, `diagramSVG(...)` export.

Files owned by each worker (edit ONLY your own; the lead edits app.js, app_body.html, textgen.js, build.py, refgen.js):
- importers worker: importers.js (new) + your test scripts under /home/claude/drawtool/imp_test/
- IT-icon worker: icons_gen_k.py, icons_k.js (+ icon_sheet_k*.png)
- IT-views worker: standards.js, std_templates.js, xlsxexport.js, STD_SPEC.md

build.py will include importers.js and refgen.js after textgen.js (lead adds this; until then you can test by injecting your file into a page that loaded offline.html).

## Planned IT icon keys (category 「信息技术」) — the views worker may reference these with the `ic(key, fallbackKey)` helper; fall back to existing keys (server, database, data_center, cloud, firewall, gateway, switch, router, storage, app, api, message_bus, data_lake, security, identity, audit_log, crypto, ops_monitor, edge_node, gpu, laptop, user_group, workflow, document)
it_k8s 容器集群 · it_container 容器 · it_vm 虚拟机 · it_xc_server 信创服务器 · it_rack 服务器机柜 · it_lb 负载均衡 · it_core_switch 核心交换机 · it_gap 网闸（隔离装置） · it_bastion 堡垒机 · it_ids 入侵检测 · it_vpn VPN 网关 · it_waf Web 应用防火墙 · it_ca CA 证书 · it_mq 消息队列 · it_cache 缓存 · it_middleware 应用中间件 · it_microservice 微服务 · it_registry 镜像仓库 · it_cicd 持续集成 · it_os 国产操作系统 · it_web 门户网站 · it_mobile 移动应用 · it_object_store 对象存储 · it_dw 数据仓库 · it_lakehouse 湖仓一体 · it_etl 数据集成 · it_stream 流计算 · it_batch 批处理 · it_tsdb 时序数据库 · it_graphdb 图数据库 · it_search 搜索引擎 · it_file_server 文件服务器 · it_backup 备份 · it_dr 灾备中心 · it_metadata 数据目录 · it_master_data 主数据 · it_data_service 数据服务 · it_business_obj 业务对象
