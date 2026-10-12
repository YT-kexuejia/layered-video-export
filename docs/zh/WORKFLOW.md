# 从口播到成片

用户把仓库交给具有文件、终端及浏览器访问能力的 Agent，然后说：

> 阅读 SKILL.md，用自带模板给这个口播视频配解说画面和后期，先给网页预览和 SRT，确认后通过网页导出。

Agent 先按 [MODULES.md](MODULES.md) 建立模块交接，再执行下面的命令。`pipeline.py` 是编排入口，现有模板、3D 组件与分层渲染器是稳定执行层；不要为了模块化重写已通过视觉验收的渲染代码。

首次需要安装 Python 3.13+、Node 22+、Chrome、FFmpeg/ffprobe，以及 `npm install`、`python -m pip install -r requirements.txt`。当前硬件编码路径要求 NVIDIA NVENC 和 Chrome AVC WebCodecs；不保证任意电脑无需配置即可运行。Agent 应检查环境、完成配置，并解释实际缺少的条件。语音识别模型首次下载需要联网；通常后续可本地运行。

```sh
python pipeline.py init "/path/to/narration.mp4" --project local/my-video
python pipeline.py transcribe --project local/my-video --language zh
# Agent 阅读 transcript.json/txt，按 PLAN.md 生成 plan.json
python pipeline.py build --project local/my-video --font "/path/to/SourceHanSansSC-Bold.otf"
```

`init` 支持 `--node --ffmpeg --ffprobe --chrome` 显式工具路径。1080p 源视频不复制；其他尺寸先保留完整画面等比缩放加边。`transcribe` 默认 CPU int8 的 small 模型，可设置 `--model` 为本地模型目录或更大模型，`--device cuda` 需匹配 CUDA/cuDNN。字幕按词的实际时码切分，去标点，长句拆分；Agent 必须校对误识别。生成项目保持原始时长。

预览服务读取 `LVE_CONFIG` 环境变量：

```powershell
$env:LVE_CONFIG=(Resolve-Path local/my-video/config.json).Path
python serve.py
```

默认打开 `http://127.0.0.1:4920/`。网页提供播放、进度拖动、倍速、章节跳转、SRT 下载、开始/继续/暂停导出及 MP4 下载。`config.json` 位于生成项目，不提交 Git。需要关闭 Agent 释放内存时，应从独立终端启动服务；如果服务作为 Agent 的子进程启动，不能承诺关闭 Agent 后仍运行。后续重新启动同一配置可恢复已有导出。

交付预览前必须做两轮画面检查：逐场景检查稳定帧，再检查每个转场前、中、后的帧。背景需要连续覆盖完整 1920×1080 画布；出现竖向或横向黑带、透明缝隙、一像素边线、背景断层、上一场景残留或模块硬切时，先修复再交付。可对可疑时点比较 `t-0.1s`、`t`、`t+0.1s`，并用短导出复核相同时间点，避免只在浏览器预览中看起来正常。

命令行导出也使用同一引擎：

```sh
python export_video.py --job=my-video
```

每五分钟验证一个1080p24片段并删除该段临时图片和图层；最终拼接并加入原声。短测可用 `--duration=30 --segment-frames=240`。输出状态记录整体 `renderFps`、阶段、段落数量和最终路径。并发数不是越高越好，当前管线避免逐帧解码整段人物视频，优先减少重复工作。

自带模板未包含字体二进制、品牌图标、界面截图或音乐。可使用本机字体；分发字体和其他素材时需要对应许可与来源记录。用户视频与测试数据不会随项目发布。
