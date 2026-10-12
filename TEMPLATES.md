# 可下载的风格模板接口

自带 **Studio Blue** 模板：延续科技口播的蓝色光带、金属球体、人物侧栏、章节配色和多种图解。动效用 MIT Anime.js，3D 用 MIT Three.js；光带 shader 独立实现。没有打包 React Bits、GSAP、个人视频或测试素材。

新模板是一个目录，根目录包含 `template.json`。可发布到独立 GitHub 仓库或作为下载包；用户下载后运行：

```sh
python pipeline.py build --project local/my-video --template /path/to/downloaded-template
```

参照仓库自带 template.json：files 映射模板源文件到生成项目的文件名；assets 逐项列出 file、target、source、license；gpuModules 指定 UI 捕获时剔除的 WebGL 组件；previewEntrypoint 是 JSX 入口。复制路径不能逃出模板或项目目录。模板是可执行代码，只使用可信作者来源。

**layered-film-v1** 协议当前是固定的1080p24、presenter-v1人物几何：`window.__film.seek(t,true)`、getScene()、duration、window.__story；DOM 的 .light canvas、.scene-visual canvas、.portrait、#speaker、.bottom 等保持 ADAPTER.md 中的含义。seek 必须确定性地绘制指定时刻，快速往返拖动仍还原正确画面。

可自由改变排版细节、章节配色、图解、模型和动效；改变人物几何、字幕坐标或图层协议时，需要同步提供/修改合成适配器。目前不承诺任何 React 网站直接放入即可加速导出。

模板上传前：保留所有第三方版权及许可；字体/模型/截图附许可；用合成或获授权的示例验证；附版本号与协议；检查预览和导出的一致性；不提交用户媒体及配置。仓库 LICENSE 仅覆盖本项目自有代码，不能替代模板内第三方素材的授权。
