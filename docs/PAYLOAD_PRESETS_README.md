# 平台载荷绘图预设

`app/payload_presets.js` 是经典脚本数据模块，放在图标元数据和 `app.js` 之后、`payloads.js` 之前加载。`PayloadPresets.forNode(node)` 返回独立的可选条目副本；`profileFor(node)` 返回分类，`previewProfiles` 提供八类预览入口。支持 `lib:key`、节点对象或图标元数据对象。

界面统一标注“常用绘图预设，可调整”。模块均为可选示意，不代表具体型号实装；距离仅是图面单位，不能当作实际射程。`originCountry` 只保留来源信息，不参与能力分类，更不代表阵营、性能或装机能力认证。用户仍可添加任意自定义载荷，预设不能作为兼容性限制。

条目使用稳定且相同的 `id`／`presetId`／`presetKey`，例如 `destroyer:secondary-port` 和 `destroyer:secondary-starboard` 表示两个独立副炮模块。默认 `enabled:false`，选择平台不会自动开启全部模块。界面应按这些键保存编辑后的对象；关闭只改变 `enabled`，重新开启使用已保存值，不能以新返回的默认值覆盖。自定义条目由界面独立保存，不受平台模板替换影响。

`kind`／`type` 为相同类型标识；`range` 为正图面单位，`sweep` 为开角，`direction` 为世界北向零度、顺时针角度。`mount` 相对平台中心归一化，右／下为正；渲染乘以平台宽高后随平台旋转。光电、电子侦察、磁探、被动声呐默认虚线；主动模块默认实线。每项均标记 `modelStatus:'illustrative-configuration'`。

检查：`node tests/payload_presets_test.cjs`，使用实际图标元数据覆盖全部键、八类预览、具名无人机与僚机、双副炮稳定标识、完整可选模块和国别无关匹配。
