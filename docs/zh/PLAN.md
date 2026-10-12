# Agent 场景计划

`plan.json` 与 media.json 的 duration 一致。场景连续覆盖整个视频，不能有空档或重叠。所有时间是源视频的绝对秒数。字段：

```json
{
 "duration": 30,
 "topic": "本期主题", "brand": "视频笔记", "speaker": "讲解者",
 "tagline": "", "introTitle": "本期主题", "introSubtitle": "",
 "chapters": [{"start":0,"short":"认识主题","theme":"blue","accent":"#b7dbff","beam":["#9ac6ff","#deedff"],"labels":["概念","方法","应用"],"summary":"本章脉络"}],
 "scenes": [{"id":"intro","start":0,"end":30,"chapter":0,"kind":"sphere","label":"AI","a":"认识主题","b":"从这里开始","desc":"一句总结","titleAt":7.2,"visualAt":8,"reveal":[],"wide":false,"motion":"scale"}]
}
```

此例只展示结构，不是给任意口播套用的内容。介绍后的固定人物转场在6.42–7.62秒，与分层合成几何保持一致。若实际介绍更长，先在计划中保留相应内容，不要让核心信息抢在口播前出现；修改人物转场时间需同时修改模板和合成适配器。

- 标题 `a`/`b`：主标题与强调行，短而准确；`desc` 概括；`wide` 为需要横向空间的图解。
- `titleAt`、`visualAt`：口播提及标题/图形的时刻。`reveal`：各项目实际提及的时间。不要凭平均间隔推测信息时间。
- `sphere` 使用 label（不写死模型名字）；`chip`、`camera`、`server`、`assembly`、`cache`、`gpu-board`、`film-reel`、`camera-rig`、`scales`：程序化3D。
- `cards`、`checklist`、`flow`：items 是 `[标题,说明]` 数组；最多三个简洁项目。
- `editorial`、`split-compare`、`prompt`、`prompt-compare`、`dialogue`：rows 是 `[标题,说明]`。
- `workflow`、`balance`、`loop`、`iteration`、`character`、`asset-tray`、`input-spectrum`、`grid-scale`、`contact-sheet`：labels 数组。workflow/balance 需要三个标签。迭代至少两个。
- `metric`：value、unit、label；`bars`/`score`：bars/scores 为 `[名称,数值]`，必须有真实依据，不凭空造评分。
- `ui`：image 是 assets 下的文件名，caption、可选 focus。素材来源和许可记录在 assets.json，不附未获授权的真实产品界面到通用模板。
- `chapter` 是章节过渡，配合新主题颜色。theme 可用 blue/cyan/violet/amber/ice。

其他预设内容见模板 Visuals/DirectedVisuals。技术教程特定预设包含领域文案，Agent 应先确认其与口播一致，再选择或改写；不能把模板中的示意当成实际产品事实。

不要连续三段使用同一结构。换版式需有信息目的。3D 进入使用渐显与小尺度变化；保持转场前后连续性。固定底部字幕条，不受句子长度影响。字幕独立保存在 captions.json，正常情况下无需在 plan 中重写。
