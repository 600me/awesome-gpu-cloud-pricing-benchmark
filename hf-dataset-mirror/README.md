---
license: mit
task_categories:
  - tabular-classification
language:
  - en
tags:
  - gpu
  - cloud-pricing
  - h100
  - a100
  - l40s
  - rtx-4090
  - tco
  - llm-inference
  - cost-engineering
  - benchmark
size_categories:
  - n<1K
pretty_name: "GPU Cloud H100/A100/L40S/4090 Real Pricing & Effective Cost Benchmark (2026)"
---

# GPU Cloud H100/A100/L40S/RTX 4090 Pricing & Effective-Cost Benchmark (2026)

Catalogue $/GPU-hour is not what you pay. This dataset records the advertised on-demand rate and the
**effective cost of one *useful* GPU-hour** after 150 GB of model storage, cold-start pre-pull, and a
realistic 85% utilisation ceiling.

## Files

| File | Rows | Description |
|---|---|---|
| `data/gpu_cloud_pricing_2026.csv` | 28 | Wide table, one row per provider/GPU/tier |
| `data/gpu_cloud_pricing_2026.jsonl` | 28 | Same records as newline-delimited JSON |

## Schema

| Column | Type | Meaning |
|---|---|---|
| `provider` | string | Vendor (RunPod, Vast.ai, Lambda, CoreWeave, AWS, GCP, Azure) |
| `gpu_model` | string | GPU SKU as sold |
| `vram_gb` | int | VRAM per GPU |
| `tier` | string | Community / Secure / on-demand / node size |
| `usd_per_gpu_hour` | float | Published on-demand list rate |
| `usd_per_100_gpu_hours` | float | Straight-line 100-hour cost |
| `bundle_min_gpus` | int | Minimum billable GPUs (bundle rounding) |
| `nvme_usd_per_gb_month` | float | Attached NVMe list rate |
| `cold_start_minutes` | float | Image pull + model load before first token |
| `egress_usd_per_gb` | float | Egress list rate where charged |
| `storage_usd_per_hour_150gb` | float | 150 GB NVMe amortised per hour |
| `cold_start_usd_per_hour` | float | Cold start amortised over an 8-hour session |
| `effective_usd_per_useful_hour` | float | **(rate + storage + cold start) / 0.85 utilisation** |

## Method (fully reproducible)

```
storage_hour  = nvme_usd_per_gb_month * 150 / 730
cold_hour     = (cold_start_minutes / 60) * usd_per_gpu_hour / 8
effective     = (usd_per_gpu_hour + storage_hour + cold_hour) / 0.85
```

Utilisation 0.85 is an explicit planning assumption, not a measurement. Change it and the ranking
between a cheap marketplace bundle and a fixed on-demand node can flip.

## Headline result

Cheapest effective useful GPU-hour in this snapshot: **RunPod RTX 4090 (Community) at $0.42/h**, versus
$0.34/h advertised — a 25% gap between the invoice line and the cost of useful compute.

## Summary table

| Provider | GPU | Tier | $/GPU-h | $/100 GPU-h | Effective $/useful h |
|---|---|---|---|---|---|
| RunPod | H100 SXM | Community | $2.69 | $269.00 | $3.19 |
| RunPod | H100 SXM | Secure | $3.99 | $399.00 | $4.72 |
| RunPod | H100 PCIe | Community | $1.99 | $199.00 | $2.37 |
| RunPod | H100 PCIe | Secure | $2.89 | $289.00 | $3.43 |
| RunPod | A100 80G SXM | Community | $1.39 | $139.00 | $1.66 |
| RunPod | A100 80G SXM | Secure | $1.79 | $179.00 | $2.13 |
| RunPod | A100 80G PCIe | Community | $1.19 | $119.00 | $1.43 |
| RunPod | A100 80G PCIe | Secure | $1.79 | $179.00 | $2.13 |
| RunPod | L40S | Community | $0.99 | $99.00 | $1.19 |
| RunPod | RTX 4090 | Community | $0.34 | $34.00 | $0.42 |
| RunPod | RTX 4090 | Secure | $0.89 | $89.00 | $1.07 |
| Vast.ai | H100 SXM | Verified on-demand | $1.79 | $178.80 | $2.12 |
| Vast.ai | H100 PCIe | Verified on-demand | $2.00 | $200.10 | $2.38 |
| Vast.ai | A100 80G SXM | Verified on-demand | $0.99 | $98.90 | $1.18 |
| Vast.ai | A100 80G PCIe | Verified on-demand | $0.80 | $80.20 | $0.96 |
| Vast.ai | RTX 4090 | Verified on-demand | $0.46 | $45.60 | $0.55 |
| Lambda | H100 SXM | On-demand | $2.99 | $299.00 | $3.53 |
| Lambda | A100 40G SXM | On-demand | $1.29 | $129.00 | $1.52 |
| Lambda | L40S | On-demand | $0.86 | $86.00 | $1.02 |
| CoreWeave | H100 SXM | On-demand | $4.76 | $476.00 | $5.62 |
| CoreWeave | L40S | On-demand | $1.99 | $199.00 | $2.36 |
| AWS | H100 SXM (p5.48xlarge) | On-demand, 8-GPU node | $12.29 | $1229.00 | $14.49 |
| AWS | A100 40G (p4d.24xlarge) | On-demand, 8-GPU node | $4.10 | $410.00 | $4.85 |
| AWS | L40S (g6e.xlarge) | On-demand, 1-GPU node | $1.86 | $186.10 | $2.21 |
| GCP | H100 SXM (a3-highgpu-8g) | On-demand, 8-GPU node | $11.06 | $1106.00 | $13.04 |
| GCP | A100 40G (a2-highgpu-1g) | On-demand, 1-GPU node | $3.67 | $367.00 | $4.34 |
| Azure | H100 SXM (ND96isr v5) | On-demand, 8-GPU node | $12.29 | $1229.00 | $14.49 |
| Azure | A100 80G (NC24ads v4) | On-demand, 1-GPU node | $3.67 | $367.00 | $4.34 |

## Use the calculators and mirror

- [Interactive calculator](https://gpu.mybskm.top/calculator/?utm_source=hf_dataset_gpu)
- [Benchmark site](https://gpu.mybskm.top/?utm_source=hf_dataset_gpu)
- [HuggingFace Space](https://huggingface.co/spaces/600me/llm-gpu-cost-calculator)

**Deep dives**
- [RunPod vs Vast.ai: real H100/A100 cost after cold start, NVMe and egress](https://gpu.mybskm.top/blog/runpod-vs-vastai-h100-a100.html)
- [The H100 rental trap](https://gpu.mybskm.top/blog/h100-rental-trap.html)


## The 4-calculator / 4-Space / 4-Dataset matrix

**Online calculators**
- [GPU cloud true TCO](https://gpu.mybskm.top/calculator/?utm_source=hf_dataset_matrix)
- [Scraping / anti-bot TCO](https://scrape.mybskm.top/calculator/?utm_source=hf_dataset_matrix)
- [Residential proxy sticky-session loss](https://proxy.mybskm.top/calculator/?utm_source=hf_dataset_matrix)
- [MoR vs US LLC breakeven](https://pay.mybskm.top/?utm_source=hf_dataset_matrix)

**HuggingFace Static Spaces**
- [gpu-cloud-h100-a100-pricing-benchmark](https://huggingface.co/spaces/600me/llm-gpu-cost-calculator)
- [web-scraping-anti-bot-api-benchmark](https://huggingface.co/spaces/600me/rag-web-scraping-cost-calculator)
- [residential-proxy-commercial-policy-matrix](https://huggingface.co/spaces/600me/residential-proxy-sticky-session-calculator)
- [global-saas-mor-vs-us-llc-fee-matrix](https://huggingface.co/spaces/600me/ai-saas-stripe-vs-mor-tax-calculator)

**HuggingFace Datasets**
- [web-scraping-anti-bot-api-benchmark](https://huggingface.co/datasets/600me/web-scraping-anti-bot-api-benchmark)
- [residential-proxy-commercial-policy-matrix](https://huggingface.co/datasets/600me/residential-proxy-commercial-policy-matrix)
- [global-saas-mor-vs-us-llc-fee-matrix](https://huggingface.co/datasets/600me/global-saas-mor-vs-us-llc-fee-matrix)


## Transparency & FTC affiliate disclosure

This dataset is published by the independent cost-research project at mybskm.top. Some outbound vendor links are affiliate links: if you open one and later buy, we may earn a commission at no extra cost to you. Commissions never change the measured numbers, the formula, or which vendor wins a scenario, and the free open-source baseline is included on purpose because it pays us nothing. Every price is a vendor-published list rate captured on the `observed_at` date; prices, trials, KYC rules and refund terms change without notice. Nothing here is a quote, a guarantee of eligibility, tax or legal advice, or a promise of results. Verify current pricing and terms with the vendor before purchasing.
