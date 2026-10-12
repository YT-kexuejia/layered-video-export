# Layered Video Export

**面向网页解说视频的分层快速导出程序。** 将动态背景 / 3D、网页图文和人物原视频分开处理，再合成 1080p、24 fps 成片。

它减少的是重复截图和逐帧视频定位的工作，不是降低分辨率。适合有长时间静止图文、持续动态背景和人物画中画的讲解视频。

> 当前版本是一个有明确适配约束的参考实现，不是任意网页的一键导出器。Windows + NVIDIA GPU 为已支持目标环境。详见 [适配协议](ADAPTER.md)。

## 工作方式

| 画面部分 | 处理方式 |
| --- | --- |
| 动态背景与 Canvas / Three.js | 按时间生成，通过 WebCodecs 编码为 H.264，分批写盘 |
| 文字、图表、网页 UI | 只在变化区间截透明 PNG，静止区间复用图片 |
| 小型动态波形 | ManimGX 生成透明图层 |
| 人物原视频 | FFmpeg 连续读取、裁切与叠加 |
| 最终合成 | NVIDIA NVENC，保留原声，生成 MP4 和 SRT |

## 存储规则

- 每段最多 **7200 帧，即 5 分钟**；最后一段处理剩余帧。
- 合成成功后检查分辨率、帧率及帧数。
- 先保存视频段及 manifest，再删除该段图片和临时图层。
- 暂停保留当前段图片、已完成图层和已合成视频段。
- 继续时复用已有 PNG 和完成图层。当前段未完成的 GPU 流需要重新生成。
- 磁盘剩余不足 1GB 时停止，已有素材保留。
- 最后拼接视频流并加入原声，视频不再次编码。

## 环境

- Windows，NVIDIA GPU 和可用的 NVENC 驱动。
- Python 3.13+，Node.js 22+，Google Chrome。
- FFmpeg / ffprobe。FFmpeg 需要包含 `h264_nvenc`、libass 字幕滤镜和 qtrle。
- 本机字体：自行配置 `fontDir` 和 `subtitleFont`，仓库不打包字体。

## 快速开始

在仓库目录运行 PowerShell：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm install
Copy-Item config.example.json config.json
```

将 FFmpeg / ffprobe / Node 加入 PATH，或在 `config.json` 中填写工具路径。Chrome 可自动检测，也可以指定 `chrome`。

```powershell
.\.venv\Scripts\python.exe doctor.py
.\.venv\Scripts\python.exe generate_example.py
.\.venv\Scripts\python.exe export_video.py --job=demo
```

`generate_example.py` **在本机生成** 12 秒测试图案和提示音，不包含真实人物、原视频或任何已测试数据，也不会覆盖已有输入。最小示例用于验证导出链路，不用于展示完整视觉设计能力。

再次运行相同命令可继续未完成任务。使用新 `--job` 建立新任务。

## 网页按钮

```powershell
.\.venv\Scripts\python.exe serve.py
```

打开 `http://127.0.0.1:4920/`，点击 Export / Continue export；暂停按钮保留素材。服务只绑定本机回环地址。服务进程需保持运行；若希望关闭终端后继续，可用虚拟环境的 `pythonw.exe serve.py` 在后台启动。不要将该接口暴露到公网。

## 接入自己的作品

配置项目目录、原视频、字体和输出目录，再按 [ADAPTER.md](ADAPTER.md) 提供时间定位 API 和 DOM 图层。当前人物布局及片头缩放使用参考几何，其他布局需要改适配器。

```powershell
$env:LVE_CONFIG = 'D:\my-project\config.json'
.\.venv\Scripts\python.exe doctor.py
.\.venv\Scripts\python.exe export_video.py --job=my-video
```

## 查看进度与结果

输出目录默认是 `local/exports/`：

```text
<job>.json                 当前阶段、总进度、整体平均 fps
<job>.frames/work-*/ui/    尚未合成的透明图文 PNG
<job>.frames/segments/    已验证的视频段
<job>.mp4                  最终成片
<job>.srt                  字幕
```

整体平均 fps 在完成视频段后按真实耗时计算；背景层 fps、波形 fps 和成片整体速度不能混为一谈。实际速度取决于显卡、内存、画面复杂度和磁盘，不承诺固定倍数。

## 项目范围

包含程序源码、配置示例、最小示例页面、本地仪表盘、AI 使用说明和 MIT 许可证。

**不包含**：人物照片、原视频、音频、个人字幕或文稿、截图、测试结果、性能日志、缓存、已导出文件、账号信息、本机配置、依赖二进制或原项目历史。

提供给其他 AI 时，让它先阅读 [AI_GUIDE.md](AI_GUIDE.md)，再调用程序。单靠提示词不能替代实际渲染代码。

## 致谢

基于 Chrome WebCodecs、FFmpeg、Puppeteer、esbuild 和 [ManimGX](https://github.com/academa-labs/manimgx)；Canvas / [Three.js](https://threejs.org/) 可作为背景和 3D 图层。受到网页视频框架按时间渲染的工作方式启发。第三方依赖各自适用其许可证，本仓库不打包其源码或二进制。

## License

自有源码采用 [MIT License](LICENSE)。输入视频、字体和项目素材的使用权由使用者负责。
