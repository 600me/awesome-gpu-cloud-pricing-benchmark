# Cheapest H100 GPU Cloud & DeepSeek R1 / V3 API Pricing Benchmark (2026)

[Live pricing dashboard](https://gpu.mybskm.top/)

Updated: **2026-11-12T20:57:15Z** · All prices in USD.

Stop paying for idle GPUs and expensive output tokens. Compare RunPod vs Vast.ai GPU rates, then compare Together.ai, OpenRouter and DeepInfra API costs before your next deployment.

100 H100 SXM GPU-hours cost $213.60 at Vast.ai (Verified on-demand sample, cache) versus $439.00 at RunPod (Secure, live): a $225.40 compute-only gap. These are quoted rates, not equivalent service guarantees or a reservation.

[Launch on RunPod](https://go.272738.xyz/runpod?src=gpu_home) · [Find a Vast.ai GPU](https://go.272738.xyz/vastai?src=gpu_home)

> **FTC Affiliate Disclosure: Some outbound vendor links on this page (via go.272738.xyz, such as ScraperAPI, Smartproxy/Decodo, RunPod, Vast.ai, ElevenLabs, and Firstbase) are affiliate links that may earn a commission at no extra cost to you. Unaffiliated vendors and open-source baselines are included using identical objective formulas.**

## ⚡ The Quick Verdict (For Readers in a Hurry)

- **Pick [RunPod](https://go.272738.xyz/runpod?gpu=H100+PCIe&src=gpu_readme_verdict) if** you need zero-cold-start Docker templates (vLLM, PyTorch, ComfyUI), persistent NVMe network volumes, and instant per-second billing — [**Deploy an H100 / A100 / RTX 4090 Pod ($10–$500 Partner Bonus Box)**](https://go.272738.xyz/runpod?gpu=H100+PCIe&src=gpu_readme_verdict_cta).
- **Pick [Vast.ai](https://go.272738.xyz/vastai?gpu=h100%20sxm&src=gpu_readme_verdict) if** you run fault-tolerant batch fine-tuning or evals and want the lowest raw spot/on-demand GPU rate (saves **$185.40 per 100 H100 SXM hours**) — [**Search Verified Vast.ai GPUs (Auto-Applied Partner Credit)**](https://go.272738.xyz/vastai?gpu=h100%20sxm&src=gpu_readme_verdict_cta).
- **Pick [ElevenLabs](https://go.272738.xyz/elevenlabs?src=gpu_readme_verdict) if** your workload is AI voice cloning, multilingual TTS, or video dubbing — [**Start Free on ElevenLabs (10,000 chars/mo free tier + 50% OFF Creator 1st mo)**](https://go.272738.xyz/elevenlabs?src=gpu_readme_verdict_cta).

## 🎟️ 2026 GPU Tier & SKU Direct Launch Matrix (1-Click Pod Deployment + Partner Credits)

| Provider & GPU Tier | VRAM | On-Demand Rate | 100 GPU-Hours | Partner Offer / Trial | 1-Click SKU Deployment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RunPod — RTX 4090 Community** | 24 GB | **$0.340/hr** | $34.00 | Per-second billing + $10–$500 Bonus Box | [**Deploy RTX 4090 Pod →**](https://go.272738.xyz/runpod?gpu=RTX+4090&src=gpu_tier_rtx4090) |
| **RunPod — A100 80GB PCIe** | 80 GB | **$1.190/hr** | $119.00 | Pre-built vLLM / DeepSeek Templates | [**Deploy A100 80GB Pod →**](https://go.272738.xyz/runpod?gpu=A100+PCIe&src=gpu_tier_a100) |
| **RunPod — H100 80GB PCIe** | 80 GB | **$1.990/hr** | $199.00 | Instant SSH + NVMe Volume Support | [**Deploy H100 80GB Pod →**](https://go.272738.xyz/runpod?gpu=H100+PCIe&src=gpu_tier_h100) |
| **Vast.ai — RTX 4090 Verified** | 24 GB | **$0.341/hr** | $34.10 | Up to 60% off AWS/GCP + Partner Rate | [**Rent Vast.ai RTX 4090 →**](https://go.272738.xyz/vastai?gpu=rtx%204090&src=gpu_tier_rtx4090) |
| **Vast.ai — A100 80GB PCIe** | 80 GB | **$1.002/hr** | $100.20 | Verified Datacenter Host Filter | [**Rent Vast.ai A100 80GB →**](https://go.272738.xyz/vastai?gpu=a100%20pcie&src=gpu_tier_a100) |
| **Vast.ai — H100 80GB SXM** | 80 GB | **$2.136/hr** | $213.60 | Lowest 100-hr H100 SXM Total ($213.60) | [**Rent Vast.ai H100 SXM →**](https://go.272738.xyz/vastai?gpu=h100%20sxm&src=gpu_tier_h100) |
| **ElevenLabs — Voice AI & Dubbing** | Managed API | **$0 Free** / $5 Starter | 10k–30k chars | Free tier available + 50% OFF Creator | [**Start Free Voice Trial →**](https://go.272738.xyz/elevenlabs?src=gpu_tier_elevenlabs) |


## Calculators and deep research

Free tools and dollar-per-useful-GPU-hour teardowns behind this dashboard:

- [VRAM & Cost Calculator](/calculator/)
- [All research (blog index)](/blog/)
- [The H100 rental trap](/blog/h100-rental-trap.html)
- [RunPod vs Vast.ai real cost](/blog/runpod-vs-vastai-h100-a100.html)
- [HF Space: LLM GPU cost calculator](https://gpu.mybskm.top/calculator/)

## Cheapest H100 GPU cloud: hourly price matrix

Compute-only prices per GPU-hour; storage, bandwidth, tax and setup time can add to your bill. A sampled minimum is not a market-wide cheapest claim. Multi-GPU bundles require the full bundle payment.

| Provider / tier | GPU | VRAM | USD / GPU-hour | 100 GPU-hours | Evidence | Launch |
|---|---|---:|---:|---:|---|---|
| RunPod / Community | RTX 4090 | 24 GB | $0.340 | $34.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| Vast.ai / Verified on-demand sample | RTX 4090 | 24 GB | $0.363 | $36.30 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/vastai?src=gpu_home) |
| Vast.ai / Verified on-demand sample | A100 80G PCIe | 80 GB | $0.802 | $80.20 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/vastai?src=gpu_home) |
| RunPod / Secure | RTX 4090 | 24 GB | $0.890 | $89.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| Vast.ai / Verified on-demand sample | A100 80G SXM | 80 GB | $1.083 | $108.30 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/vastai?src=gpu_home) |
| RunPod / Community | A100 80G PCIe | 80 GB | $1.190 | $119.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| RunPod / Community | A100 80G SXM | 80 GB | $1.390 | $139.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| RunPod / Community | H100 PCIe | 80 GB | $1.990 | $199.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| RunPod / Secure | A100 80G PCIe | 80 GB | $2.090 | $209.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| Vast.ai / Verified on-demand sample | H100 SXM | 80 GB | $2.136 | $213.60 | cache (origin: live); 2026-10-31T17:49:47Z | [Launch](https://go.272738.xyz/vastai?src=gpu_home) |
| RunPod / Secure | A100 80G SXM | 80 GB | $2.190 | $219.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| RunPod / Community | H100 SXM | 80 GB | $2.690 | $269.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| RunPod / Secure | H100 PCIe | 80 GB | $2.890 | $289.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |
| Vast.ai / Verified on-demand sample | H100 PCIe | 80 GB | $3.609 | $360.90 | cache (origin: live); 2026-10-31T17:49:47Z | [Launch](https://go.272738.xyz/vastai?src=gpu_home) |
| RunPod / Secure | H100 SXM | 80 GB | $4.390 | $439.00 | live; 2026-11-12T20:57:15Z | [Launch](https://go.272738.xyz/runpod?src=gpu_home) |

## DeepSeek R1 / V3 API pricing benchmark and Llama 3.3 70B

Rates below are USD per 1M tokens. A long reasoning answer can erase a cheap input rate: the example workload uses **10M input + 2M output tokens**, excluding cached-input discounts. Exact model IDs and revisions are shown; Turbo, 0324 and 0528 variants are not identical checkpoints.

| Provider | Model / endpoint | Input / 1M | Output / 1M | Example bill | Evidence | Start |
|---|---|---:|---:|---:|---|---|
| OpenRouter | DeepSeek-V3 (`deepseek/deepseek-chat`) | $0.320000 | $0.890000 | $4.98 | live; 2026-11-12T20:57:15Z | [Explore](https://openrouter.ai) |
| OpenRouter | DeepSeek-R1 (`deepseek/deepseek-r1`) | $0.700000 | $2.500000 | $12.00 | cache (origin: live); 2026-10-18T16:37:25Z | [Explore](https://openrouter.ai) |
| OpenRouter | Llama-3.3-70B (`meta-llama/llama-3.3-70b-instruct`) | $0.710000 | $0.710000 | $8.52 | live; 2026-11-12T20:57:15Z | [Explore](https://openrouter.ai) |
| DeepInfra | DeepSeek-V3 (`deepseek-ai/DeepSeek-V3`) | $0.320000 | $0.890000 | $4.98 | live; 2026-11-12T20:57:15Z | [Explore](https://deepinfra.com) |
| DeepInfra | DeepSeek-R1-0528 (`deepseek-ai/DeepSeek-R1-0528`) | $0.500000 | $2.150000 | $9.30 | live; 2026-11-12T20:57:15Z | [Explore](https://deepinfra.com) |
| DeepInfra | Llama-3.3-70B Turbo (`meta-llama/Llama-3.3-70B-Instruct-Turbo`) | $0.100000 | $0.320000 | $1.64 | live; 2026-11-12T20:57:15Z | [Explore](https://deepinfra.com) |
| Together.ai | DeepSeek-V3-0324 (`deepseek-ai/DeepSeek-V3`) | $1.250000 | $1.250000 | $15.00 | cache (origin: baseline); reference 2026-10-16 | [Explore](https://www.together.ai) |
| Together.ai | DeepSeek-R1-0528 (`deepseek-ai/DeepSeek-R1-0528`) | N/A | N/A | N/A | null; reference 2026-10-16 | [Explore](https://www.together.ai) |
| Together.ai | Llama-3.3-70B (`meta-llama/Llama-3.3-70B-Instruct-Turbo`) | $1.040000 | $1.040000 | $12.48 | cache (origin: baseline); reference 2026-10-16 | [Explore](https://www.together.ai) |

## RunPod vs Vast.ai — choose the bill you can actually sustain

| Provider | Billing pitfall to check | Practical next step |
|---|---|---|
| RunPod | Community and Secure are separate tiers; hourly catalog rates do not reserve inventory. | [Choose your GPU and tier](https://go.272738.xyz/runpod?src=gpu_home) |
| Vast.ai | Host reliability, storage and multi-GPU bundle requirements can outweigh a low sampled unit rate. | [Check the full offer](https://go.272738.xyz/vastai?src=gpu_home) |
| Together.ai | Model-page reference rates do not prove serverless availability; R1 is currently unavailable there. | [Check deployment options](https://www.together.ai) |
| OpenRouter | Routing/provider selection can change the effective quote; verify the selected endpoint. | [Compare routed endpoints](https://openrouter.ai) |
| DeepInfra | Compare the exact revision and quantization; output and reasoning tokens drive the bill. | [Choose an inference model](https://deepinfra.com) |

## Quote details and source transparency

Live = public API quote observed this run; cache = previous quote with its original date and origin; baseline = dated built-in reference, not a refreshed quote; N/A = no usable price. The page update time is not the quote freshness time. This is a pricing benchmark, not a measured speed, quality or uptime benchmark.

- **RunPod · H100 SXM**: Community catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **RunPod · H100 SXM**: Secure catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **Vast.ai · H100 SXM**: Lowest sampled verified rentable offer; 1 GPU bundle; storage/network extra (cache (origin: live); 2026-10-31T17:49:47Z). Source: `https://console.vast.ai/api/v0/bundles/`.
- **RunPod · H100 PCIe**: Community catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **RunPod · H100 PCIe**: Secure catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **Vast.ai · H100 PCIe**: Lowest sampled verified rentable offer; 2 GPU bundle; storage/network extra (cache (origin: live); 2026-10-31T17:49:47Z). Source: `https://console.vast.ai/api/v0/bundles/`.
- **RunPod · A100 80G SXM**: Community catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **RunPod · A100 80G SXM**: Secure catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **Vast.ai · A100 80G SXM**: Lowest sampled verified rentable offer; 1 GPU bundle; storage/network extra (live; 2026-11-12T20:57:15Z). Source: `https://console.vast.ai/api/v0/bundles/`.
- **RunPod · A100 80G PCIe**: Community catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **RunPod · A100 80G PCIe**: Secure catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **Vast.ai · A100 80G PCIe**: Lowest sampled verified rentable offer; 1 GPU bundle; storage/network extra (live; 2026-11-12T20:57:15Z). Source: `https://console.vast.ai/api/v0/bundles/`.
- **RunPod · RTX 4090**: Community catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **RunPod · RTX 4090**: Secure catalog rate; inventory not guaranteed (live; 2026-11-12T20:57:15Z). Source: `https://api.runpod.io/graphql`.
- **Vast.ai · RTX 4090**: Lowest sampled verified rentable offer; 1 GPU bundle; storage/network extra (live; 2026-11-12T20:57:15Z). Source: `https://console.vast.ai/api/v0/bundles/`.
- **OpenRouter · DeepSeek-V3**: Router catalog; provider routing can change (live; 2026-11-12T20:57:15Z). Source: `https://openrouter.ai/api/v1/models`.
- **OpenRouter · DeepSeek-R1**: Router catalog; provider routing can change (cache (origin: live); 2026-10-18T16:37:25Z). Source: `https://openrouter.ai/api/v1/models`.
- **OpenRouter · Llama-3.3-70B**: Router catalog; provider routing can change (live; 2026-11-12T20:57:15Z). Source: `https://openrouter.ai/api/v1/models`.
- **DeepInfra · DeepSeek-V3**: Standard uncached catalog rate (live; 2026-11-12T20:57:15Z). Source: `https://api.deepinfra.com/models/list`.
- **DeepInfra · DeepSeek-R1-0528**: 0528 revision; not the original R1 checkpoint (live; 2026-11-12T20:57:15Z). Source: `https://api.deepinfra.com/models/list`.
- **DeepInfra · Llama-3.3-70B Turbo**: Turbo FP8 variant (live; 2026-11-12T20:57:15Z). Source: `https://api.deepinfra.com/models/list`.
- **Together.ai · DeepSeek-V3-0324**: Dedicated/reference listing; serverless availability not verified (cache (origin: baseline); reference 2026-10-16). Source: `https://www.together.ai/models/deepseek-v3`.
- **Together.ai · DeepSeek-R1-0528**: Not available on Together Serverless; no current token quote (null; reference 2026-10-16). Source: `https://www.together.ai/models/deepseek-r1`.
- **Together.ai · Llama-3.3-70B**: Public pricing page reference; API authentication required (cache (origin: baseline); reference 2026-10-16). Source: `https://www.together.ai/pricing`.

## How prices are normalized

OpenRouter USD/token × 1,000,000; DeepInfra cents/token × 10,000. Vast.ai bundle USD/hour ÷ GPU count; GPU rates round to 3 decimals. Example API bill = input rate × 10 + output rate × 2. No paid inference or GPU rental is performed.

Refresh locally with `python3 -m pip install -r requirements.txt` followed by `python3 probe_gpu_pricing.py`. Each provider request has a 10-second timeout. Failed or missing quotes fall back to data.json, then the dated baseline, then null. All three outputs are replaced atomically.

Product buttons point at an attributed relay for activated partners (RunPod, Vast.ai) and at the vendor's own website for unactivated ones (Together.ai, OpenRouter, DeepInfra), so no click depends on an inactive affiliate account. Visiting a provider does not purchase compute.


## Sister Projects (Matrix Interlinks)

- [Proxy Infrastructure Benchmark](https://proxy.mybskm.top)
- [Global GPU Cloud Benchmark](https://gpu.mybskm.top)
- [Global Payments Matrix](https://pay.mybskm.top)
- [Web Scraping APIs Benchmark](https://scrape.mybskm.top)

### Interactive 4-Tool Suites & Long-Tail Benchmarks

- [n1 Proxy, Anti-Detect & Serverless GPU 4-Tool Suite](https://proxy.mybskm.top/matrix/proxy-gpu-4-tools-suite.html)
- [n2 AI Website Builder, Hosting & SEO 4-Tool Suite](https://proxy.mybskm.top/site-builders/builder-hosting-seo-4-tools-suite.html)
- [n3 E-Commerce AdSpy & S2S Attribution 4-Tool Suite](https://proxy.mybskm.top/seller-tools/ecom-adspy-roas-4-tools-suite.html)
- [n4 Workflow Automation, PDF API & AI Voice 4-Tool Suite](https://proxy.mybskm.top/ai-workflow/automation-pdf-voice-4-tools-suite.html)
- [n5 Property Investment, BRRRR & STR PMS 4-Tool Suite](https://proxy.mybskm.top/property-tools/str-brrrr-pms-4-tools-suite.html)
- [n6 Game Server Tickrate, Modpack RAM & NVMe 4-Tool Suite](https://proxy.mybskm.top/game-hosting/tickrate-modpack-vps-4-tools-suite.html)
- [Whisper Large-v3 10k Audio Hours: RunPod L4 vs RTX 4090 TCO](https://proxy.mybskm.top/matrix/whisper-large-v3-10k-audio-hours-runpod-l4-rtx4090-tco.html)
- [Vultr Egress Bandwidth, Snapshot & IPv4 Hidden Surcharge Audit](https://proxy.mybskm.top/matrix/vultr-egress-bandwidth-snapshot-ipv4-hidden-surcharge-audit.html)
