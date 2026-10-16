# 【刚性施工令｜无自由裁量执行工单：方案 A 独立域名 gpu.mybskm.top 自动解析与 SSL 上线】

## 一、唯一物理目标与路径
- **目标**：Kais 明确授权并指示：采用【方案 A 自动接入】，由 Codex 利用可用插件/工具完成 `gpu.mybskm.top` 域名解析（指向美西 VPS `96.9.225.9`），并在美西 VPS 执行自动化 Certbot 签发 Let's Encrypt SSL 证书，全网点亮 `https://gpu.mybskm.top`（HTTP 200）。
- **物理路径**：
  1. DNS 解析：利用插件或现有凭据/连接器为 `mybskm.top` 添加 A 记录：`gpu` ➔ `96.9.225.9`
  2. 美西服务器 Nginx 与 SSL：`us-server` 执行非交互 Certbot 申请并配置 HTTPS 虚拟主机
  3. 资产外链升级：将 `README.md` 与 `index.html` 中的公开看板地址从 IP 升级为 `https://gpu.mybskm.top` 并 push 到 GitHub

---

## 二、执行硬红线（违反直接判不及格）
1. **插件与工具优先解析**：
   - 使用可用插件、MCP、API 或 AI Chrome 登录态，为 `mybskm.top` 添加 `gpu` ➔ `96.9.225.9` 解析。
   - 严禁要求 Kais 手动去控制台添加解析。
2. **Certbot 自动化非交互**：
   - 使用：
     `certbot --nginx -d gpu.mybskm.top --non-interactive --agree-tos -m 600megd@gmail.com --redirect`
     自动签发并重载 Nginx，严禁交互式挂起。
3. **平滑生效与零破坏**：
   - 严禁影响美西 VPS 现有的 `proxy.mybskm.top`、`go.272738.xyz` 及其他现有虚拟主机。
4. **零等待人工假死锁**：
   - 只要公网 HTTPS 返回 200，直接宣告完成，严禁输出 `awaiting_human`。

---

## 三、具体实施任务

### 任务 1：添加 DNS A 记录
- 对 `mybskm.top` 添加 A 记录：
  - 子域名：`gpu`
  - 目标 IP：`96.9.225.9`
- 验证解析：`dig +short gpu.mybskm.top @8.8.8.8` 或 `1.1.1.1` 返回 `96.9.225.9`。

### 任务 2：美西 VPS 自动化签发 SSL 并配置 HTTPS
- SSH 到 `us-server`：
  - 检查 `/etc/nginx/sites-available/kais-gpu-benchmark` 包含 `server_name gpu.mybskm.top;`
  - 运行非交互 certbot：
    `certbot --nginx -d gpu.mybskm.top --non-interactive --agree-tos -m 600megd@gmail.com --redirect`
  - 运行 `nginx -t` 并 `systemctl reload nginx`

### 任务 3：本地与远端代码外链升级
- 将 `README.md` 与 `index.html` 中可能存在的 IP 访问方式更新为官方独立域名 `https://gpu.mybskm.top/`。
- 重新运行一次探针确保静态产物一致，commit 并 push 到 GitHub 远端仓库。

---

## 四、客观验收指令（必须全部通过）
1. `dig +short gpu.mybskm.top`：输出 `96.9.225.9`。
2. `ssh us-server 'nginx -t'`：退出码为 0。
3. `curl -Is https://gpu.mybskm.top | grep -E "HTTP/|location:"`：必须返回 `HTTP/2 200` 或 `HTTP/1.1 200`。
4. `curl -s https://gpu.mybskm.top | grep -i "cheapest h100"`：返回非空看板标题内容。

## 五、交付指令
立即无条件执行上述全部动作，完成验收后退出，严禁设立人工等待。


## 六、执行记录（2026-10-16T12:58:54+00:00）

- [x] 通过既有 Cloudflare 连接器添加并读回 DNS-only A 记录：`gpu.mybskm.top` → `96.9.225.9`，TTL 60。Google 公共 DNS 与 VPS 上的 `dig +short gpu.mybskm.top` 均返回目标 IP。
- [x] 原 Nginx 与页面备份：`us-server:/root/kais-gpu-domain-ssl-backup-20261016T125657Z/`；本地修改前源文件备份：`/Users/a600/tmp(临时)/kais-gpu-domain-ssl-backup-20261016T125700Z/`。
- [x] 使用工单指定完整非交互命令签发并部署 Let's Encrypt 证书；证书有效期至 `2027-01-14 11:59:01 UTC`。`nginx -t` 与 `systemctl reload nginx` 均退出 0，Nginx 为 `active`。
- [x] README 增加正式看板入口，HTML 增加正式入口与 canonical；同步修改生成器，运行探针重新生成 README、HTML 和 JSON，逐字核对生成结果一致。三个产物已同步 `/var/www/kais-gpu-benchmark/`，本地与服务器 SHA-256 一致。
- [x] 公网 `https://gpu.mybskm.top/` 返回 `HTTP/2 200`，正文匹配 `Cheapest H100`；HTTP 返回 301 到正式 HTTPS。VPS 普通 curl 与本机使用 Google DoH 的 curl 均已验证 HTTPS，未跳过 TLS 校验。
- [x] 其他 26 项 Nginx 配置文件 SHA-256 与备份前一致；`proxy.mybskm.top` 仍返回 HTTP/2 200，`go.272738.xyz/runpod` 和 `/vastai` 仍返回原专属参数的 HTTP/2 302。

本机普通 DNS 路径在新记录添加后曾返回缓存的 NXDOMAIN，因此增加 Google DoH 和 VPS 公共 DNS 交叉核验；未修改本机全局 DNS 或其他业务配置。
