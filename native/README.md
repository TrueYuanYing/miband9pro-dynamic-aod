# 原生模块源码

`module.c`、`entry.S`、`blob.ld` 为本项目 RAM 模块源码；`target.json` 保存精确 n67cn 3.1.175 指纹和既有模块符号。实际打包默认使用 `runtime/loader.lua` 内的既有编译模块，SHA256为 `fe8b72fb3faf1ba306a6caf9d74fe10e89d078c7349e20eec654110546e81c4e`。

源码的 native timer、heap、screen callback 和 cache 地址只属于这个目标。若重新编译，编译器选项可能改变指令布局、符号偏移和SHA；必须检查0字节入口、参数偏移4、所有未定义符号和重定位，再更新对应模板并重新执行测试。不要把重新编译产物当作已经实机验证的原模块。本仓库当前没有把新编译产物自动嵌入或自动推送设备的流程。

`tests/test_native_optional.py` 在使用者自行提供精确AP时执行实际Thumb指令；AP不属于仓库，缺失时跳过。测试的系统调用、面板、MPU总线和缓存使用显式替身，不能取代实机验证。
