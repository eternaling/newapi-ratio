# newapi-ratio

自动同步上游（basellm/llm-metadata）的大模型计费倍率，合并缓存分档（cc12h/cc1h → cc）后经 GitHub Pages 发布。

## 在 newapi 中使用

「模型定价设置 → 选择同步渠道」：

- 源地址填：`https://hexo.nightsoil.cn/newapi-ratio`
- 接口选：`pricing`（newapi 会自动请求 `{源地址}/api/pricing`）

也可直接下载 `ratio_config-newapi.json`（`/api/pricing`、`/pricing` 三个路径内容完全一致）。
