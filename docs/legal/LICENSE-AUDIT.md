# 第三方动效与素材许可审查

审查日期：2026-10-12。此记录针对源码发布方式，不构成所有素材已经获得授权的保证。升级依赖或改变分发方式后需要重新核对。

| 项目 | 核对结果 | 本仓库发布规则 |
| --- | --- | --- |
| React Bits LightPillar / ShinyText | 当前上游为 MIT + Commons Clause，允许作为应用使用，但明确限制组件本身的再分发、打包或移植发布 | 不把个人视频工程中的这两个组件及其修改版复制进开源模板。实现独立效果，不沿用其 shader 或组件源码。历史获取版本的许可尚未固定，不能据当前名称推断旧副本是纯 MIT |
| Three.js 及其 addons | MIT | 可以依赖和修改；分发其代码时保留上游版权与完整许可。自己的场景模型不等于 Three.js 的源码 |
| GSAP | Standard No Charge License，非 MIT；包含竞争性可视化动画构建工具限制 | AI 生成代码的使用获官方 FAQ 明确允许。若保留此依赖，应按上游条款使用且不把它纳入本仓库 MIT；新增可视化动画编辑器前重新审查 |
| ManimGX 0.1.1 | 自有代码 MIT；本地安装包元数据包含 GPL、LGPL 等许可，上游说明含 x264 的原生 wheel 整体为 GPL-3.0-or-later | 通过依赖安装使用，不把 wheel、引擎二进制或第三方源码作为自有 MIT 代码重新发布。未来发布整合安装包时单独处理 GPL/LGPL 源码与通知义务 |
| FFmpeg | LGPL/GPL 取决于具体构建与启用库 | 当前调用用户安装的外部程序，不在仓库打包二进制。以后打包时必须检查实际构建，不统一标成 MIT |
| 思源黑体 Source Han Sans | SIL OFL 1.1 | 可用于视频和分发；分发字体时附完整 OFL 与版权声明，遵守保留字体名称条款，不单独销售字体 |
| 产品 Logo、官方 UI、截图、音乐、第三方图片 | 不由代码库许可证自动授权 | 不将个人项目素材默认打包为可任意复用资产。逐项记录来源、用途和许可；公开网页可访问不代表可再分发 |
| 本项目编排、分层导出代码、独立编写的布局和模型 | 可对自有代码采用 MIT，但不覆盖第三方材料 | 保留第三方依赖各自许可；发布前检查来源，避免把参考作品的具体素材和代码当作原创 |

## 核对来源

- React Bits：https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md
- Three.js：https://github.com/mrdoob/three.js/blob/dev/LICENSE
- GSAP：https://gsap.com/community/standard-license/
- ManimGX：https://github.com/academa-labs/manimgx#license 及已安装 0.1.1 的 dist-info/licenses 和 METADATA
- FFmpeg：https://ffmpeg.org/legal.html
- Source Han Sans：https://github.com/adobe-fonts/source-han-sans/blob/master/LICENSE.txt

## 当前范围

初版上传的导出引擎没有包含 React Bits 的组件源码；渲染适配器提到 LightPillar 的文件名用于分层识别，不包含其实现。个人视频工程的 React Bits 副本仍留在本地，不因本次审查而改动现有视频。扩展完整开源工作流时必须先替换受限制的组件，再发布模板源码。

开源版自带 Studio Blue 模板已采用 MIT Anime.js 替换 GSAP，并独立实现解析光带 shader 替换 React Bits。模板中的 LightPillar 文件名仅为兼容图层接口，新实现不复制其组件或 shader。相关依赖声明见 THIRD-PARTY-NOTICES.md。对外不宣称 MIT 软件没有任何义务：仍需保留版权及许可声明。
