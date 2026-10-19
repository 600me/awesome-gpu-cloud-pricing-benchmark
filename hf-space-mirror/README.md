---
title: GPU Fit & Cost Calculator
emoji: 🧮
colorFrom: green
colorTo: blue
sdk: static
app_file: index.html
pinned: false
license: mit
short_description: VRAM, KV cache, NVLink and GPU rental cost calculator
---

# GPU Fit & Cost Calculator

A single-file, zero-dependency static Space for sizing LLM inference on rented GPUs and pricing the result on RunPod and Vast.ai.

## What it computes

- **Weights:** total parameters × bytes per parameter for BF16 (2 B), FP8 (1 B) and INT4 (0.5 B).
- **KV cache:** GQA `2 × layers × KV heads × head dim × 2 bytes × tokens × concurrent sequences`.
- **DeepSeek MLA:** `layers × (512 latent + 64 RoPE) × 2 bytes × tokens × sequences` — the compressed latent cache, not a naive MHA blow-up.
- **Runtime floor:** 2 GiB CUDA/runtime overhead plus a 15% safety margin.
- **Card count:** 90% practical VRAM utilization, then 2/4/8-card rounding for tensor-parallel symmetry.
- **Topology:** NVLink domain checks; explicit PCIe-only warnings for RTX 4090 and L40S; multi-node warning above 8 SXM GPUs.
- **Cost ledger:** sampled RunPod and Vast.ai compute-only rates, 1-hour / 24-hour / 30-day totals, and full-bundle billing when a Vast.ai offer is only rentable as a 2-GPU bundle.

## Why static

`sdk: static` serves this Space as plain HTML/CSS/JS. There is no container to boot, no Python server to keep alive and no cold-start sleep. The page is the same byte-identical artifact published at `https://gpu.mybskm.top/calculator/`.

## Files

- `index.html` — the complete calculator, styles and vanilla JS.
- `README.md` — this Space card and static SDK metadata.

## Sister tools

All four calculators in this matrix are mirrored as zero-dependency Hugging Face Static Spaces:

1. **This Space** — GPU Fit & Cost Calculator: https://huggingface.co/spaces/600me/llm-gpu-cost-calculator
2. LLM & RAG web-scraping TCO calculator: https://huggingface.co/spaces/600me/rag-web-scraping-cost-calculator
3. Residential proxy sticky-session & `cf_clearance` loss calculator: https://huggingface.co/spaces/600me/residential-proxy-sticky-session-calculator
4. MoR vs US LLC + Stripe breakeven calculator: https://huggingface.co/spaces/600me/ai-saas-stripe-vs-mor-tax-calculator

Main sites: [gpu.mybskm.top](https://gpu.mybskm.top/) · [scrape.mybskm.top](https://scrape.mybskm.top/calculator/) · [proxy.mybskm.top](https://proxy.mybskm.top/calculator/) · [pay.mybskm.top](https://pay.mybskm.top/)

## Disclosure

The RunPod and Vast.ai buttons are affiliate links (`utm_source=gpu_calculator&utm_medium=cta`). We may earn a commission at no additional cost to the visitor. Providers set their own prices, inventory and terms; the calculator is a planning tool, not a quote or a deployment guarantee.
