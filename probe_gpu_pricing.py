#!/usr/bin/env python3
"""Public pricing probe and self-contained static site generator. No credentials."""

import html
import json
import os
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent
TIMEOUT = 10
LINKS = {
    "RunPod": "https://go.272738.xyz/runpod",
    "Vast.ai": "https://go.272738.xyz/vastai",
    "Together.ai": "https://go.272738.xyz/together",
    "OpenRouter": "https://go.272738.xyz/openrouter",
    "DeepInfra": "https://go.272738.xyz/deepinfra",
}
ENDPOINTS = {
    "RunPod": "https://api.runpod.io/graphql",
    "Vast.ai": "https://console.vast.ai/api/v0/bundles/",
    "Together.ai": "https://api.together.xyz/v1/models",
    "OpenRouter": "https://openrouter.ai/api/v1/models",
    "DeepInfra": "https://api.deepinfra.com/models/list",
}
BASELINE_AT = "2026-10-16T00:00:00Z"  # Reference date, not a live observation time.
GPU_TYPES = [
    ("H100 SXM", 80, "NVIDIA H100 80GB HBM3", "H100 SXM"),
    ("H100 PCIe", 80, "NVIDIA H100 PCIe", "H100 PCIE"),
    ("A100 80G SXM", 80, "NVIDIA A100-SXM4-80GB", "A100 SXM4"),
    ("A100 80G PCIe", 80, "NVIDIA A100 80GB PCIe", "A100 PCIE"),
    ("RTX 4090", 24, "NVIDIA GeForce RTX 4090", "RTX 4090"),
]
# RunPod and Vast references were read from their public APIs on the date above.
# Vast references are sampled, verified rentable offers, not guaranteed inventory.
RUNPOD_BASE = {"Community": [2.69, 1.99, 1.39, 1.19, .34],
               "Secure": [3.99, 2.89, 1.79, 1.79, .89]}
VAST_BASE = [3.261, 2.589, 1.068, .802, .401]
LLM_TYPES = {
    "OpenRouter": [
        ("DeepSeek-V3", "deepseek/deepseek-chat", .2574, 1.0287, "Router catalog; provider routing can change"),
        ("DeepSeek-R1", "deepseek/deepseek-r1", .7, 2.5, "Router catalog; provider routing can change"),
        ("Llama-3.3-70B", "meta-llama/llama-3.3-70b-instruct", .1, .32, "Router catalog; provider routing can change"),
    ],
    "DeepInfra": [
        ("DeepSeek-V3", "deepseek-ai/DeepSeek-V3", .32, .89, "Standard uncached catalog rate"),
        ("DeepSeek-R1-0528", "deepseek-ai/DeepSeek-R1-0528", .5, 2.15, "0528 revision; not the original R1 checkpoint"),
        ("Llama-3.3-70B Turbo", "meta-llama/Llama-3.3-70B-Instruct-Turbo", .1, .32, "Turbo FP8 variant"),
    ],
    "Together.ai": [
        ("DeepSeek-V3-0324", "deepseek-ai/DeepSeek-V3", 1.25, 1.25, "Dedicated/reference listing; serverless availability not verified"),
        ("DeepSeek-R1-0528", "deepseek-ai/DeepSeek-R1-0528", None, None, "Not available on Together Serverless; no current token quote"),
        ("Llama-3.3-70B", "meta-llama/Llama-3.3-70B-Instruct-Turbo", 1.04, 1.04, "Public pricing page reference; API authentication required"),
    ],
}
TOGETHER_SOURCES = {
    "DeepSeek-V3-0324": "https://www.together.ai/models/deepseek-v3",
    "DeepSeek-R1-0528": "https://www.together.ai/models/deepseek-r1",
    "Llama-3.3-70B": "https://www.together.ai/pricing",
}


def number(value, multiplier=1, digits=6):
    """Reject missing, boolean, negative and non-finite prices; retain true zero."""
    try:
        if value is None or isinstance(value, bool):
            return None
        value = Decimal(str(value)) * Decimal(str(multiplier))
        if not value.is_finite() or value < 0:
            return None
        return float(value.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, TypeError):
        return None


def baseline():
    gpu, llm = [], []
    for i, (name, ram, runpod_id, vast_id) in enumerate(GPU_TYPES):
        for tier in RUNPOD_BASE:
            gpu.append(dict(provider="RunPod", model=name, vram_gb=ram,
                            tier=tier, model_id=runpod_id, usd_per_hour=RUNPOD_BASE[tier][i],
                            notes=f"{tier} catalog rate; inventory not guaranteed"))
        gpu.append(dict(provider="Vast.ai", model=name, vram_gb=ram,
                        tier="Verified on-demand sample", model_id=vast_id,
                        usd_per_hour=VAST_BASE[i],
                        bundle_gpu_count=2 if name == "RTX 4090" else 1,
                        bundle_usd_per_hour=number(VAST_BASE[i] * (2 if name == "RTX 4090" else 1), digits=3),
                        notes="Sample minimum per GPU; full multi-GPU bundle may be required"))
    for provider, models in LLM_TYPES.items():
        for name, model_id, prompt, completion, note in models:
            llm.append(dict(provider=provider, model=name, model_id=model_id,
                            input_usd_per_1m=prompt, output_usd_per_1m=completion,
                            notes=note))
    for row in gpu + llm:
        row.update(source="baseline", observed_at=None, reference_date=BASELINE_AT,
                   source_url=TOGETHER_SOURCES.get(row["model"], ENDPOINTS[row["provider"]])
                   if row["provider"] == "Together.ai" else ENDPOINTS[row["provider"]],
                   link=LINKS[row["provider"]])
    return {"gpu": gpu, "llm": llm}


def row_key(row):
    return row.get("provider"), row.get("model_id"), row.get("tier", "")


def read_cache():
    try:
        data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
        if data.get("schema_version") == 1:
            return {row_key(r): r for group in ("gpu", "llm")
                    for r in data.get(group, []) if isinstance(r, dict)}
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return {}


def fetch_provider(provider, now):
    """Catch every provider failure locally; return usable rows and public status."""
    rows, status = {}, {"endpoint": ENDPOINTS[provider], "http_status": None}
    try:
        kwargs = {"timeout": TIMEOUT, "headers": {"User-Agent": "Kais-GPU-Pricing/1.0"}}
        method = "GET"
        if provider == "RunPod":
            method = "POST"
            kwargs["json"] = {"query": "{ gpuTypes { id memoryInGb securePrice communityPrice } }"}
        elif provider == "Vast.ai":
            method = "POST"  # Public search only; never creates an instance.
            kwargs["json"] = {"verified": {"eq": True}, "rentable": {"eq": True},
                              "rented": {"eq": False}, "gpu_name": {"in": [g[3] for g in GPU_TYPES]},
                              "type": "on-demand", "limit": 500, "order": [["dph_total", "asc"]]}
        response = requests.request(method, ENDPOINTS[provider], **kwargs)
        status["http_status"] = response.status_code
        response.raise_for_status()
        payload = response.json()
        if provider == "RunPod":
            models = {m["id"]: m for m in payload["data"]["gpuTypes"]}
            for name, ram, model_id, _ in GPU_TYPES:
                item = models.get(model_id, {})
                if number(item.get("memoryInGb")) != ram:
                    continue
                for tier, field in (("Community", "communityPrice"), ("Secure", "securePrice")):
                    price = number(item.get(field), digits=3)
                    if price is not None and price > 0:  # Zero means unavailable in this catalog.
                        rows[(provider, model_id, tier)] = {"usd_per_hour": price}
        elif provider == "Vast.ai":
            for item in payload["offers"]:
                try:
                    model_id = item["gpu_name"]
                    target = next((g for g in GPU_TYPES if g[3] == model_id), None)
                    if target is None or item.get("rentable") is not True or item.get("rented") is not False:
                        continue
                    if item.get("verification") != "verified" or item.get("is_bid") is not False:
                        continue
                    memory = number(item.get("gpu_ram"))
                    # Vast reports MiB; keep 40GB A100 offers out of the 80GB rows.
                    if memory is None or abs(memory / 1024 - target[1]) > 2:
                        continue
                    count, total = number(item.get("num_gpus")), number(item.get("dph_total"), digits=9)
                    if count is None or count < 1 or count != int(count) or total is None or total <= 0:
                        continue
                    price = number(Decimal(str(total)) / Decimal(str(count)), digits=3)
                    key = (provider, model_id, "Verified on-demand sample")
                    if key not in rows or price < rows[key]["usd_per_hour"]:
                        rows[key] = dict(usd_per_hour=price, bundle_gpu_count=int(count),
                                         bundle_usd_per_hour=number(total, digits=3),
                                         notes=f"Lowest sampled verified rentable offer; {int(count)} GPU bundle; storage/network extra")
                except (KeyError, TypeError, ValueError, InvalidOperation):
                    continue
        else:
            items = payload.get("data", []) if provider == "OpenRouter" else payload
            id_field = {"OpenRouter": "id", "DeepInfra": "model_name", "Together.ai": "id"}[provider]
            models = {m[id_field]: m for m in items if isinstance(m, dict) and id_field in m}
            for name, model_id, _, _, _ in LLM_TYPES[provider]:
                item = models.get(model_id, {})
                pricing = item.get("pricing") or {}
                fields, multiplier = ("prompt", "completion"), 1_000_000
                if provider == "DeepInfra":
                    fields, multiplier = ("cents_per_input_token", "cents_per_output_token"), 10_000
                elif provider == "Together.ai":
                    fields, multiplier = ("input", "output"), 1  # Together lists USD / 1M.
                prompt, completion = (number(pricing.get(f), multiplier) for f in fields)
                if prompt is not None and completion is not None:
                    row = dict(input_usd_per_1m=prompt, output_usd_per_1m=completion)
                    if provider == "DeepInfra" and item.get("deprecated"):
                        row["notes"] = "Deprecated catalog entry; availability not verified"
                    rows[(provider, model_id, "")] = row
        status["result"] = "live" if rows else "no usable target quotes; fallback"
    except Exception as exc:
        # Do not store response bodies, credentials, private account data or raw logs.
        status["result"] = f"{type(exc).__name__}; fallback"
    for row in rows.values():
        row.update(source="live", observed_at=now, source_url=ENDPOINTS[provider])
    status["live_rows"] = len(rows)
    return rows, status


def collect(now):
    data = baseline()
    cache = read_cache()
    data.update(schema_version=1, generated_at=now, currency="USD", links=LINKS.copy(), providers={})
    for provider in LINKS:
        live, status = fetch_provider(provider, now)
        data["providers"][provider] = status
        for group, fields in (("gpu", ("usd_per_hour",)),
                              ("llm", ("input_usd_per_1m", "output_usd_per_1m"))):
            for row in data[group]:
                if row["provider"] != provider:
                    continue
                key = row_key(row)
                if key in live:
                    row.update(live[key])
                else:
                    old = cache.get(key, {})
                    # An all-or-nothing row keeps input/output rates from the same quote.
                    if all(number(old.get(f)) is not None for f in fields):
                        row.update({f: number(old[f], digits=3 if group == "gpu" else 6) for f in fields})
                        for field in ("observed_at", "reference_date", "source_url", "notes"):
                            if isinstance(old.get(field), str):
                                row[field] = old[field]
                        for field in ("bundle_gpu_count", "bundle_usd_per_hour"):
                            if number(old.get(field)) is not None:
                                row[field] = number(old[field])
                        row["cached_source"] = old.get("cached_source", old.get("source", "unknown"))
                        row["source"] = "cache"
                    elif not all(number(row.get(f)) is not None for f in fields):
                        row.update({f: None for f in fields})
                        row["source"] = "null"
                row["link"] = LINKS[provider]
                row["fetch_status"] = status["result"]
    for row in data["llm"]:
        a, b = row["input_usd_per_1m"], row["output_usd_per_1m"]
        row["one_m_each_usd"] = number(Decimal(str(a)) + Decimal(str(b))) if a is not None and b is not None else None
        row["example_10m_input_2m_output_usd"] = number(Decimal(str(a))*10 + Decimal(str(b))*2) if a is not None and b is not None else None
    for row in data["gpu"]:
        row["cost_100_gpu_hours_usd"] = number(Decimal(str(row["usd_per_hour"]))*100, digits=3) if row["usd_per_hour"] is not None else None
    return data


def money(value, digits=3):
    return "N/A" if value is None else f"${value:,.{digits}f}"


def evidence(row):
    origin = f" (origin: {row['cached_source']})" if row.get("cached_source") else ""
    return row["source"] + origin + "; " + (row.get("observed_at") or "reference " + row["reference_date"][:10])


def cost_example(data):
    rows = [r for r in data["gpu"] if r["model"] == "H100 SXM" and r["usd_per_hour"] is not None]
    if len(rows) < 2:
        return "A $1/hour price difference costs $100 over 100 GPU-hours. Compare the matrix before launching."
    low, high = min(rows, key=lambda r: r["usd_per_hour"]), max(rows, key=lambda r: r["usd_per_hour"])
    diff = number(Decimal(str(high["usd_per_hour"]))-Decimal(str(low["usd_per_hour"])), digits=3)
    return (f"100 H100 SXM GPU-hours cost {money(low['cost_100_gpu_hours_usd'], 2)} at "
            f"{low['provider']} ({low['tier']}, {low['source']}) versus "
            f"{money(high['cost_100_gpu_hours_usd'], 2)} at {high['provider']} "
            f"({high['tier']}, {high['source']}): a {money(number(Decimal(str(diff))*100), 2)} compute-only gap. "
            "These are quoted rates, not equivalent service guarantees or a reservation.")


def render_readme(data):
    out = ["# Cheapest H100 GPU Cloud & DeepSeek R1 / V3 API Pricing Benchmark (2026)",
           "", "[Live pricing dashboard](https://gpu.mybskm.top/)",
           "", f"Updated: **{data['generated_at']}** · All prices in USD.", "",
           "Stop paying for idle GPUs and expensive output tokens. Compare RunPod vs Vast.ai GPU rates, "
           "then compare Together.ai, OpenRouter and DeepInfra API costs before your next deployment.", "",
           cost_example(data), "",
           "[Launch on RunPod](" + LINKS["RunPod"] + ") · [Find a Vast.ai GPU](" + LINKS["Vast.ai"] + ")", "",
           "## Cheapest H100 GPU cloud: hourly price matrix", "",
           "Compute-only prices per GPU-hour; storage, bandwidth, tax and setup time can add to your bill. "
           "A sampled minimum is not a market-wide cheapest claim. Multi-GPU bundles require the full bundle payment.", "",
           "| Provider / tier | GPU | VRAM | USD / GPU-hour | 100 GPU-hours | Evidence | Launch |",
           "|---|---|---:|---:|---:|---|---|"]
    for r in sorted(data["gpu"], key=lambda r: r["usd_per_hour"] if r["usd_per_hour"] is not None else float("inf")):
        out.append(f"| {r['provider']} / {r['tier']} | {r['model']} | {r['vram_gb']} GB | "
                   f"{money(r['usd_per_hour'])} | {money(r['cost_100_gpu_hours_usd'], 2)} | {evidence(r)} | [Launch]({r['link']}) |")
    out += ["", "## DeepSeek R1 / V3 API pricing benchmark and Llama 3.3 70B", "",
            "Rates below are USD per 1M tokens. A long reasoning answer can erase a cheap input rate: "
            "the example workload uses **10M input + 2M output tokens**, excluding cached-input discounts. "
            "Exact model IDs and revisions are shown; Turbo, 0324 and 0528 variants are not identical checkpoints.", "",
            "| Provider | Model / endpoint | Input / 1M | Output / 1M | Example bill | Evidence | Start |",
            "|---|---|---:|---:|---:|---|---|"]
    for r in data["llm"]:
        out.append(f"| {r['provider']} | {r['model']} (`{r['model_id']}`) | {money(r['input_usd_per_1m'], 6)} | "
                   f"{money(r['output_usd_per_1m'], 6)} | {money(r['example_10m_input_2m_output_usd'], 2)} | {evidence(r)} | [Explore]({r['link']}) |")
    out += ["", "## RunPod vs Vast.ai — choose the bill you can actually sustain", "",
            "| Provider | Billing pitfall to check | Practical next step |",
            "|---|---|---|",
            f"| RunPod | Community and Secure are separate tiers; hourly catalog rates do not reserve inventory. | [Choose your GPU and tier]({LINKS['RunPod']}) |",
            f"| Vast.ai | Host reliability, storage and multi-GPU bundle requirements can outweigh a low sampled unit rate. | [Check the full offer]({LINKS['Vast.ai']}) |",
            f"| Together.ai | Model-page reference rates do not prove serverless availability; R1 is currently unavailable there. | [Check deployment options]({LINKS['Together.ai']}) |",
            f"| OpenRouter | Routing/provider selection can change the effective quote; verify the selected endpoint. | [Compare routed endpoints]({LINKS['OpenRouter']}) |",
            f"| DeepInfra | Compare the exact revision and quantization; output and reasoning tokens drive the bill. | [Choose an inference model]({LINKS['DeepInfra']}) |",
            "", "## Quote details and source transparency", "",
            "Live = public API quote observed this run; cache = previous quote with its original date and origin; "
            "baseline = dated built-in reference, not a refreshed quote; N/A = no usable price. "
            "The page update time is not the quote freshness time. This is a pricing benchmark, not a measured speed, quality or uptime benchmark.", ""]
    for r in data["gpu"] + data["llm"]:
        out.append(f"- **{r['provider']} · {r['model']}**: {r['notes']} ({evidence(r)}). Source: `{r['source_url']}`.")
    out += ["", "## How prices are normalized", "",
            "OpenRouter USD/token × 1,000,000; DeepInfra cents/token × 10,000. "
            "Vast.ai bundle USD/hour ÷ GPU count; GPU rates round to 3 decimals. "
            "Example API bill = input rate × 10 + output rate × 2. No paid inference or GPU rental is performed.", "",
            "Refresh locally with `python3 -m pip install -r requirements.txt` followed by "
            "`python3 probe_gpu_pricing.py`. Each provider request has a 10-second timeout. "
            "Failed or missing quotes fall back to data.json, then the dated baseline, then null. "
            "All three outputs are replaced atomically.", "",
            "Product buttons use fixed outbound relay links. This repository does not verify relay destinations, "
            "affiliate enrollment or commissions; visiting a provider does not purchase compute.", ""]
    out += ['', '## Sister Projects (Matrix Interlinks)', '', '- [Proxy Infrastructure Benchmark](https://proxy.mybskm.top) · [GitHub repository](https://github.com/600me/awesome-residential-proxies-benchmark)', '- [Global GPU Cloud Benchmark](https://gpu.mybskm.top) · [GitHub repository](https://github.com/600me/awesome-gpu-cloud-pricing-benchmark)', '- [Global Payments Matrix](https://pay.mybskm.top) · [GitHub repository](https://github.com/600me/awesome-indie-global-payments-matrix)', '']
    return "\n".join(out)


def render_html(data):
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    nav = " ".join(f'<a href="{url}" rel="noopener noreferrer">{html.escape(name)} ↗</a>' for name, url in LINKS.items())
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cheapest H100 Cloud · RunPod vs Vast.ai · DeepSeek API Pricing 2026</title>
<link rel="canonical" href="https://gpu.mybskm.top/">
<meta property="og:title" content="Cheapest H100 Cloud · RunPod vs Vast.ai · DeepSeek API Pricing 2026">
<meta property="og:description" content="Find the cheapest H100 cloud for your workload. Compare H100, A100 and RTX 4090 hourly quotes, model 100 GPU-hours and explore provider deployment options.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://gpu.mybskm.top/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Cheapest H100 Cloud · RunPod vs Vast.ai · DeepSeek API Pricing 2026">
<meta name="twitter:description" content="Find the cheapest H100 cloud for your workload. Compare H100, A100 and RTX 4090 hourly quotes, model 100 GPU-hours and explore provider deployment options.">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Cheapest H100 Cloud · RunPod vs Vast.ai · DeepSeek API Pricing 2026",
  "url": "https://gpu.mybskm.top/",
  "description": "Find the cheapest H100 cloud for your workload. Compare H100, A100 and RTX 4090 hourly quotes, model 100 GPU-hours and explore provider deployment options.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Any",
  "browserRequirements": "Requires JavaScript for interactive comparisons.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "description": "Free access to this comparison tool; provider services are priced separately."
  },
  "featureList": [
    "H100, A100 and RTX 4090 hourly quote comparison",
    "100 GPU-hour cost estimates",
    "DeepSeek and Llama API token cost comparison"
  ]
}
</script>
<meta name="description" content="Find the cheapest H100 cloud for your workload. Compare H100, A100 and RTX 4090 hourly quotes, model 100 GPU-hours and explore provider deployment options.">
<style>
:root{color-scheme:dark;--bg:#090d14;--panel:#101925;--line:#253246;--muted:#a0afc2;--green:#63f6ba;--ink:#edf5ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 90% 0,#152d31,transparent 45%),var(--bg);color:var(--ink);font:15px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace}main{max-width:1320px;margin:auto;padding:42px 24px}a{color:var(--green)}.eyebrow{color:var(--green);letter-spacing:.15em;font-size:12px}h1{font-family:system-ui,sans-serif;letter-spacing:-.04em;font-size:clamp(32px,5vw,62px);line-height:1.1;max-width:1000px;margin:20px 0}h2{font:600 23px system-ui,sans-serif}.intro{max-width:900px;color:var(--muted)}.callout{background:linear-gradient(100deg,#102a26,#122030);border:1px solid #2b5e50;border-radius:14px;padding:20px;margin:24px 0}.providers{display:flex;gap:10px;flex-wrap:wrap}.providers a,.action{display:inline-block;text-decoration:none;padding:9px 13px;border:1px solid #326b58;border-radius:7px;background:#122b25}.tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:28px 0 14px}button,input,select{font:inherit;color:var(--ink);border:1px solid var(--line);background:var(--panel);border-radius:8px;padding:12px}button{cursor:pointer}button[aria-selected=true]{background:var(--green);color:#06251a}input{flex:1;min-width:200px}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:12px;background:#0d1520}table{width:100%;border-collapse:collapse;min-width:860px}th{text-align:left;font-size:11px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase}th,td{padding:17px 16px;border-bottom:1px solid var(--line);vertical-align:top}tbody tr:hover{background:#152232}small{display:block;color:var(--muted);font-size:11px;max-width:300px;overflow-wrap:anywhere}.price{font-size:20px;color:var(--green);white-space:nowrap}.badge{font-size:11px;color:#eecb87}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:28px 0}.card{padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:12px}.card p,footer{color:var(--muted);font-size:12px}.empty{text-align:center;color:var(--muted)}footer{border-top:1px solid var(--line);padding-top:20px;margin-top:32px}#count{color:var(--muted);font-size:12px}@media(max-width:600px){main{padding:28px 14px}.tools>*{flex:1}select{width:100%}.price{font-size:17px}}
</style></head><body><main>
<div class="eyebrow">GPU / INFERENCE / COST INTELLIGENCE — 2026</div>
<h1>Your next GPU bill<br>starts with a better quote.</h1>
<p class="intro"><a href="https://gpu.mybskm.top/">Live pricing dashboard</a></p>
<p class="intro">Searching for the cheapest H100 GPU cloud? Compare RunPod vs Vast.ai, then check the DeepSeek R1 / V3 API pricing benchmark before paying for idle compute or costly output tokens.</p>
<p class="intro">Snapshot generated <time>__TIME__</time>. Every row labels its quote source and date.</p>
<section class="callout"><strong>Same GPU-hours. Different bill.</strong><p>__EXAMPLE__</p><nav class="providers" aria-label="Provider deployment links">__NAV__</nav></section>
<div class="tools"><div role="tablist" aria-label="Pricing type"><button id="gpu-tab" role="tab" aria-selected="true" aria-controls="pricing">GPU cloud</button> <button id="llm-tab" role="tab" aria-selected="false" aria-controls="pricing">LLM APIs</button></div>
<input id="search" type="search" aria-label="Fuzzy search models or providers" placeholder="Search H100, DeepSeek, RunPod…">
<select id="sort" aria-label="Sort price ascending"><option value="primary">Price ↑ (GPU/hour or input/1M)</option><option value="output">Output / 1M ↑</option><option value="total">Example workload cost ↑</option></select></div>
<p id="count" aria-live="polite"></p><section id="pricing" role="tabpanel" aria-labelledby="gpu-tab" class="tablewrap"><table><thead id="thead"></thead><tbody id="rows"></tbody></table></section>
<p class="intro" id="units"></p><noscript>Enable JavaScript for filtering and sorting. The accompanying README.md contains the full static pricing matrices.</noscript>
<section class="cards">
<article class="card"><h2>RunPod vs Vast.ai</h2><p>Catalog tier and marketplace offer are different purchase conditions. Check GPU count, storage, reliability and availability before launching.</p></article>
<article class="card"><h2>Tokens add up</h2><p>The API example uses 10M input + 2M output tokens. A $1/1M output-rate gap costs $2 on that workload. Reasoning tokens can increase billed output.</p></article>
<article class="card"><h2>Read the exact model</h2><p>0324, 0528 and Turbo are distinct variants. Together R1 is unavailable on Serverless; its missing quote stays N/A. Check current deployment options via the provider buttons.</p></article>
</section><footer>USD quote comparison, not a latency or quality benchmark. Live = API quote this run; cache = earlier quote, retaining origin/date; baseline = dated reference; N/A = unavailable price. Prices exclude tax and variable extras. The lowest sampled rate is not a market-wide guarantee. Fixed relay buttons do not verify destinations, affiliate status or commissions. No rentals or paid inference are performed.<nav aria-label="Sister projects"><a href="https://proxy.mybskm.top">Proxy benchmark</a> · <a href="https://pay.mybskm.top">Payments calculator</a></nav></footer>
</main><script id="snapshot" type="application/json">__DATA__</script><script>
'use strict';
const data=JSON.parse(document.getElementById('snapshot').textContent);
let mode='gpu';
const $=id=>document.getElementById(id);
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const usd=(x,n=3)=>x===null||x===undefined?'N/A':'$'+Number(x).toLocaleString('en-US',{minimumFractionDigits:n,maximumFractionDigits:n});
function fuzzy(text,query){text=text.toLowerCase();return query.toLowerCase().trim().split(/\s+/).every(word=>{let i=0;for(const c of text){if(c===word[i])i++;}return i===word.length;});}
function priceKey(){if(mode==='gpu')return $('sort').value==='total'?'cost_100_gpu_hours_usd':'usd_per_hour';return {primary:'input_usd_per_1m',output:'output_usd_per_1m',total:'example_10m_input_2m_output_usd'}[$('sort').value];}
function render(){
 const key=priceKey(), q=$('search').value;
 const rows=data[mode].filter(r=>fuzzy([r.provider,r.model,r.model_id,r.tier||'',r.vram_gb?`${r.vram_gb}GB`:''].join(' '),q)).slice().sort((a,b)=>(a[key]??Infinity)-(b[key]??Infinity));
 $('count').textContent=`${rows.length} quotes · ${mode==='gpu'?'per GPU-hour':'per 1M tokens'} · missing prices sort last`;
 const heads=mode==='gpu'?['Provider / tier','GPU / memory','USD / GPU-hour','100 GPU-hours','Evidence / date','Launch']:['Provider','Model / endpoint','Input / 1M','Output / 1M','10M input + 2M output','Evidence / start'];
 $('thead').innerHTML='<tr>'+heads.map(x=>'<th scope="col">'+esc(x)+'</th>').join('')+'</tr>';
 $('rows').innerHTML=rows.map(r=>{
  const proof=`<span class="badge">${esc(r.source)}${r.cached_source?' · origin '+esc(r.cached_source):''}</span><small>${esc(r.observed_at||'Reference '+r.reference_date.slice(0,10))}</small>`;
  const link=`<a class="action" href="${esc(data.links[r.provider])}" rel="noopener noreferrer">${mode==='gpu'?'Launch GPU':'Explore API'} ↗</a>`;
  const provider=`<strong>${esc(r.provider)}</strong><small>${esc(r.tier||'Token billing')}</small>`;
  const cells=mode==='gpu'?[provider,`<strong>${esc(r.model)}</strong><small>${esc(r.vram_gb)} GB VRAM</small><small>${esc(r.notes)}</small>`,`<span class="price">${usd(r.usd_per_hour)}</span>${r.bundle_gpu_count?'<small>Full '+esc(r.bundle_gpu_count)+' GPU bundle: '+usd(r.bundle_usd_per_hour)+'/hour</small>':''}`,usd(r.cost_100_gpu_hours_usd,2),proof,link]:[provider,`<strong>${esc(r.model)}</strong><small>${esc(r.model_id)}</small><small>${esc(r.notes)}</small>`,`<span class="price">${usd(r.input_usd_per_1m,6)}</span>`,usd(r.output_usd_per_1m,6),usd(r.example_10m_input_2m_output_usd,2),proof+'<br>'+link];
  return '<tr>'+cells.map(c=>'<td>'+c+'</td>').join('')+'</tr>';
 }).join('')||'<tr><td class="empty" colspan="6">No matching quotes. Try another model or provider.</td></tr>';
 $('units').textContent=mode==='gpu'?'Compute-only USD per GPU-hour. Multi-GPU offers require the full bundle; storage and networking are extra. Inventory is not reserved.':'USD per 1M tokens; standard uncached rates. The example bill is input rate × 10 + output rate × 2. N/A is never treated as free.';
}
for(const next of ['gpu','llm'])$(next+'-tab').addEventListener('click',()=>{mode=next;for(const m of ['gpu','llm'])$(m+'-tab').setAttribute('aria-selected',String(m===mode));$('pricing').setAttribute('aria-labelledby',next+'-tab');render();});
$('search').addEventListener('input',render);$('sort').addEventListener('change',render);render();
</script></body></html>'''
    return (template.replace("__TIME__", html.escape(data["generated_at"]))
            .replace("__EXAMPLE__", html.escape(cost_example(data)))
            .replace("__NAV__", nav).replace("__DATA__", payload))


def atomic_write(path, content):
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="." + path.name + ".", suffix=".tmp", delete=False) as handle:
            name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    data = collect(now)
    # Render all outputs before replacing any file.
    outputs = {"data.json": json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
               "README.md": render_readme(data), "index.html": render_html(data)}
    for name, content in outputs.items():
        atomic_write(ROOT / name, content)
    print(f"Generated {len(data['gpu'])} GPU and {len(data['llm'])} LLM quotes at {now}")
    for provider, status in data["providers"].items():
        print(f"{provider}: HTTP {status['http_status']}, {status['result']}, {status['live_rows']} live rows")
    for name in outputs:
        print(f"{name}: {(ROOT / name).stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
