# 展示媒体

这里放5张说明图和2段GIF，帮助了解最终V20画面、系统AOD调度、透明裁图优化和探索历程。

|文件|内容|来源与边界|
|---|---|---|
|hero.png|V20封面|私人V20成品资源本地渲染；示意屏幕边缘，不是产品实拍|
|bright-demo.gif|完整亮屏剧情|18.64秒预览，12.5fps编码；含年轻瑞克、白闪、老瑞克喝酒|
|aod-demo.gif|息屏动画与末帧保持|按40ms目标时序；末帧保持与示例分钟变化，共6.32秒|
|storyboard.png|四阶段画面|完整剧情到AOD末帧的成品预览|
|architecture.png|两条更新链|根据本项目源码与局部分析绘制的原创说明图|
|crop-optimization.png|无损裁图|成品AOD预览和实际文件测量数字；不代表功耗或面板FPS|
|milestones.png|版本历程|根据探索记录和用户反馈绘制的原创说明图|

GIF循环用于网页观看。每轮表示一次进入AOD的动画播放，不代表设备会在息屏中无限循环。时间、日期、步数、心率、天气等为示例值，分钟变化为加速示例。媒体不是实机录屏，不能作为公开加固版的硬件验证证据。

原创架构图与历程图随本项目MIT许可。包含第三方角色、动画画面或字体图像的成品预览不属于MIT代码许可；第三方权利归其相应权利人。仓库不提供角色原始素材、字体文件、私人BIN或原固件，也不赋予这些材料的再分发许可。

## 排版方向

以纸白、墨色和单一强调色组织信息；封面采用非对称分区，运行原理用两条时间轨，历程使用目录式分行，数据图直接标注测量值。各图用统一细线页眉和章节编号关联，避免等大卡片和装饰网格。

设计原则参考 [Pentagram 的 MIT Technology Review](https://www.pentagram.com/work/mit-technology-review)、[Aron Fay 的数字与标题设计](https://fay.design/work/mit-technology-review/)及 [teenage engineering 的 OP-1 功能说明](https://teenage.engineering/guides/op-1/original/layout)。只参考分栏、字级和标注方法，没有复制作品图片、品牌标志或专用字体。
