# 研究参考和分发范围

项目在自有设备与用户提供的原版文件副本上进行分析。仓库不分发完整原厂 AP、BL、OTA、诊断 dump、配对数据、个人路径、账号信息或用户动画素材。`runtime/loader.lua` 内的编译模块来自本项目C/Thumb源码；固件指纹、地址绑定用于拒绝错误目标，不能视为跨版本ABI。

参考入口：

- [Mi8WfBinTool](https://github.com/zhy8388608/Mi8WfBinTool)：BIN图像、索引和Lua资源结构的对照参考。
- [AstralSightStudios Canopus](https://github.com/AstralSightStudios/Canopus)：原生代码加载及特定设备适配的公开研究参考。
- [AstroBox](https://github.com/AstralSightStudios/AstroBox-NG)：安装工具和设备连接。
- [Xiaomi WatchFace 协议](https://github.com/AstralSightStudios/AstroBox-NG-Module-Pb/blob/main/protos/xiaomi/wear_watch_face.proto)：表盘资源版本及安装通信字段。
- [LVGL](https://docs.lvgl.io/)：图像、timer、invalidate等接口的参考；厂商绑定的具体行为仍需设备验证。

MIT许可仅覆盖本仓库代码。示例几何动画由本项目程序绘制。使用者自行提供有权使用的素材和基底；仓库没有赋予第三方表盘、动画、字体或固件的再分发许可。本项目不宣称由上述项目维护者支持，也没有向他们提交适配结论或咨询。
