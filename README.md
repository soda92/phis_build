# phis_build

宇信自动打包程序

## 使用方法

第一次运行会创建phis_build.toml，在其中修改名称和目标复制路径

共享目录用斜杠代替反斜杠

名称是Python文件的名称

然后运行

`phis_build --no-zip` 会自动构建并复制到共享目录

`phis_build --no-copy` 会自动构建并打压缩包，适合微信发送
