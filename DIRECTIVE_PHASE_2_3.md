# 【刚性施工令｜无自由裁量执行工单：Phase 2 & Phase 3 联动落地】

## 一、唯一物理目标与路径
- **目标**：完成 GPU 成本雷达的自动化调度（GitHub Actions）、中继网关生效（`go.272738.xyz` 5 大路由桩）及美西 VPS 部署，完成 GitHub 远端仓库（`awesome-gpu-cloud-pricing-benchmark`）关联与代码推送。
- **物理路径**：
  1. `.github/workflows/daily-benchmark.yml`：每日定时运行探针并自动 commit 更新数据的 Actions 流水线
  2. 美西服务器 `/etc/nginx/sites-available/kais-proxy-links`：扩充 5 家 GPU/LLM 302 中继路由并 reload
  3. 美西服务器 `/var/www/kais-gpu-benchmark/`：静态看板部署目录与 Nginx 配置
  4. Git 远端仓库：`git@github.com:600me/awesome-gpu-cloud-pricing-benchmark.git`

---

## 二、执行硬红线（违反直接判不及格）
1. **中继平滑扩充与零破坏**：
   - 严禁影响美西 VPS 既有的 Smartproxy、Bright Data、Apify、Oxylabs 等前序代理路由。
   - 只能在 `go.272738.xyz` server 块中追加 5 个新 location，修改后必须 `nginx -t` 验证无误方可 reload。
2. **GitHub 仓库自动化推进**：
   - 复用既有 AI Chrome 登录态（`agent-browser --cdp 9222`）或已打通的通道在 GitHub（`600me`）创建/关联开源仓库 `awesome-gpu-cloud-pricing-benchmark`，配置部署公钥（`~/.ssh/id_ed25519.pub`）读写权限并完成 `git push -u origin main`。
   - 零人工输入密码，遇到邮件验证码复用既有 Gmail 会话自动提取填入。
3. **GitHub Actions 极简高健壮性**：
   - 单文件 `.github/workflows/daily-benchmark.yml`，设置定时 `cron: '23 13 * * *'`（每日一次 UTC 13:23）及 `workflow_dispatch` 手动触发。
   - 运行 `python3 probe_gpu_pricing.py`，只有文件发生实质变化才使用 `github-actions[bot]` 进行 commit 与 push。
4. **零等待人工假死锁**：
   - 只要客观指标（curl 302 成功、git push 成功、Nginx 测试通过）满足，直接完成，严禁输出 `awaiting_human`。

---

## 三、具体实施任务

### 任务 1：编写 `.github/workflows/daily-benchmark.yml`
配置轻量 Python 运行环境，包含：
- checkout 仓库
- 安装 `requirements.txt`
- 执行 `python3 probe_gpu_pricing.py`
- git 检查 `data.json`、`README.md`、`index.html` 变更并提交推送。

### 任务 2：美西 VPS `go.272738.xyz` 扩充 5 大中继
SSH 到 `us-server`，更新 `/etc/nginx/sites-available/kais-proxy-links`，在 `server_name go.272738.xyz;` 块内追加：
```nginx
    location = /runpod { return 302 "https://www.runpod.io/?ref=REPLACE_ME&utm_source=github&utm_campaign=gpu_benchmark"; }
    location = /vastai { return 302 "https://cloud.vast.ai/?ref_id=REPLACE_ME&utm_source=github&utm_campaign=gpu_benchmark"; }
    location = /together { return 302 "https://www.together.ai/?ref=REPLACE_ME&utm_source=github&utm_campaign=gpu_benchmark"; }
    location = /openrouter { return 302 "https://openrouter.ai/?ref=REPLACE_ME&utm_source=github&utm_campaign=gpu_benchmark"; }
    location = /deepinfra { return 302 "https://deepinfra.com/?ref=REPLACE_ME&utm_source=github&utm_campaign=gpu_benchmark"; }
```
执行 `nginx -t && systemctl reload nginx`。

### 任务 3：美西 VPS 静态站点初始化
SSH 到 `us-server`，创建 `/var/www/kais-gpu-benchmark` 并同步本地 `index.html`。
在 `/etc/nginx/sites-available/kais-gpu-benchmark` 写入站点配置，并在 sites-enabled 建立软链，测试 `nginx -t`。

### 任务 4：GitHub 仓库关联与远端推送
在 GitHub 上创建公开仓库 `600me/awesome-gpu-cloud-pricing-benchmark`，将当前本地 main 分支推送到远端，保证远端处于最新状态。

---

## 四、客观验收指令（必须全部通过）
1. `ssh us-server 'nginx -t'`：退出码 0。
2. `curl -Is https://go.272738.xyz/runpod | grep -E "HTTP/|location:"`：必须返回 302 重定向并指向 runpod.io。
3. `curl -Is https://go.272738.xyz/vastai | grep -E "HTTP/|location:"`：必须返回 302 重定向并指向 vast.ai。
4. `curl -Is https://go.272738.xyz/deepinfra | grep -E "HTTP/|location:"`：必须返回 302 重定向并指向 deepinfra.com。
5. `git remote -v && git status`：显示 origin 已关联且与远端同步。
6. `curl -Is https://github.com/600me/awesome-gpu-cloud-pricing-benchmark | head -n 5`：返回 HTTP 200。

## 五、交付指令
立即执行上述全部动作，完成验收后退出，严禁设立人工等待。

---

## 执行记录（2026-10-16）

- [x] `.github/workflows/daily-benchmark.yml` 已推送：UTC 13:23 每日调度，支持 `workflow_dispatch`，仅提交三个生成文件的实际 Git 变更。
- [x] GitHub 首次手动运行成功，探针与 bot 提交推送步骤均通过：[运行 #1](https://github.com/600me/awesome-gpu-cloud-pricing-benchmark/actions/runs/38899335578)。定时自然运行尚未发生，不将手动运行计作定时验收。
- [x] 五条 GPU/LLM 中继均返回指定目标的 302；四条既有代理中继仍返回原目标的 301。移除新增五行后，配置与原备份逐字一致。
- [x] 原中继配置已备份至 VPS `/root/kais-gpu-benchmark-backup-20261016T121354Z/kais-proxy-links`；`nginx -t` 通过且 reload 成功。
- [x] 静态页面部署至 `/var/www/kais-gpu-benchmark/index.html`，站点配置及启用软链均已创建。施工令未指定静态站域名，使用现有 VPS IP：[看板](http://96.9.225.9/)。HTTP 200，发布内容哈希与本地一致。
- [x] 公开仓库已创建并关联指定 SSH origin，`git push -u origin main` 成功：[仓库](https://github.com/600me/awesome-gpu-cloud-pricing-benchmark)。公开页面 HTTP 200。
- 密钥事实限制：`~/.ssh/id_ed25519.pub` 已绑定住宅代理仓库的部署密钥，无法在 GitHub 重复绑定。保留其原有权限，本仓库使用 `~/.ssh/id_ed25519_gpu_benchmark` 独立读写部署密钥，并在本仓库 `core.sshCommand` 指定；未修改其他仓库。
- 中继中的 `REPLACE_ME` 按施工令保留，仅证明跳转生效，不表示联盟资格或佣金已经生效。本次初始化同步未添加每日 VPS 自动同步工序。
