# Talking Head Studio / 口播视频自动包装

**简体中文** · [English](README.en.md) · [Español](README.es.md)

把一个口播视频交给现有 Agent，自动完成本地转写、内容理解、解说画面编排、3D 动效、字幕、网页预览和分层加速导出。项目自带 **Studio Blue** 模板，也支持安装新的兼容模板。

![网页预览与导出界面](docs/images/web-interface.jpg)

![Studio Blue 模板效果](docs/images/studio-blue-template.png)

预览中的人物是虚构演示形象，仓库不包含用户肖像、测试视频或历史导出数据。

## 这是怎么工作的

现有 Agent 负责理解整段口播、决定每个画面表达什么并完成视觉复核；本地程序负责转写、构建、预览和渲染。项目本身不要求额外配置 AI API Key，也不会在后台启动隐藏的 AI 服务。

工作流分成九个有明确交接文件的模块：素材接入、语音转写、内容编排、视觉设计、动效代码、3D、字幕音频、分层渲染、独立复核。详见 [模块说明](docs/zh/MODULES.md)，机器可读注册表位于 [config/workflow.modules.json](config/workflow.modules.json)。模块化不会改变已经确认的模板版式、动画节奏、字幕规则或 1080p24 导出基准。

## 用 Agent 开始制作

```sh
git clone https://github.com/YT-kexuejia/layered-video-export.git
cd layered-video-export
npm install
python -m pip install -r requirements.txt
```

把仓库目录和口播视频交给支持文件与命令操作的 Agent，然后直接发送：

> 阅读 SKILL.md，用自带模板给这个口播视频完成后期包装。先生成网页预览和 SRT；检查口播与画面时码、人物裁切、转场和黑边，确认后再导出 1080p24 成片。

Agent 会按 [SKILL.md](SKILL.md) 执行完整流程。常用命令：

```sh
python pipeline.py init "D:\path\talking-head.mp4" --project "D:\path\my-video"
python pipeline.py transcribe --project "D:\path\my-video" --device cpu
# Agent 阅读 transcript 并写好 plan.json 后：
python pipeline.py build --project "D:\path\my-video"
set LVE_CONFIG=D:\path\my-video\config.json
python serve.py
```

打开终端显示的本地地址即可预览、拖动、跳章节、下载 SRT，以及开始、继续或暂停导出。完整步骤见 [工作流文档](docs/zh/WORKFLOW.md)，画面计划格式见 [编排规范](docs/zh/PLAN.md)。

## 自带模板与扩展模板

自带模板位于 [`templates/studio-blue`](templates/studio-blue)，包括蓝色连续光带、信息排版、人物侧栏、章节配色、金属球体，以及服务器、装配层、镜头轨道、天平等 3D 场景。模板按口播实际时码揭示信息；字幕去除句号、逗号等标点，以空格分句并限制单句长度。

后续模板可以作为独立 Git 仓库或下载包分发。只要包含兼容的 `template.json`，即可使用：

```sh
python pipeline.py build --project "D:\path\my-video" --template "D:\path\downloaded-template"
```

模板接口与授权要求见 [模板文档](docs/zh/TEMPLATES.md)。自带动效使用 MIT 许可的 Anime.js，3D 使用 MIT 许可的 Three.js；光带和模板视觉由本项目实现。字体文件、用户素材和第三方图片不会随仓库分发。

## 分层加速导出

| 图层 | 处理方式 |
| --- | --- |
| 背景与 3D | 确定性时间驱动，连续编码 |
| 图文 UI | 仅截取变化区间，静止区间复用 |
| 波形 | ManimGX 生成小型透明图层 |
| 人物视频 | FFmpeg 连续解码、裁切与合成 |
| 成片 | NVIDIA NVENC 编码分段，最后无损拼接并加入原声 |

默认每 7200 帧，即五分钟，完成一个段落。程序先验证段落，再删除该段图片与临时图层；中断时保留未完成素材和已完成段落，下次点击继续即可复用。网页显示的是整体实测帧率。

## 目录结构

```text
├─ README.md / README.en.md / README.es.md   三语入口文档
├─ SKILL.md / AGENTS.md                      Agent 入口
├─ pipeline.py / serve.py / export_video.py  用户命令
├─ src/python/                               Python 内部模块
├─ src/js/                                   JavaScript 渲染模块
├─ templates/studio-blue/                    自带模板
├─ web/                                      本地网页控制台
├─ examples/basic/                           合成示例与配置样例
├─ config/                                   工作流机器配置
└─ docs/                                     设计、工作流和授权文档
```

## 环境与许可

当前经过验证的目标环境是 Windows、Python 3.13+、Node 22+、Chrome、FFmpeg/ffprobe、NVIDIA NVENC 和 Chrome AVC WebCodecs。首次安装依赖、下载转写模型需要联网。CPU 可执行转写；CUDA 环境可加速转写。

本项目自有代码和自带模板采用 MIT 许可。依赖继续遵守各自许可；本仓库不打包 FFmpeg、ManimGX 原生 wheel、字体或用户素材。详见 [第三方说明](docs/legal/THIRD-PARTY-NOTICES.md) 和 [许可审计](docs/legal/LICENSE-AUDIT.md)。
