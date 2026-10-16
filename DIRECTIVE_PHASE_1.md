# 【刚性施工令｜无自由裁量执行工单】

## 一、唯一物理目标与路径
- **目标**：在 `/Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/` 内单次物理闭环完成 Phase 1 全部落地代码与首版生成产物，并通过本地客观工程验收（退出码 0）。
- **物理交付路径**（严格收敛在以下最简文件，严禁新增其他模块或多层目录）：
  1. `requirements.txt`：仅 `requests`
  2. `.gitignore`：包含 `__pycache__/`, `*.pyc`, `.env` 等
  3. `probe_gpu_pricing.py`：单脚本完成公共 API 抓取、降级容错、金额计算、Markdown 与 HTML 模板静态编译
  4. `data.json`：由探针自动生成的格式化数据快照（既是公开产物，又是下次降级缓存）
  5. `README.md`：由探针自动生成的高权重 SEO 英文评测仓库正文
  6. `index.html`：由探针自动生成的暗黑极客风格独立单文件 Web 看板

## 二、执行硬红线（违反直接判不及格）
1. **架构严禁过度工程**：所有业务逻辑严格在 `probe_gpu_pricing.py` 单文件内闭环。严禁新建 `src/`、`adapters/`、`services/` 等抽象层；严禁引入 SQLite、Redis、Celery 或任何常驻守护进程。
2. **零等待人工假死锁**：严禁创建任何 `awaiting_human` 标志或等待人工确认的假死锁。脚本执行完成必须 Exit Code 0。
3. **稳健四级降级链**：
   $$\text{实时 API 采集} \longrightarrow \text{本地已有 data.json 缓存} \longrightarrow \text{脚本内置 baseline} \longrightarrow \text{标为 null}$$
   每个厂商请求超时设为 10 秒，任何单家失败在函数内 catch 并降级，绝对禁止中断整体运行。
4. **单位换算精度铁律**：
   - OpenRouter：`pricing.prompt` 与 `pricing.completion`（美元/Token）必须 $\times 1,000,000$ 换算为“每 1M Tokens 美元”。
   - DeepInfra：`cents_per_input_token` 与 `cents_per_output_token` 必须 $\times 10,000$ 换算为“每 1M Tokens 美元”。
   - RunPod & Vast.ai：小时单价保留至 2~3 位小数，明确标注 GPU 型号（H100 SXM/PCIe, A100 80G, RTX 4090）与显存。
5. **商业中继桩 1:1 锚定（严禁擅改）**：
   README.md 与 index.html 内的所有产品落地链接，必须严格使用以下解耦中继桩：
   - RunPod: `https://go.272738.xyz/runpod`
   - Vast.ai: `https://go.272738.xyz/vastai`
   - Together.ai: `https://go.272738.xyz/together`
   - OpenRouter: `https://go.272738.xyz/openrouter`
   - DeepInfra: `https://go.272738.xyz/deepinfra`
6. **SEO 与受众痛点三要素**：
   README.md 必须面向全球开发者（全英文），针对 "cheapest h100 gpu cloud", "runpod vs vast.ai", "deepseek r1 / v3 api pricing benchmark" 等高频搜索词优化，包含算力差价痛点对比表格与一键开机出口。

## 三、探针脚本 `probe_gpu_pricing.py` 必须实现的核心功能
1. **数据拉取与 Baseline**：
   - 包含内置的可靠 Baseline 数据（覆盖 RunPod, Vast.ai, Together, OpenRouter, DeepInfra 在 2026 年的主流机型与开源模型 DeepSeek-V3/R1, Llama-3.3-70B 价格）。
   - 尝试通过公共接口拉取最新报价（OpenRouter `https://openrouter.ai/api/v1/models`、DeepInfra `https://api.deepinfra.com/models/list`、RunPod/Vast.ai 公开接口）；若遇接口阻断或需特定鉴权，则平滑回退至 Baseline/历史缓存，不报错中断。
2. **原子写入（Atomic Write）**：
   - 使用临时文件加 `os.replace` 输出 `data.json`、`README.md` 与 `index.html`，防止产生半份脏数据。
3. **输出产物一致性**：
   - `data.json`：符合 `{"schema_version": 1, "generated_at": "...", "gpu": [...], "llm": [...]}` 结构。
   - `README.md`：包含更新时间戳、GPU 小时价格矩阵、LLM API Token 成本矩阵、厂商横向评测与跳转出口。
   - `index.html`：单文件 HTML/CSS/JS（暗黑极客主题、支持 GPU/LLM 标签切换、实时模糊搜索、按单价升序排序，点击按钮直达对应中继）。

## 四、客观验收指令
在项目目录执行：
```sh
python3 probe_gpu_pricing.py
```
**达标判定标准**：
- 退出码必须为 0（`$? == 0`）。
- `data.json`、`README.md`、`index.html` 文件大小均 > 1KB，且内容包含 5 大厂商的中继链接。
- 用 Python 测试解析 `data.json` 必须合法且包含 gpu 与 llm 数组。

## 五、交付指令
立即无条件执行上述工程落地，完成所有代码编写与首次探针运行。完成后直接退出，不设立任何人工阻滞。
