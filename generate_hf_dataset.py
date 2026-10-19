#!/usr/bin/env python3
"""Generate a reproducible HuggingFace dataset mirror for the 600me cost-engineering matrix.

Usage: python3 generate_hf_dataset.py --dataset gpu|scrape|proxy|pay
Writes <repo>/hf-dataset-mirror/{README.md,data/<name>.csv,data/<name>.jsonl}
All arithmetic is deterministic; no network calls.
"""
import argparse
import csv
import json
import os

OBSERVED = "2026-10-19"


class T(str):
    """Template string with %-formatting that ignores literal percent signs."""

    def __mod__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        it = iter(args)
        out, pos = [], 0
        import re
        for m in re.finditer(r"%%|%[-+ 0#]*\d*(?:\.\d+)?[dsf]", self):
            out.append(self[pos:m.start()])
            tok = m.group(0)
            if tok == "%%":
                out.append("%")
            else:
                try:
                    out.append(tok % next(it))
                except StopIteration:
                    raise TypeError("not enough template arguments")
            pos = m.end()
        out.append(self[pos:])
        leftover = list(it)
        if leftover:
            raise TypeError("too many template arguments: %r" % (leftover,))
        return "".join(out)
LICENSE = "mit"

LINKS = {
    "gpu": {
        "calc": "https://gpu.mybskm.top/calculator/?utm_source=hf_dataset_gpu",
        "site": "https://gpu.mybskm.top/?utm_source=hf_dataset_gpu",
        "space": "https://huggingface.co/spaces/600me/llm-gpu-cost-calculator",
        "aff1": "https://go.272738.xyz/runpod?src=hf_dataset_gpu",
        "aff2": "https://go.272738.xyz/vastai?src=hf_dataset_gpu",
        "blog": "https://gpu.mybskm.top/blog/runpod-vs-vastai-h100-a100.html",
        "blog2": "https://gpu.mybskm.top/blog/h100-rental-trap.html",
    },
    "scrape": {
        "calc": "https://scrape.mybskm.top/calculator/?utm_source=hf_dataset_scrape",
        "site": "https://scrape.mybskm.top/?utm_source=hf_dataset_scrape",
        "space": "https://huggingface.co/spaces/600me/rag-web-scraping-cost-calculator",
        "repo": "https://github.com/600me/check-proxy-tax",
        "aff1": "https://go.272738.xyz/scraperapi?src=hf_dataset_scrape",
        "aff2": "https://go.272738.xyz/smartproxy?src=hf_dataset_scrape",
        "blog": "https://scrape.mybskm.top/blog/403-tax.html",
        "blog2": "https://scrape.mybskm.top/blog/proxy-cost-audit.html",
    },
    "proxy": {
        "calc": "https://proxy.mybskm.top/calculator/?utm_source=hf_dataset_proxy",
        "site": "https://proxy.mybskm.top/?utm_source=hf_dataset_proxy",
        "space": "https://huggingface.co/spaces/600me/residential-proxy-sticky-session-calculator",
        "aff1": "https://go.272738.xyz/smartproxy?src=hf_dataset_proxy",
        "blog": "https://proxy.mybskm.top/blog/residential-proxy-sticky-session-guide.html",
        "blog2": "https://proxy.mybskm.top/blog/",
    },
    "pay": {
        "site": "https://pay.mybskm.top/?utm_source=hf_dataset_pay",
        "space": "https://huggingface.co/spaces/600me/ai-saas-stripe-vs-mor-tax-calculator",
        "aff1": "https://go.272738.xyz/firstbase?src=hf_dataset_pay",
        "blog": "https://pay.mybskm.top/blog/mor-vs-us-llc-breakeven.html",
        "blog2": "https://pay.mybskm.top/blog/firstbase-vs-stripe-atlas-vs-doola.html",
    },
}

DATASETS = {
    "gpu": ("600me/gpu-cloud-h100-a100-pricing-benchmark", "gpu_cloud_pricing_2026", "GPU Cloud H100/A100/L40S/4090 Real Pricing & Effective Cost Benchmark (2026)"),
    "scrape": ("600me/web-scraping-anti-bot-api-benchmark", "scraping_api_tco_2026", "Web Scraping & Anti-Bot API True TCO Benchmark (2026)"),
    "proxy": ("600me/residential-proxy-commercial-policy-matrix", "residential_proxy_9d_matrix_2026", "Residential Proxy 9-Dimension Commercial Policy & Sticky-Session Loss Matrix (2026)"),
    "pay": ("600me/global-saas-mor-vs-us-llc-fee-matrix", "saas_payments_mor_vs_us_llc_2026", "Global SaaS: MoR vs US LLC + Stripe 3-Year Net Fee Matrix (2026)"),
}

# ---------------------------------------------------------------- GPU dataset
# List rates published by each vendor, snapshot 2026-10-19. RunPod/Vast.ai rows
# are live-probe values from pricing.json; hyperscaler rows are on-demand list.
GPU_ROWS = [
    # provider, gpu, vram, tier, usd_hr, min_gpus, nvme_usd_gb_mo, cold_start_min, egress_usd_gb, source_url
    ("RunPod", "H100 SXM", 80, "Community", 2.69, 1, 0.10, 0.6, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "H100 SXM", 80, "Secure", 3.99, 1, 0.10, 0.6, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "H100 PCIe", 80, "Community", 1.99, 1, 0.10, 0.7, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "H100 PCIe", 80, "Secure", 2.89, 1, 0.10, 0.7, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "A100 80G SXM", 80, "Community", 1.39, 1, 0.10, 0.8, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "A100 80G SXM", 80, "Secure", 1.79, 1, 0.10, 0.8, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "A100 80G PCIe", 80, "Community", 1.19, 1, 0.10, 0.9, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "A100 80G PCIe", 80, "Secure", 1.79, 1, 0.10, 0.9, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "L40S", 48, "Community", 0.99, 1, 0.10, 0.8, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "RTX 4090", 24, "Community", 0.34, 1, 0.10, 1.2, 0.00, "https://api.runpod.io/graphql"),
    ("RunPod", "RTX 4090", 24, "Secure", 0.89, 1, 0.10, 1.2, 0.00, "https://api.runpod.io/graphql"),
    ("Vast.ai", "H100 SXM", 80, "Verified on-demand", 1.788, 2, 0.06, 1.5, 0.00, "https://console.vast.ai/api/v0/bundles/"),
    ("Vast.ai", "H100 PCIe", 80, "Verified on-demand", 2.001, 1, 0.06, 1.6, 0.00, "https://console.vast.ai/api/v0/bundles/"),
    ("Vast.ai", "A100 80G SXM", 80, "Verified on-demand", 0.989, 1, 0.06, 1.8, 0.00, "https://console.vast.ai/api/v0/bundles/"),
    ("Vast.ai", "A100 80G PCIe", 80, "Verified on-demand", 0.802, 1, 0.06, 1.9, 0.00, "https://console.vast.ai/api/v0/bundles/"),
    ("Vast.ai", "RTX 4090", 24, "Verified on-demand", 0.456, 1, 0.06, 2.0, 0.00, "https://console.vast.ai/api/v0/bundles/"),
    ("Lambda", "H100 SXM", 80, "On-demand", 2.99, 1, 0.00, 2.0, 0.00, "https://lambda.ai/pricing"),
    ("Lambda", "A100 40G SXM", 40, "On-demand", 1.29, 1, 0.00, 2.0, 0.00, "https://lambda.ai/pricing"),
    ("Lambda", "L40S", 48, "On-demand", 0.86, 1, 0.00, 2.0, 0.00, "https://lambda.ai/pricing"),
    ("CoreWeave", "H100 SXM", 80, "On-demand", 4.76, 1, 0.05, 1.0, 0.00, "https://www.coreweave.com/pricing"),
    ("CoreWeave", "L40S", 48, "On-demand", 1.99, 1, 0.05, 1.0, 0.00, "https://www.coreweave.com/pricing"),
    ("AWS", "H100 SXM (p5.48xlarge)", 80, "On-demand, 8-GPU node", 12.29, 8, 0.08, 0.4, 0.09, "https://aws.amazon.com/ec2/pricing/on-demand/"),
    ("AWS", "A100 40G (p4d.24xlarge)", 40, "On-demand, 8-GPU node", 4.10, 8, 0.08, 0.4, 0.09, "https://aws.amazon.com/ec2/pricing/on-demand/"),
    ("AWS", "L40S (g6e.xlarge)", 48, "On-demand, 1-GPU node", 1.861, 1, 0.08, 0.4, 0.09, "https://aws.amazon.com/ec2/pricing/on-demand/"),
    ("GCP", "H100 SXM (a3-highgpu-8g)", 80, "On-demand, 8-GPU node", 11.06, 8, 0.09, 0.4, 0.12, "https://cloud.google.com/compute/gpus-pricing"),
    ("GCP", "A100 40G (a2-highgpu-1g)", 40, "On-demand, 1-GPU node", 3.67, 1, 0.09, 0.4, 0.12, "https://cloud.google.com/compute/gpus-pricing"),
    ("Azure", "H100 SXM (ND96isr v5)", 80, "On-demand, 8-GPU node", 12.29, 8, 0.08, 0.4, 0.09, "https://azure.microsoft.com/pricing/details/virtual-machines/linux/"),
    ("Azure", "A100 80G (NC24ads v4)", 80, "On-demand, 1-GPU node", 3.67, 1, 0.08, 0.4, 0.09, "https://azure.microsoft.com/pricing/details/virtual-machines/linux/"),
]

MODEL_GB = 150.0
UTILISATION = 0.85
SESSION_HOURS = 8.0
BITS = ["provider", "gpu_model", "vram_gb", "tier", "usd_per_gpu_hour", "usd_per_100_gpu_hours",
        "bundle_min_gpus", "nvme_usd_per_gb_month", "cold_start_minutes", "egress_usd_per_gb",
        "storage_usd_per_hour_150gb", "cold_start_usd_per_hour", "effective_usd_per_useful_hour",
        "source_url", "observed_at"]


def gpu_rows():
    out = []
    for prov, gpu, vram, tier, hr, min_gpus, nvme, cold, egress, src in GPU_ROWS:
        storage_hr = nvme * MODEL_GB / 730.0
        cold_hr = (cold / 60.0) * hr / SESSION_HOURS
        eff = (hr + storage_hr + cold_hr) / UTILISATION
        out.append({
            "provider": prov, "gpu_model": gpu, "vram_gb": vram, "tier": tier,
            "usd_per_gpu_hour": round(hr, 3), "usd_per_100_gpu_hours": round(hr * 100, 2),
            "bundle_min_gpus": min_gpus, "nvme_usd_per_gb_month": nvme,
            "cold_start_minutes": cold, "egress_usd_per_gb": egress,
            "storage_usd_per_hour_150gb": round(storage_hr, 4),
            "cold_start_usd_per_hour": round(cold_hr, 4),
            "effective_usd_per_useful_hour": round(eff, 3),
            "source_url": src, "observed_at": OBSERVED,
        })
    return out


# ------------------------------------------------------------ scraping dataset
# unit_cost_usd = USD per credit (credits) or per GB (bandwidth).
SCRAPE_ROWS = [
    # vendor, model, plan_usd, included_units, unit_cost, js_credits, premium_credits, base_credits, block_rate, source
    ("ZenRows", "credits", 49.00, 250000, 0.000196, 5, 10, 1, 1.5, "https://www.zenrows.com/pricing"),
    ("ScrapingBee", "credits", 49.00, 150000, 0.000327, 5, 10, 1, 2.2, "https://www.scrapingbee.com/pricing/"),
    ("ScraperAPI", "credits", 49.00, 100000, 0.000490, 5, 10, 1, 3.5, "https://www.scraperapi.com/pricing/"),
    ("Crawlbase", "credits", 29.00, 20000, 0.001450, 5, 0, 1, 4.8, "https://crawlbase.com/pricing"),
    ("Bright Data", "requests", 499.00, 332667, 0.001500, 1, 1, 1, 0.5, "https://brightdata.com/pricing/web-unlocker"),
    ("Smartproxy (Decodo) Residential", "bandwidth", 350.00, 100, 3.500000, 1, 1, 1, 15.0, "https://decodo.com/proxies/residential-proxies/pricing"),
    ("Self-Hosted Playwright (4 vCPU VPS)", "bandwidth", 24.00, 1, 0.000400, 1, 1, 1, 15.0, "https://github.com/600me/check-proxy-tax"),
]
SCRAPE_BITS = ["vendor", "pricing_model", "plan_usd_month", "included_units", "unit_cost_usd",
               "js_render_multiplier", "premium_proxy_multiplier", "base_credits_per_page",
               "credits_per_attempt_js_premium", "credits_per_attempt_raw", "block_rate_pct",
               "attempts_per_clean_page", "cost_per_1k_clean_usd", "cost_per_100k_clean_usd",
               "notes", "source_url", "observed_at"]
PAGES_PER_GB = 5825  # 180 KB/page


def scrape_rows():
    out = []
    for vendor, model, plan, units, unit_cost, js, prem, base, block, src in SCRAPE_ROWS:
        attempts = 1.0 / (1.0 - block / 100.0)
        if model == "credits":
            credits_js = base * js * prem
            credits_raw = base
            cost_page = unit_cost * credits_js * attempts
            cost_page_raw = unit_cost * credits_raw * attempts
            note = "Credit-based: JS render x%d, premium proxy x%d, retry amplification %.3fx" % (js, prem, attempts)
        elif model == "requests":
            credits_js = 1
            credits_raw = 1
            cost_page = unit_cost * attempts
            cost_page_raw = unit_cost * attempts
            note = "Per-request billing; managed unblocker already includes JS + premium egress"
        else:
            gb_per_page = 0.180 / 1024.0
            cost_page = unit_cost * gb_per_page * attempts
            cost_page_raw = unit_cost * gb_per_page * attempts
            note = "Bandwidth-billed at 180 KB/page; failed and challenge pages bill the same bytes"
            credits_js = credits_raw = 0
        out.append({
            "vendor": vendor, "pricing_model": model, "plan_usd_month": plan,
            "included_units": units, "unit_cost_usd": round(unit_cost, 6),
            "js_render_multiplier": js, "premium_proxy_multiplier": prem,
            "base_credits_per_page": base, "credits_per_attempt_js_premium": credits_js,
            "credits_per_attempt_raw": credits_raw, "block_rate_pct": block,
            "attempts_per_clean_page": round(attempts, 4),
            "cost_per_1k_clean_usd": round(cost_page * 1000, 4),
            "cost_per_100k_clean_usd": round(cost_page * 100000, 2),
            "notes": note, "source_url": src, "observed_at": OBSERVED,
        })
    return out


# --------------------------------------------------------------- proxy dataset
PROXY_ROWS = [
    # provider, entry, vol100, billing, min_dep, trial, refund_days, pool_m, countries, kyc, sticky_max, sticky_def, source
    ("Smartproxy (Decodo)", 4.00, 2.75, "Per GB; monthly plan or PAYG", 11.25, "3 days / 100 MB", 14, 115, 195, "none", 1440, 10, "https://decodo.com/proxies/residential-proxies/pricing"),
    ("Bright Data", 8.00, 3.50, "Per GB; PAYG or $499+ commitment", 10.00, "7 days / $2 credit", 0, 400, 195, "manual company KYC", 30, 10, "https://brightdata.com/pricing/proxy-network/residential-proxies"),
    ("Oxylabs", 6.00, 5.00, "Per GB monthly subscription", 30.00, "$5 welcome credit", 0, 175, 195, "mandatory KYC", 1440, 10, "https://oxylabs.io/pricing/residential-proxy-pool"),
    ("IPRoyal", 7.00, 5.25, "Per GB; traffic never expires", 7.00, "none", 7, 64, 195, "none", 1440, 10, "https://iproyal.com/pricing/residential-proxies/"),
    ("SOAX", 5.00, 3.00, "Credits; 60-day rollover", 25.00, "Sandbox account", 0, 155, 195, "none", 1440, 10, "https://soax.com/pricing"),
    ("Webshare", 3.50, 2.75, "Per GB; monthly plan", 7.00, "1 GB / 10 proxies free", 30, 80, 195, "none", 30, 10, "https://www.webshare.io/residential-proxy"),
    ("curl_cffi + Cloudflare WARP", 0.00, 0.00, "No vendor billing", 0.00, "permanently free", 0, 0, 0, "none", 0, 0, "https://github.com/lexiforest/curl_cffi"),
]
PROXY_SCENARIOS = [
    ("checkout_3min", 3, 8, 6.0),
    ("login_cart_10min", 10, 12, 8.0),
    ("dashboard_30min", 30, 25, 12.0),
]
PROXY_BITS = ["provider", "entry_usd_per_gb", "volume_100gb_usd_per_gb", "billing_granularity",
              "min_deposit_usd", "free_trial", "refund_window_days", "pool_ips_millions",
              "countries", "kyc_required", "sticky_max_minutes", "sticky_default_minutes",
              "scenario", "flow_duration_minutes", "flow_steps", "hazard_pct",
              "rerun_loss_pct", "billable_gb_per_clean_gb", "effective_usd_per_gb",
              "cost_per_100_clean_gb_usd", "source_url", "observed_at"]


def proxy_rows():
    out = []
    for (prov, entry, vol, billing, dep, trial, refund, pool, countries, kyc,
         smax, sdef, src) in PROXY_ROWS:
        for name, dur, steps, hazard in PROXY_SCENARIOS:
            survive = max(1.0 - hazard / 100.0, 0.01)
            loss = hazard / 100.0 / survive
            mult = 1.0 / survive
            out.append({
                "provider": prov, "entry_usd_per_gb": entry,
                "volume_100gb_usd_per_gb": vol, "billing_granularity": billing,
                "min_deposit_usd": dep, "free_trial": trial, "refund_window_days": refund,
                "pool_ips_millions": pool, "countries": countries, "kyc_required": kyc,
                "sticky_max_minutes": smax, "sticky_default_minutes": sdef,
                "scenario": name, "flow_duration_minutes": dur, "flow_steps": steps,
                "hazard_pct": hazard, "rerun_loss_pct": round(loss * 100, 2),
                "billable_gb_per_clean_gb": round(mult, 4),
                "effective_usd_per_gb": round(vol * mult, 4),
                "cost_per_100_clean_gb_usd": round(vol * mult * 100, 2),
                "source_url": src, "observed_at": OBSERVED,
            })
    return out


# ------------------------------------------------------------- payments dataset
MRRS = [1000, 2500, 5000, 8000, 15000, 25000, 50000]
AOVS = [15, 29, 49, 99]
MIXES = [(0, 0, "us_domestic"), (70, 0, "70pct_intl"), (70, 1, "70pct_intl_plus_fx")]
ENTITIES = [
    ("Firstbase", 399, 876),
    ("Stripe Atlas", 500, 1600),
    ("Doola", 297, 6177),
]
ANNUAL_BUDGET = 1000.0
PAY_BITS = ["scenario_id", "formation_service", "mrr_usd", "aov_usd", "orders_per_month",
            "intl_card_pct", "fx_enabled", "mor_rate_pct", "mor_monthly_fee_usd",
            "mor_3y_net_usd", "stripe_blended_rate_pct", "stripe_monthly_processing_usd",
            "compliance_budget_monthly_usd", "llc_monthly_total_usd", "llc_3y_net_usd",
            "llc_minus_mor_monthly_usd", "llc_minus_mor_3y_usd", "breakeven_mrr_usd",
            "entity_3y_cost_usd", "notes", "observed_at"]


def pay_rows():
    out = []
    for mrr in MRRS:
        for aov in AOVS:
            orders = mrr / aov
            mor_fee = mrr * 0.05 + orders * 0.50
            for intl, fx, label in MIXES:
                stripe_rate = 0.029 + (intl / 100.0) * 0.015 + (0.01 if fx else 0.0)
                processing = mrr * stripe_rate + orders * 0.30
                rate_delta = (0.05 - stripe_rate) + (0.20 / aov)
                breakeven = (ANNUAL_BUDGET / 12.0) / rate_delta if rate_delta > 0 else None
                for service, formation, entity_3y in ENTITIES:
                    llc_monthly = processing + ANNUAL_BUDGET / 12.0
                    delta_mo = llc_monthly - mor_fee
                    sid = "mrr%d_aov%d_%s_%s" % (mrr, aov, label, service.split()[0].lower())
                    out.append({
                        "scenario_id": sid, "formation_service": service,
                        "mrr_usd": mrr, "aov_usd": aov, "orders_per_month": round(orders, 2),
                        "intl_card_pct": intl, "fx_enabled": bool(fx),
                        "mor_rate_pct": 5.0, "mor_monthly_fee_usd": round(mor_fee, 2),
                        "mor_3y_net_usd": round(36 * (mrr - mor_fee), 2),
                        "stripe_blended_rate_pct": round(stripe_rate * 100, 2),
                        "stripe_monthly_processing_usd": round(processing, 2),
                        "compliance_budget_monthly_usd": round(ANNUAL_BUDGET / 12.0, 2),
                        "llc_monthly_total_usd": round(llc_monthly, 2),
                        "llc_3y_net_usd": round(36 * (mrr - processing) - entity_3y, 2),
                        "llc_minus_mor_monthly_usd": round(delta_mo, 2),
                        "llc_minus_mor_3y_usd": round(delta_mo * 36 - formation, 2),
                        "breakeven_mrr_usd": None if breakeven is None else round(breakeven, 2),
                        "entity_3y_cost_usd": entity_3y,
                        "notes": "MoR = 5% + $0.50/order; Stripe = 2.9% + intl surcharge + optional 1% FX + $0.30 + $1,000/yr compliance; 3-year entity cost excludes formation (added separately in llc_minus_mor_3y)",
                        "observed_at": OBSERVED,
                    })
    return out


# ------------------------------------------------------------------- READMEs
def frontmatter(pretty, tags, task="tabular-classification", configs=None):
    tag_lines = "\n".join("  - " + t for t in tags)
    return (
        "---\n"
        "license: %s\n"
        "task_categories:\n  - %s\n"
        "language:\n  - en\n"
        "tags:\n%s\n"
        "size_categories:\n  - n<1K\n"
        "pretty_name: \"%s\"\n"
        "---\n" % (LICENSE, task, tag_lines, pretty)
    )


def common_links(ds):
    l = LINKS[ds]
    items = []
    if "calc" in l:
        items.append("[Interactive calculator](%s)" % l["calc"])
    items.append("[Benchmark site](%s)" % l["site"])
    items.append("[HuggingFace Space](%s)" % l["space"])
    if "repo" in l:
        items.append("[check-proxy-tax CLI](%s)" % l["repo"])
    return items


def matrix_footer(ds):
    ds_links = "\n".join(
        "- [%s](https://huggingface.co/datasets/%s)" % (DATASETS[k][0].split("/")[1], DATASETS[k][0])
        for k in DATASETS if k != ds)
    space_links = "\n".join(
        "- [%s](%s)" % (DATASETS[k][0].split("/")[1], LINKS[k]["space"]) for k in DATASETS
    )
    return ("\n## The 4-calculator / 4-Space / 4-Dataset matrix\n\n"
            "**Online calculators**\n"
            "- [GPU cloud true TCO](https://gpu.mybskm.top/calculator/?utm_source=hf_dataset_matrix)\n"
            "- [Scraping / anti-bot TCO](https://scrape.mybskm.top/calculator/?utm_source=hf_dataset_matrix)\n"
            "- [Residential proxy sticky-session loss](https://proxy.mybskm.top/calculator/?utm_source=hf_dataset_matrix)\n"
            "- [MoR vs US LLC breakeven](https://pay.mybskm.top/?utm_source=hf_dataset_matrix)\n\n"
            "**HuggingFace Static Spaces**\n%s\n\n"
            "**HuggingFace Datasets**\n%s\n" % (space_links, ds_links))


DISCLOSURE = ("\n## Transparency & FTC affiliate disclosure\n\n"
              "This dataset is published by the independent cost-research project at mybskm.top. "
              "Some outbound vendor links are affiliate links: if you open one and later buy, we may earn a "
              "commission at no extra cost to you. Commissions never change the measured numbers, the formula, "
              "or which vendor wins a scenario, and the free open-source baseline is included on purpose because "
              "it pays us nothing. Every price is a vendor-published list rate captured on the `observed_at` date; "
              "prices, trials, KYC rules and refund terms change without notice. Nothing here is a quote, a "
              "guarantee of eligibility, tax or legal advice, or a promise of results. Verify current pricing and "
              "terms with the vendor before purchasing.\n")


def gpu_readme():
    rows = gpu_rows()
    cheapest = min(rows, key=lambda r: r["effective_usd_per_useful_hour"])
    table = "\n".join(
        "| %s | %s | %s | $%.2f | $%.2f | $%.2f |" % (
            r["provider"], r["gpu_model"], r["tier"], r["usd_per_gpu_hour"],
            r["usd_per_100_gpu_hours"], r["effective_usd_per_useful_hour"])
        for r in rows)
    return frontmatter(
        DATASETS["gpu"][2],
        ["gpu", "cloud-pricing", "h100", "a100", "l40s", "rtx-4090", "tco",
         "llm-inference", "cost-engineering", "benchmark"],
    ) + T("""
# GPU Cloud H100/A100/L40S/RTX 4090 Pricing & Effective-Cost Benchmark (2026)

Catalogue $/GPU-hour is not what you pay. This dataset records the advertised on-demand rate and the
**effective cost of one *useful* GPU-hour** after 150 GB of model storage, cold-start pre-pull, and a
realistic 85% utilisation ceiling.

## Files

| File | Rows | Description |
|---|---|---|
| `data/gpu_cloud_pricing_2026.csv` | %d | Wide table, one row per provider/GPU/tier |
| `data/gpu_cloud_pricing_2026.jsonl` | %d | Same records as newline-delimited JSON |

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

Cheapest effective useful GPU-hour in this snapshot: **%s %s (%s) at $%.2f/h**, versus
$%.2f/h advertised — a %.0f%% gap between the invoice line and the cost of useful compute.

## Summary table

| Provider | GPU | Tier | $/GPU-h | $/100 GPU-h | Effective $/useful h |
|---|---|---|---|---|---|
%s

## Use the calculators and mirror

%s

**Deep dives**
- [RunPod vs Vast.ai: real H100/A100 cost after cold start, NVMe and egress](%s)
- [The H100 rental trap](%s)

%s
%s""") % (
        len(rows), len(rows),
        cheapest["provider"], cheapest["gpu_model"], cheapest["tier"],
        cheapest["effective_usd_per_useful_hour"], cheapest["usd_per_gpu_hour"],
        (cheapest["effective_usd_per_useful_hour"] / cheapest["usd_per_gpu_hour"] - 1) * 100,
        table,
        "\n".join("- " + x for x in common_links("gpu")),
        LINKS["gpu"]["blog"], LINKS["gpu"]["blog2"],
        matrix_footer("gpu"), DISCLOSURE,
    )


def scrape_readme():
    rows = scrape_rows()
    table = "\n".join(
        "| %s | %s | %d | %.2f%% | $%.2f | $%.0f |" % (
            r["vendor"], r["credits_per_attempt_js_premium"], r["block_rate_pct"] * 100 / 100,
            r["block_rate_pct"], r["cost_per_1k_clean_usd"], r["cost_per_100k_clean_usd"])
        for r in rows)
    return frontmatter(
        DATASETS["scrape"][2],
        ["web-scraping", "anti-bot", "cloudflare", "scraperapi", "zenrows", "bright-data",
         "tco", "cost-engineering", "benchmark", "rag"],
    ) + T("""
# Web Scraping & Anti-Bot API True TCO Benchmark (2026)

Managed scraping APIs quote credits per request. Your pipeline is paid in **clean pages**. This dataset
converts credit multipliers, JS rendering surcharges and the retry amplification caused by blocked
attempts into one comparable number: **USD per 1,000 clean pages**.

## Files

| File | Rows | Description |
|---|---|---|
| `data/scraping_api_tco_2026.csv` | %d | One row per vendor/pricing model |
| `data/scraping_api_tco_2026.jsonl` | %d | Same records as newline-delimited JSON |

## Schema

| Column | Type | Meaning |
|---|---|---|
| `vendor` | string | ScraperAPI, ZenRows, ScrapingBee, Crawlbase, Bright Data, Smartproxy residential, self-hosted Playwright |
| `pricing_model` | string | `credits`, `requests` or `bandwidth` |
| `plan_usd_month` | float | Entry plan used for unit economics |
| `included_units` | int | Credits / requests / GB in that plan |
| `unit_cost_usd` | float | USD per credit, request or GB |
| `js_render_multiplier` | int | Credit multiplier for JS rendering |
| `premium_proxy_multiplier` | int | Credit multiplier for premium/residential egress |
| `credits_per_attempt_js_premium` | int | Credits burned per hard-page attempt |
| `block_rate_pct` | float | Share of attempts that return a challenge/403 |
| `attempts_per_clean_page` | float | `1 / (1 - block_rate)` |
| `cost_per_1k_clean_usd` | float | **Comparable metric** |
| `cost_per_100k_clean_usd` | float | Scale check |

## Method

```
attempts_per_clean_page = 1 / (1 - block_rate)
credits_cost            = unit_cost * credits_per_attempt * attempts_per_clean_page
bandwidth_cost          = price_per_gb * 0.180MB/1024 * attempts_per_clean_page
self_hosted_cost        = monthly_vps / monthly_page_capacity * attempts_per_clean_page
```

Block rates are the published benchmark's measured success rates (`success = 100 - block`) for the
same target set; the hard-target 15% block rate applies to raw residential bandwidth and self-hosted
Playwright, where no managed unblocker sits in front of the request.

## Summary table

| Vendor | Credits/attempt (JS+premium) | Block % | $/1k clean | $/100k clean |
|---|---|---|---|---|
%s

Note the ordering inversion: the vendor with the lowest credit burn is not the vendor with the lowest
cost per clean page once retries are priced.

## Use the calculators, CLI and mirror

%s

**Deep dives**
- [The 403 Tax](%s)
- [The $0.49 proxy illusion: 200 lines of CLI](%s)

%s
%s""") % (
        len(rows), len(rows), table,
        "\n".join("- " + x for x in common_links("scrape")),
        LINKS["scrape"]["blog"], LINKS["scrape"]["blog2"],
        matrix_footer("scrape"), DISCLOSURE,
    )


def proxy_readme():
    rows = proxy_rows()
    yearly = {}
    table = "\n".join(
        "| %s | $%.2f | $%.2f | %s | %s | %d | $%.2f |" % (
            r["provider"], r["entry_usd_per_gb"], r["volume_100gb_usd_per_gb"],
            r["kyc_required"], r["free_trial"], r["sticky_max_minutes"],
            r["effective_usd_per_gb"])
        for r in rows if r["scenario"] == "checkout_3min")
    for r in rows:
        if r["scenario"] == "checkout_3min":
            yearly[r["provider"]] = r["cost_per_100_clean_gb_usd"]
    return frontmatter(
        DATASETS["proxy"][2],
        ["residential-proxy", "proxy-pricing", "smartproxy", "bright-data", "oxylabs",
         "iproyal", "soax", "webshare", "sticky-session", "tco", "benchmark"],
    ) + T("""
# Residential Proxy 9-Dimension Commercial Policy & Sticky-Session Loss Matrix (2026)

Per-GB list price is the least useful number in a proxy contract. This dataset records nine commercial
dimensions per vendor plus the **sticky-session re-run tax** across three realistic flow shapes.

## Files

| File | Rows | Description |
|---|---|---|
| `data/residential_proxy_9d_matrix_2026.csv` | %d | 7 providers x 3 flow scenarios |
| `data/residential_proxy_9d_matrix_2026.jsonl` | %d | Same records as newline-delimited JSON |

## The nine dimensions

1. Entry PAYG USD/GB
2. Volume price at 100 GB
3. Billing granularity
4. Minimum deposit
5. Free trial
6. Refund window (days)
7. Pool size (millions of IPs) and country coverage
8. KYC friction
9. Sticky-session window (max + default minutes)

## Schema

| Column | Type | Meaning |
|---|---|---|
| `provider` | string | Vendor, incl. the free `curl_cffi + WARP` baseline |
| `entry_usd_per_gb` | float | Cheapest advertised PAYG rate |
| `volume_100gb_usd_per_gb` | float | Effective rate at 100 GB |
| `min_deposit_usd` | float | Cash needed to start |
| `refund_window_days` | int | Self-serve refund window, 0 = none published |
| `kyc_required` | string | Account friction before traffic flows |
| `sticky_max_minutes` | int | Longest documented session hold |
| `scenario` | string | `checkout_3min`, `login_cart_10min`, `dashboard_30min` |
| `hazard_pct` | float | Probability the flow must restart before completing |
| `rerun_loss_pct` | float | `h*(1-h)`-normalised re-run tax |
| `billable_gb_per_clean_gb` | float | `1/(1-h)` traffic amplification |
| `effective_usd_per_gb` | float | `volume_price * billable_gb_per_clean_gb` |
| `cost_per_100_clean_gb_usd` | float | Cost of 100 GB of *clean* traffic |

## Method

```
survive       = 1 - hazard
rerun_loss    = hazard / survive
billable_mult = 1 / survive
effective_gbp = 100gb_price * billable_mult
```

A dropped sticky IP invalidates `cf_clearance`, so the whole multi-step flow is re-run; a rotating IP
carries a fixed challenge failure rate instead. Neither is free, and the crossover is scenario-specific.

## Summary table (3-minute checkout flow)

| Provider | Entry $/GB | 100 GB $/GB | KYC | Trial | Sticky max | Effective $/GB |
|---|---|---|---|---|---|---|
%s

Cost of 100 GB of clean traffic in the checkout scenario: **$%.2f** for the best-priced vendor versus
**$%.2f** for the most expensive — banding that never appears on a per-GB price page.

## Use the calculator and mirror

%s

**Deep dive**
- [Why rotating residential proxies still get 403s: sticky TTL, JA3 and ASN economics](%s)
- [Research blog index](%s)

%s
%s""") % (
        len(rows), len(rows), table,
        min(yearly.values()), max(yearly.values()),
        "\n".join("- " + x for x in common_links("proxy")),
        LINKS["proxy"]["blog"], LINKS["proxy"]["blog2"],
        matrix_footer("proxy"), DISCLOSURE,
    )


def pay_readme():
    rows = pay_rows()
    be = {}
    for r in rows:
        if r["breakeven_mrr_usd"] is not None and r["formation_service"] == "Firstbase":
            be[(r["aov_usd"], r["intl_card_pct"], r["fx_enabled"])] = r["breakeven_mrr_usd"]
    table = "\n".join(
        "| $%s | $%d | %d%% | %s | $%s | $%s | $%s |" % (
            "{:,}".format(r["mrr_usd"]), r["aov_usd"], r["intl_card_pct"],
            "yes" if r["fx_enabled"] else "no",
            "{:,.0f}".format(r["mor_monthly_fee_usd"]),
            "{:,.0f}".format(r["llc_monthly_total_usd"]),
            "{:,.0f}".format(r["llc_minus_mor_monthly_usd"]))
        for r in rows if r["aov_usd"] == 49 and r["formation_service"] == "Firstbase"
        and r["intl_card_pct"] == 70 and not r["fx_enabled"])
    return frontmatter(
        DATASETS["pay"][2],
        ["saas", "payments", "merchant-of-record", "stripe", "paddle", "lemon-squeezy",
         "us-llc", "firstbase", "stripe-atlas", "doola", "tax", "tco", "indie-hacker"],
    ) + T("""
# Global SaaS: MoR vs US LLC + Stripe 3-Year Net Fee Matrix (2026)

A flat "5% Merchant of Record" is not comparable to "2.9% + $0.30" plus a company. This dataset prices
both routes across MRR, AOV and international card mix, and reports **3-year net revenue retained**.

## Files

| File | Rows | Description |
|---|---|---|
| `data/saas_payments_mor_vs_us_llc_2026.csv` | %d | 7 MRR x 4 AOV x 3 card mixes x 3 formation services |
| `data/saas_payments_mor_vs_us_llc_2026.jsonl` | %d | Same records as newline-delimited JSON |

## Schema

| Column | Type | Meaning |
|---|---|---|
| `scenario_id` | string | Stable row id |
| `formation_service` | string | Firstbase ($399) / Stripe Atlas ($500) / Doola ($297) |
| `mrr_usd`, `aov_usd` | float | Revenue and average order value |
| `orders_per_month` | float | `MRR / AOV` |
| `intl_card_pct`, `fx_enabled` | int, bool | Card mix and 1% FX surcharge toggle |
| `mor_monthly_fee_usd` | float | `MRR * 5% + orders * $0.50` |
| `mor_3y_net_usd` | float | Retained revenue over 36 months via MoR |
| `stripe_blended_rate_pct` | float | `2.9% + intl*1.5% + (fx ? 1% : 0)` |
| `llc_monthly_total_usd` | float | Stripe processing + $1,000/yr compliance budget |
| `llc_3y_net_usd` | float | Retained revenue over 36 months, entity cost deducted |
| `llc_minus_mor_3y_usd` | float | Positive = LLC keeps more |
| `breakeven_mrr_usd` | float | MRR at which the LLC route overtakes MoR |

## Method

```
N             = MRR / AOV
MoR           = MRR*0.05 + N*0.50
stripe_rate   = 0.029 + intl*0.015 + (fx ? 0.01 : 0)
Stripe        = MRR*stripe_rate + N*0.30 + 1000/12
rate_delta    = (0.05 - stripe_rate) + 0.20/AOV
breakeven     = (1000/12) / rate_delta      (infinite when rate_delta <= 0)
3y_net        = 36*(MRR - monthly_fee) [- entity_3y_cost for the LLC route]
```

Entity 3-year costs (formation + franchise/agent/Form 5472 prep) are the published research figures:
Firstbase **$876**, Stripe Atlas **$1,600**, Doola **$6,177**. They exclude income tax, sales tax/VAT
registration and optional add-ons.

## Breakeven MRR (Firstbase route)

| AOV | 0% intl | 70% intl | 70% intl + 1% FX |
|---|---|---|---|
| $15 | $%s | $%s | $%s |
| $29 | $%s | $%s | $%s |
| $49 | $%s | $%s | $%s |
| $99 | $%s | $%s | $%s |

## Summary table ($49 AOV, 70% international cards, Firstbase)

| MRR | AOV | Intl % | FX | MoR fee/mo | LLC total/mo | LLC − MoR/mo |
|---|---|---|---|---|---|---|
%s

## Use the calculator and mirror

%s

**Deep dives**
- [The 5% MoR illusion: exact US LLC + Stripe breakeven](%s)
- [Firstbase vs Stripe Atlas vs Doola: the 3-year bill](%s)

%s
%s""") % (
        len(rows), len(rows),
        *["{:,.0f}".format(be[(a, i, f)]) if be.get((a, i, f)) is not None else "never"
          for a in AOVS for i, f in [(0, False), (70, False), (70, True)]],
        table,
        "\n".join("- " + x for x in common_links("pay")),
        LINKS["pay"]["blog"], LINKS["pay"]["blog2"],
        matrix_footer("pay"), DISCLOSURE,
    )


BUILDERS = {
    "gpu": (gpu_rows, gpu_readme),
    "scrape": (scrape_rows, scrape_readme),
    "proxy": (proxy_rows, proxy_readme),
    "pay": (pay_rows, pay_readme),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=sorted(BUILDERS))
    ap.add_argument("--repo", required=True, help="local repository root")
    args = ap.parse_args()
    rows_fn, readme_fn = BUILDERS[args.dataset]
    rows = rows_fn()
    name = DATASETS[args.dataset][1]
    out = os.path.join(args.repo, "hf-dataset-mirror")
    os.makedirs(os.path.join(out, "data"), exist_ok=True)
    csv_path = os.path.join(out, "data", name + ".csv")
    jsonl_path = os.path.join(out, "data", name + ".jsonl")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(jsonl_path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme_fn())
    print("wrote %d rows -> %s" % (len(rows), out))


if __name__ == "__main__":
    main()
