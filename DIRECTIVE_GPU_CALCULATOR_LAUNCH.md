# 【刚性施工令｜无自由裁量执行工单：纯静态大模型算力成本计算器与双端落地】

## 一、物理目标与交付定义
- **目标**：
  1. **【计算器核心交付】编写纯静态科学计算器 `calculator/index.html`**：
     - 在 `/Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/calculator/index.html` 创建独立的纯前端科学计算器；
     - 采用原生 HTML5 + Vanilla JS + 科技感 Dark Theme CSS，零前端打包依赖，打开即秒开；
     - 支持 4 大核心参数：模型（Llama 3.1 8B、Llama 3.3 70B、Qwen 2.5 72B、DeepSeek V3/R1 671B MoE、自定义参数量）、精度（BF16/FP8/INT4）、上下文窗口（4k/8k/32k/128k）、并发数（1/4/16/64）；
     - 显存算法必须精确：含权重显存、动态 KV Cache（含 DeepSeek 独家 MLA 潜在注意力优化算法）、CUDA 2GB 开销与 15% 安全余量；
     - 输出显存拆解图表、最低显卡张数（4090/L40S/A100/H100/H200）、NVLink 跨卡通信拓扑告警、RunPod 与 Vast.ai 真实价格账本与“强制 2 卡捆绑”避坑提示；
     - 嵌入高质感出单按钮（直通 `https://go.272738.xyz/runpod` 与 `https://go.272738.xyz/vastai`，带参 `utm_source=gpu_calculator&utm_medium=cta`），并包含合规 FTC 披露；
  2. **【HuggingFace 镜像包】创建 `hf-space-mirror/` 镜像目录**：
     - 在 `/Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/hf-space-mirror/` 创建：
       - `index.html`（与 calculator/index.html 完全一致）；
       - `README.md`（配置 HuggingFace Static Space 元数据，sdk: static，零容器休眠）；
  3. **【主站导航集成】更新主站看板 `index.html`**：
     - 在 `gpu.mybskm.top` 主站顶部或显要位置增加直达按钮/导航：`[🧮 Interactive GPU Fit & Cost Calculator ↗]` 指向 `/calculator/`；
  4. **【离线算法断言测试】编写 `test_calculator_math.py`**：
     - 针对 8B（BF16 4k）、70B（BF16 4k 与 INT4 4k）、DeepSeek 671B（FP8 4k MLA）进行显存计算断言测试，退出码必须为 0；
  5. **【美西 VPS 部署与全网验收】**：
     - 同步至 `us-server:/var/www/kais-gpu-benchmark/`；
     - 确保 `curl -sI https://gpu.mybskm.top/calculator/` 返回 HTTP 200；
     - Git commit 并 push 到远端。

---

## 二、代码与公式执行硬红线（违反直接判不及格）
1. **纯静态零依赖，严禁引入复杂框架**：
   - 必须是纯单文件 HTML+JS+CSS（或内部引用本地静态文件），严禁引入 npm/webpack 打包，严禁引入外部大体积商业 JS 库；
2. **算法科学严谨**：
   - 70B BF16 4k 显存需求必须在 ~150-155 GiB 区间（断言必须推荐 4x A100/H100，不得推荐 2 卡）；
   - DeepSeek 671B 必须正确按 MLA 架构计算 KV Cache（不可按普通 MHA 错误暴涨）；
3. **真实商业链接与披露**：
   - 严禁出现 `REPLACE_ME`；CTA 必须直链已核验的 RunPod / Vast.ai 中继；
   - 必须在 CTA 附近展示清晰的 FTC 佣金透明披露；
4. **HuggingFace 静态兼容**：
   - `hf-space-mirror/README.md` 必须包含合法的 YAML Frontmatter（sdk: static）。

---

## 三、客观验收指令（必须全部退出码为 0）
1. 算法离线单元测试：
   - `python3 /Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/test_calculator_math.py` 退出码必须为 0；
2. 主站计算器在线存活验证：
   - `curl -s -I "https://gpu.mybskm.top/calculator/" | grep -q "200"` 退出码必须为 0；
3. 链接与合规验证：
   - `grep "REPLACE_ME" /Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/calculator/index.html` 必须返回空（退出码为 1）；
   - `grep "go.272738.xyz/runpod" /Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/calculator/index.html` 退出码必须为 0；
4. HuggingFace 静态镜像包验证：
   - `grep "sdk: static" /Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark/hf-space-mirror/README.md` 退出码必须为 0；
5. Git 状态核验：
   - `git -C "/Users/a600/project-workspaces(项目工作区)/kais-gpu-cloud-benchmark" status` 保持 clean，已 commit 并 push 到远端。
