# 通用体系结构规范包 · 数据约定（所有模块共用）

Goal: diagrams follow architecture-framework conventions, with typed elements, numbering, required attributes, a rule checker, a title block, and model-derived tables (接口清单、信息交换矩阵、元素清单、部署清单、数据流清单). Two view families:
- `dodaf` — DoDAF 2.02 / UAF / NAF v4 viewpoints (OV-1, OV-2, OV-5b, SV-1, SV-4);
- `it` — 信息系统架构 (TOGAF / 4A, as used in Chinese 信息系统总体设计 documents): BIZ 业务、APP 应用、DATA 数据、TECH 技术 + DEPLOY 部署、SEC 安全.

## Document / page fields
- `page.view`: one of `'OV-1' | 'OV-2' | 'OV-5b' | 'SV-1' | 'SV-4' | 'BIZ' | 'APP' | 'DATA' | 'TECH' | 'DEPLOY' | 'SEC'` or absent (free drawing).
- `doc.meta` (title-block data, document level): `{ project, drawingNo, version, classification, author, reviewer, approver, date, org }` — all strings, any may be empty. `classification` (密级) e.g. 公开／内部／秘密. Page-level drawing number = `${drawingNo}-${pageIndex+1}` when several pages.
- `doc.showCodes`: boolean — show element/link codes on the canvas and in exports.

## View definitions (window.Std.VIEWS)
Each view: `{ family: 'dodaf'|'it', name, etypes, link, linkName, hint? }`. `Std.FAMILIES` = `[['dodaf','DoDAF／UAF 体系结构视图'],['it','信息系统架构（TOGAF／4A）']]` (the view selector groups by it with `<optgroup>`). `Std.viewLabel(v)`: DoDAF → `OV-1　高层作战概念图`, IT → `部署架构图` (the code is not shown for IT views — title block, check dialog and xlsx use the name only).

| view | family | 中文名 | node etypes allowed | link code prefix | link meaning |
|---|---|---|---|---|---|
| OV-1 | dodaf | 高层作战概念图 | op_node, performer, resource | CN | 概念关联 |
| OV-2 | dodaf | 作战资源流描述 | op_node, performer | NL | 需求线（资源流） |
| OV-5b | dodaf | 作战活动模型 | op_activity, performer (as lanes) | AF | 活动流 |
| SV-1 | dodaf | 系统接口描述 | system, subsystem, op_node (as containers) | SI | 系统接口 |
| SV-4 | dodaf | 系统功能描述 | sys_function, system (as containers) | FF | 功能数据流 |
| BIZ | it | 业务架构图 | biz_domain, biz_capability, biz_process, biz_role, biz_object | BF | 业务流 |
| APP | it | 应用架构图 | app_system, app_module, app_service, ext_system | AI | 应用集成 |
| DATA | it | 数据架构图 | data_domain, data_entity, data_store, data_proc | DF | 数据流 |
| TECH | it | 技术架构图 | tech_layer, platform, tech_component, infra | TD | 技术依赖 |
| DEPLOY | it | 部署架构图 | zone, deploy_node, deploy_unit, net_device | NC | 网络连接 |
| SEC | it | 安全架构图 | sec_domain, sec_control, protected_asset, sec_boundary | AC | 访问控制关系 |

## Element types (window.Std.ETYPES) — `node.etype`
| etype | 中文 | code prefix |
|---|---|---|
| op_node | 作战节点 | ON |
| performer | 执行者 | PF |
| op_activity | 作战活动 | OA |
| resource | 装备／资源 | RS |
| system | 系统 | SY |
| subsystem | 子系统 | SS |
| sys_function | 系统功能 | SF |
| biz_domain / biz_capability / biz_process / biz_role / biz_object | 业务域／业务能力／业务流程／活动／业务角色／业务对象 | BD / BC / BP / BR / BO |
| app_system / app_module / app_service / ext_system | 应用系统／应用模块／应用服务／外部系统 | AP / AM / AS / EX |
| data_domain / data_entity / data_store / data_proc | 数据域／数据实体／主题／数据存储／数据处理 | DD / DE / DS / DP |
| tech_layer / platform / tech_component / infra | 技术层／平台／中间件／技术组件／基础设施 | TL / PL / TC / IN |
| zone / deploy_node / deploy_unit / net_device | 网络区域／安全域／部署节点（服务器、虚拟机、容器集群）／部署单元（应用实例）／网络／边界设备 | ZN / DN / DU / NW |
| sec_domain / sec_control / protected_asset / sec_boundary | 安全域／安全措施／保护对象／边界防护设备 | SD / SC / PA / SB |
Containers (band/lane/group) may also carry an etype (e.g. a lane = performer in OV-5b, a group = system in SV-4, a band = zone in DEPLOY).

### Default type inference for IT views (`Std.defaultEtype`, used by 自动编号 / 一键修复)
Uses container nesting (explicit or inferred type of ancestors), icon key (`lib:<key>`), shape and name cues:
- BIZ: band → biz_domain; lane/group → biz_capability inside a domain, else biz_domain; person icons → biz_role; document/cylinder shapes or `document`/`it_business_obj` icons → biz_object; other leaves → biz_process.
- APP: bands/lanes are layout only (no type); a group named “外部…” outside an app_system is layout only and its content → ext_system; group → app_system (app_module inside an app_system); leaves → app_service inside an app_module or inside a band/lane named “支撑／服务／中台／公共”, app_module inside an app_system, else app_system.
- DATA: band/lane whose name ends with “层” (采集层、存储层…) is layout only; band → data_domain; group → data_domain at top level, inside a domain → data_store if named 库／仓／湖／存储 else data_entity; leaves: storage icons (database, it_dw, it_tsdb, it_object_store …), cylinder, or names like 数据库／ODS／DW → data_store; integration/compute icons (it_etl, it_stream, it_batch, it_data_service, workflow, it_mq …) or names like 采集／清洗／治理／计算 → data_proc; else data_entity.
- TECH: band/lane → tech_layer; group → platform inside a layer, else tech_layer; server/storage/network icons → infra; middleware icons (it_middleware, it_mq, it_cache, it_k8s …) → platform; else tech_component.
- DEPLOY: band → zone; lane inside a zone is layout only (排版行); group → zone at top level or when named 区／域／DMZ, deploy_node otherwise; leaves with network/security icons (firewall, gateway, it_gap, it_lb, switch, router, it_core_switch, it_vpn, it_waf, it_bastion, it_ids) or names (防火墙、网闸、交换机…) → net_device; inside a deploy_node → deploy_unit; else deploy_node.
- SEC: band → sec_domain; lane inside a domain is layout only; group → sec_domain (top level or named 域／区) else protected_asset; boundary icons/names (firewall, gateway, it_gap, it_vpn, it_waf, it_ids) → sec_boundary; control icons/names (security, identity, audit_log, crypto, it_ca, it_backup, it_bastion, ops_monitor; 审计、认证、加密…) → sec_control; else protected_asset.

## Node fields
- `node.etype` (above), `node.code` e.g. `SY-03`, `node.attrs = { desc, owner }` (说明、责任单位).
- Extra attrs by etype (`Std.NODE_EXTRA`, shown in the properties panel only for these types): deploy_node → `spec` 规格（CPU／内存／存储）, `os` 操作系统, `ip` 地址／网段, `count` 数量; deploy_unit / net_device → spec, ip, count; sec_boundary → spec, count; zone / sec_domain → `level` 安全等级 (e.g. 等保三级、涉密秘密级; input with suggestions `Std.LEVELS`).

## Link fields
- `link.code` e.g. `SI-07`, `link.attrs = { content, protocol, medium, freq, latency, security }`
  - content 交换内容／信息元素, protocol 协议／接口标准, medium 链路／介质, freq 频度, latency 时延要求, security 密级.
  - additional key `port` 端口 (DEPLOY).
- Per-view field sets (`Std.VIEW_LINK_ATTRS`, `Std.linkAttrsOf(v)`; DoDAF views and free drawing keep the five fields above; 密级 always shown):
  - BIZ: content 业务对象, freq 频度／触发
  - APP: content 集成内容, protocol 集成方式／协议, freq, latency
  - DATA: content 数据对象, protocol 交换方式, freq 频度／时效
  - TECH: content 依赖说明, protocol 接口／协议
  - DEPLOY: protocol 协议, port 端口, medium 链路／带宽
  - SEC: content 访问策略, protocol 协议／端口, medium 链路／介质
- Existing fields stay: from, to, dir ('one'|'both'|'none'), kind, label, route.
- `kind` is `plain` 关联, `data` 数据流, `ctrl` 指令流, `wired` 有线／光纤, `radio` 无线／数据链, `sat` 卫通链路, `alarm` 告警, or `sync` 时统.

## Title block node
- `node.type === 'tblock'` (one per page, top-level, ~ 520×120). Rendering cells come from `Std.tblockCells(node, page)` → `[{x,y,w,h,text,size,bold,fill,align}]` (absolute coords). Data from doc.meta + page.name + page.view.

## Numbering rule (Std.autoNumber(page))
Codes are `${prefix}-${NN}` with two-digit NN in reading order (top-to-bottom, left-to-right by node centre; links ordered by source then target position). Existing codes are kept unless `renumber=true`.

## Rule checker (Std.check → [{level:'error'|'warn'|'info', rule, msg, pageId, nodeId?|linkId?}], every issue has 定位)
Generic (all views): etype-missing, etype-view, code-missing, code-dup, name-empty, link-code, legend-missing, tblock-missing; link-content (DoDAF, BIZ, APP — not required for TECH/DEPLOY/SEC); isolated (OV-2, SV-1, SV-4); sv1-iface; ov5b-lane.
信息系统架构:
| rule | 中文 | level |
|---|---|---|
| biz-scope | 业务流程不在业务域／能力内 | warn |
| app-proto | 集成未写方式／协议 | warn |
| app-isolated | 应用无集成关系（app_system / ext_system with no link on itself or its contents） | warn |
| data-content | 数据流未写数据对象（replaces link-content on DATA; info when only a label is written） | warn |
| data-domain | 数据实体不在数据域内 | warn |
| tech-layer | 技术组件不在技术层内 | warn |
| dep-zone | 部署节点不在网络区域内 | error |
| dep-node | 部署单元不在部署节点内 | warn |
| dep-cross | 跨区直连未经边界设备：link endpoints in different zones (nearest zone ancestor-or-self) and neither endpoint is net_device / sec_boundary | error |
| dep-level | 网络区域未标安全等级 | info |
| sec-cross | 跨域访问未经边界防护 (same rule with sec_domain) | error |
| sec-asset | 保护对象不在安全域内 | error |
| sec-level | 安全域未标安全等级 | warn |

Std.fix (一键修复), in order per page: IT views — (1) re-attach an element that lies geometrically inside a suitable container but is not its child (findParent), (2) type untyped elements, (3) copy a security level written in the zone / domain name or description (e.g. “业务专网区（等保三级）”) to `attrs.level`; then for all views: auto-number, label → content, add legend, insert/place title block. Returns `{typed, nodes, links, content, legend, tblock, parent, level}`.

## Canvas
- Band code tag: inside the band at top-left; when the band contains lanes or groups it straddles the band's top edge so it is not hidden by them.

## xlsx (StdXlsx.build(doc))
- 说明 (cover; view list with 视图族), 元素清单 (typed containers are included; 所属容器 = nearest typed ancestor; extra columns 安全等级／规格／操作系统／地址／网段／数量 appear only when used),
- 接口清单 — columns = the single IT view's field set, or the union with generic names when views are mixed or DoDAF; sorted by code. Sheet is renamed for a single IT view: 业务流清单／集成清单／接口清单(DATA)／依赖清单／网络连接清单／访问控制清单,
- 部署清单 (DEPLOY pages): 区域, 编号, 节点, 类型, 规格, 操作系统, 地址, 数量, 部署单元 (units with ×count; net devices included),
- 数据流清单 (DATA pages): 编号, 源, 源类型, 目标, 目标类型, 数据对象, 交换方式, 频度／时效, 源数据域, 目标数据域, 密级,
- 信息交换矩阵·<page> per page.

## Templates (std_templates.js, `template.group`)
- 「体系结构视图」: std-ov1, std-ov2, std-ov5b, std-sv1, std-sv4.
- 「信息系统架构」 (fictional 边海防无人化巡逻体系·指控信息系统; drawing numbers ZKXT-YW/YY/SJ/JS/BS/AQ-01): it-biz 业务架构图·巡逻任务全流程, it-app 应用架构图·指控信息系统, it-data 数据架构图·采集治理服务, it-tech 技术架构图·分层技术栈 (with a right-hand 安全保障体系 column), it-deploy 部署架构图·分区部署, it-sec 安全架构图·等级保护 (with a right-hand 安全管理中心 column). Each passes Std.check with 0 issues, is stable under 一键美化 (beautify), and references `it_*` icons through `ic(key, fallback)`.
