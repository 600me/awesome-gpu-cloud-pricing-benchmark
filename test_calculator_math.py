#!/usr/bin/env python3
"""Offline math and packaging assertions for the GPU fit calculator.

The Python implementation below is intentionally independent of the browser
code.  A second pass extracts the calculator's pure JS core and runs the same
cases through Node, so the shipped page cannot silently drift from the model
that these assertions certify.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CALC = ROOT / "calculator" / "index.html"
MIRROR_INDEX = ROOT / "hf-space-mirror" / "index.html"
MIRROR_README = ROOT / "hf-space-mirror" / "README.md"
MAIN = ROOT / "index.html"

GIB = 1024**3
SAFETY_MARGIN = 1.15
CUDA_OVERHEAD_GIB = 2.0
PRACTICAL_VRAM_UTILIZATION = 0.90
KV_DTYPE_BYTES = 2

PRECISIONS = {"bf16": 2.0, "fp8": 1.0, "int4": 0.5}
CONTEXTS = {4096, 8192, 32768, 131072}
CONCURRENCIES = {1, 4, 16, 64}

MODELS = {
    "llama31-8b": dict(params=8.03, layers=32, kv_heads=8, head_dim=128, arch="gqa"),
    "llama33-70b": dict(params=70.6, layers=80, kv_heads=8, head_dim=128, arch="gqa"),
    "qwen25-72b": dict(params=72.7, layers=80, kv_heads=8, head_dim=128, arch="gqa"),
    "deepseek-v3": dict(
        params=671.0, layers=61, kv_heads=128, head_dim=128, arch="mla",
        kv_lora_rank=512, qk_rope_head_dim=64,
    ),
}

GPUS = [
    # id, vram GiB, NVLink, RunPod $/GPU-hr, Vast $/GPU-hr, Vast bundle
    ("4090", 24, False, 0.34, 0.429, 2),
    ("l40s", 48, False, 0.79, 0.801, 1),
    ("a100", 80, True, 1.39, 0.989, 1),
    ("h100", 80, True, 2.69, 2.01, 1),
    ("h200", 141, True, 3.59, 3.274, 1),
]

_PASSED = 0


def check(condition: bool, message: str) -> None:
    global _PASSED
    if not condition:
        raise AssertionError(message)
    _PASSED += 1
    print(f"PASS  {message}")


def close(actual: float, expected: float, tol: float = 1e-9) -> bool:
    return abs(float(actual) - float(expected)) <= tol


def kv_bytes_per_token(model: dict) -> int:
    if model["arch"] == "mla":
        return model["layers"] * (model["kv_lora_rank"] + model["qk_rope_head_dim"]) * KV_DTYPE_BYTES
    return 2 * model["layers"] * model["kv_heads"] * model["head_dim"] * KV_DTYPE_BYTES


def compute(model_id: str, precision: str, context: int, concurrency: int) -> dict:
    model = MODELS[model_id]
    weights = model["params"] * 1e9 * PRECISIONS[precision] / GIB
    kv_per_token = kv_bytes_per_token(model)
    kv = kv_per_token * context * concurrency / GIB
    subtotal = weights + kv + CUDA_OVERHEAD_GIB
    total = subtotal * SAFETY_MARGIN
    naive_mha = (
        2 * model["layers"] * model["kv_heads"] * model["head_dim"]
        * KV_DTYPE_BYTES * context * concurrency / GIB
    )
    gpus = {}
    for gid, vram, nvlink, runpod_rate, vast_rate, bundle in GPUS:
        raw = max(1, math.ceil(total / (vram * PRACTICAL_VRAM_UTILIZATION) - 1e-9))
        cards = 1 if raw <= 1 else 2 ** math.ceil(math.log2(raw))
        billed = math.ceil(cards / bundle) * bundle
        gpus[gid] = {
            "raw": raw,
            "cards": cards,
            "capacity": cards * vram,
            "nvlink": nvlink,
            "runpod": cards * runpod_rate,
            "vast": billed * vast_rate,
            "vast_billed": billed,
            "bundle": bundle,
        }
    return {
        "model": model_id,
        "weights": weights,
        "kv_per_token": kv_per_token,
        "kv": kv,
        "subtotal": subtotal,
        "total": total,
        "reserve": total - subtotal,
        "naive_mha": naive_mha,
        "mla_saving": naive_mha / kv if model["arch"] == "mla" else None,
        "gpus": gpus,
    }


NODE_HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const match = html.match(/<script id="calc-core">([\s\S]*?)<\/script>/);
if (!match) { console.error('missing calc-core script'); process.exit(2); }
const context = {console};
vm.createContext(context);
vm.runInContext(match[1], context);
const C = context.GPU_CALC;
if (!C) { console.error('GPU_CALC not exported'); process.exit(3); }
const cases = JSON.parse(process.argv[2]);
const out = cases.map(function (item) {
  const r = C.compute(item);
  return {
    total: r.totalGiB,
    weights: r.weightsGiB,
    kv: r.kvGiB,
    kv_per_token: r.kvPerTokenBytes,
    naive: r.naiveMhaKvGiB,
    gpus: r.gpus.map(function (g) {
      return {
        id: g.id, raw: g.rawCards, cards: g.cards,
        runpod: g.runpod.hourly, vast: g.vast.hourly,
        vast_billed: g.vast.billedCards, topology: g.topology.level
      };
    })
  };
});
process.stdout.write(JSON.stringify(out));
"""


def run_js_cases(cases: list[dict]) -> list[dict]:
    try:
        proc = subprocess.run(
            ["node", "-e", NODE_HARNESS, str(CALC), json.dumps(cases)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise AssertionError("Node.js is required for the JS/Python cross-check") from exc
    check(proc.returncode == 0, f"calculator JS core evaluates cleanly (node exit {proc.returncode})")
    if proc.returncode != 0:
        raise AssertionError(proc.stderr.strip())
    return json.loads(proc.stdout)


def assert_case(ref: dict, js: dict, label: str) -> None:
    check(close(js["total"], ref["total"], 1e-7),
          f"{label}: JS total matches Python ({ref['total']:.3f} GiB)")
    check(close(js["weights"], ref["weights"], 1e-7),
          f"{label}: JS weight term matches Python ({ref['weights']:.3f} GiB)")
    check(close(js["kv"], ref["kv"], 1e-9),
          f"{label}: JS KV term matches Python ({ref['kv']:.4f} GiB)")
    check(int(js["kv_per_token"]) == int(ref["kv_per_token"]),
          f"{label}: KV bytes/token identical in JS and Python ({ref['kv_per_token']:,} B)")
    for gpu in js["gpus"]:
        expected = ref["gpus"][gpu["id"]]
        check(gpu["cards"] == expected["cards"],
              f"{label}: JS recommends {gpu['cards']}× {gpu['id']} (Python {expected['cards']}×)")
        check(close(gpu["runpod"], expected["runpod"], 1e-9),
              f"{label}: JS RunPod hourly matches Python for {gpu['id']}")
        check(close(gpu["vast"], expected["vast"], 1e-9),
              f"{label}: JS Vast.ai hourly matches Python for {gpu['id']}")


def main() -> int:
    print("== GPU calculator offline math & packaging assertions ==")
    check(CALC.is_file(), f"calculator page exists: {CALC}")
    html = CALC.read_text(encoding="utf-8")

    # ---- 8B / BF16 / 4k -------------------------------------------------
    r8 = compute("llama31-8b", "bf16", 4096, 1)
    check(19.9 <= r8["total"] <= 20.3, f"8B BF16 4k total in expected band ({r8['total']:.3f} GiB)")
    check(close(r8["weights"], 14.957, 0.002), f"8B BF16 weights ≈ 14.96 GiB ({r8['weights']:.3f})")
    check(close(r8["kv"], 0.5, 1e-9), "8B BF16 4k KV cache is exactly 0.50 GiB")
    check(r8["total"] < 24, "8B BF16 4k fits one 24 GB RTX 4090")
    check(r8["gpus"]["4090"]["cards"] == 1, "8B BF16 4k recommends exactly 1× RTX 4090")

    # ---- 70B / BF16 / 4k: must be ~150-155 GiB and 4 cards ---------------
    r70 = compute("llama33-70b", "bf16", 4096, 1)
    check(150.0 <= r70["total"] <= 155.0,
          f"70B BF16 4k total is in the mandated 150-155 GiB band ({r70['total']:.3f} GiB)")
    check(close(r70["total"], 154.966, 0.002),
          f"70B BF16 4k total matches the closed-form model ({r70['total']:.3f} GiB)")
    check(close(r70["weights"], 131.503, 0.002),
          f"70B BF16 weight term ≈ 131.50 GiB ({r70['weights']:.3f})")
    check(close(r70["kv"], 1.25, 1e-9), "70B BF16 4k KV cache is exactly 1.25 GiB")
    check(r70["gpus"]["a100"]["raw"] == 3,
          "70B BF16 4k raw fit is 3 A100 cards at 90% usable VRAM")
    check(r70["gpus"]["a100"]["cards"] == 4,
          "70B BF16 4k recommends 4× A100, not 2 cards")
    check(r70["gpus"]["h100"]["cards"] == 4,
          "70B BF16 4k recommends 4× H100, not 2 cards")
    check(r70["gpus"]["a100"]["raw"] != 2 and r70["gpus"]["h100"]["raw"] != 2,
          "70B BF16 4k never reports a 2-card raw fit")
    check(r70["gpus"]["a100"]["capacity"] == 320,
          "4× A100 80GB provides a 320 GB VRAM pool")

    # ---- 70B / INT4 / 4k -------------------------------------------------
    r70i = compute("llama33-70b", "int4", 4096, 1)
    check(41.0 <= r70i["total"] <= 42.0,
          f"70B INT4 4k total ≈ 41.5 GiB ({r70i['total']:.3f} GiB)")
    check(close(r70i["weights"], 32.876, 0.002),
          f"70B INT4 weight term ≈ 32.88 GiB ({r70i['weights']:.3f})")
    check(close(r70i["kv"], 1.25, 1e-9), "INT4 weights do not shrink the BF16 KV cache")
    check(r70i["gpus"]["4090"]["cards"] == 2,
          "70B INT4 4k recommends 2× RTX 4090 (PCIe-only warning applies)")
    check(r70i["gpus"]["4090"]["nvlink"] is False,
          "70B INT4 multi-4090 topology is correctly marked PCIe-only")
    check(r70i["gpus"]["a100"]["cards"] == 1,
          "70B INT4 4k fits a single 80 GB A100")

    # ---- DeepSeek 671B / FP8 / 4k / MLA ---------------------------------
    rds = compute("deepseek-v3", "fp8", 4096, 1)
    check(rds["kv_per_token"] == 70272,
          "DeepSeek MLA KV is exactly 70,272 bytes/token (61 × (512+64) × 2)")
    check(close(rds["kv"], 0.2681, 0.0002),
          f"DeepSeek 4k MLA KV cache ≈ 0.27 GiB ({rds['kv']:.4f} GiB)")
    check(700.0 <= rds["total"] <= 740.0,
          f"DeepSeek 671B FP8 4k total ≈ 721 GiB ({rds['total']:.3f} GiB)")
    check(close(rds["weights"], 624.917, 0.003),
          f"DeepSeek 671B FP8 weight term ≈ 624.92 GiB ({rds['weights']:.3f})")
    check(rds["naive_mha"] > 15.0,
          f"naive MHA comparison explodes past 15 GiB ({rds['naive_mha']:.3f} GiB)")
    check(rds["mla_saving"] > 50.0,
          f"MLA reduces KV memory by >50× versus naive MHA ({rds['mla_saving']:.1f}×)")
    check(rds["kv"] < 1.0, "DeepSeek MLA KV stays below 1 GiB at 4k, not a naive multi-GiB block")
    check(rds["gpus"]["h200"]["cards"] == 8,
          "DeepSeek 671B FP8 4k recommends 8× H200")
    check(rds["gpus"]["h100"]["cards"] == 16,
          "DeepSeek 671B FP8 4k recommends 16× H100 at 80 GB each")
    check(rds["gpus"]["h200"]["cards"] * 141 >= rds["total"],
          "8× H200 capacity covers the DeepSeek requirement")

    # ---- Dynamic KV with concurrency ------------------------------------
    r64 = compute("llama33-70b", "bf16", 4096, 64)
    check(close(r64["kv"], 1.25 * 64, 1e-9),
          "concurrency 64 multiplies 70B KV cache by 64 (80 GiB)")
    check(close(r64["total"], (131.503 + 80 + 2) * 1.15, 0.003),
          f"concurrency 64 total follows the same closed form ({r64['total']:.3f} GiB)")

    # ---- Internal algebra ------------------------------------------------
    for label, ref in (("8B", r8), ("70B", r70), ("70B INT4", r70i), ("DeepSeek", rds)):
        check(close(ref["subtotal"], ref["weights"] + ref["kv"] + CUDA_OVERHEAD_GIB, 1e-9),
              f"{label}: weights + KV + 2 GiB CUDA equals the subtotal")
        check(close(ref["total"], ref["subtotal"] * SAFETY_MARGIN, 1e-9),
              f"{label}: 15% safety margin applied exactly once")
        check(close(ref["reserve"], ref["subtotal"] * 0.15, 1e-9),
              f"{label}: reserve is exactly 15% of the pre-margin subtotal")

    # ---- Pricing rules ---------------------------------------------------
    check(close(r8["gpus"]["4090"]["runpod"], 0.34, 1e-9),
          "1× RTX 4090 RunPod ledger = 1 × $0.34/hr")
    check(r8["gpus"]["4090"]["vast_billed"] == 2,
          "1× RTX 4090 Vast.ai requirement is billed as a 2-GPU bundle")
    check(close(r8["gpus"]["4090"]["vast"], 0.858, 1e-9),
          "1× RTX 4090 Vast.ai ledger charges the full 2-GPU bundle ($0.858/hr)")
    check(close(r70["gpus"]["a100"]["runpod"], 4 * 1.39, 1e-9),
          "4× A100 RunPod ledger = 4 × $1.39/hr")
    check(close(r70["gpus"]["a100"]["vast"], 4 * 0.989, 1e-9),
          "4× A100 Vast.ai ledger = 4 × $0.989/hr")
    check(close(rds["gpus"]["h200"]["runpod"], 8 * 3.59, 1e-9),
          "8× H200 RunPod ledger = 8 × $3.59/hr")

    # ---- JS/Python cross-check ------------------------------------------
    cases = [
        {"model": "llama31-8b", "precision": "bf16", "context": 4096, "concurrency": 1},
        {"model": "llama33-70b", "precision": "bf16", "context": 4096, "concurrency": 1},
        {"model": "llama33-70b", "precision": "int4", "context": 4096, "concurrency": 1},
        {"model": "deepseek-v3", "precision": "fp8", "context": 4096, "concurrency": 1},
        {"model": "llama33-70b", "precision": "bf16", "context": 4096, "concurrency": 64},
    ]
    js_results = run_js_cases(cases)
    refs = [
        r8, r70, r70i, rds, r64,
    ]
    for label, ref, js in zip(
        ("8B BF16 4k", "70B BF16 4k", "70B INT4 4k", "DeepSeek FP8 4k MLA", "70B BF16 4k ×64"),
        refs,
        js_results,
    ):
        assert_case(ref, js, label)
    check(len(js_results) == 5, "all five JS cases returned results")

    # ---- Static page content --------------------------------------------
    for needle in (
        "Llama 3.1 8B", "Llama 3.3 70B", "Qwen 2.5 72B",
        "DeepSeek V3 / R1 671B MoE", "Custom parameter count",
        "BF16", "FP8", "INT4",
        "4k", "8k", "32k", "128k",
        "MLA", "NVLink", "2-GPU bundle",
        "Topology-safe best fit", "RTX 4090", "L40S", "A100 80GB SXM",
        "H100 80GB SXM", "H200 141GB SXM",
    ):
        check(needle in html, f"calculator page contains required content: {needle!r}")
    check("REPLACE_ME" not in html, "calculator page contains no REPLACE_ME placeholder")
    check(html.count("utm_source=gpu_calculator") >= 2,
          "both CTA links carry utm_source=gpu_calculator")
    check("https://go.272738.xyz/runpod" in html,
          "RunPod CTA points at the verified go.272738.xyz relay")
    check("https://go.272738.xyz/vastai" in html,
          "Vast.ai CTA points at the verified go.272738.xyz relay")
    check("utm_medium=cta" in html, "CTA links carry utm_medium=cta")
    check("Affiliate disclosure (FTC 16 CFR Part 255)" in html,
          "FTC affiliate disclosure is present near the CTAs")
    check("at no additional cost to you" in html,
          "FTC disclosure states the commission is at no extra cost")
    check(re.search(r"<script[^>]+src=", html) is None,
          "calculator has zero external <script src> dependencies")
    check(re.search(r"<link[^>]+stylesheet", html) is None,
          "calculator has zero external stylesheet dependencies")

    # ---- HuggingFace static mirror --------------------------------------
    check(MIRROR_INDEX.is_file(), "hf-space-mirror/index.html exists")
    check(MIRROR_README.is_file(), "hf-space-mirror/README.md exists")
    check(hashlib.sha256(MIRROR_INDEX.read_bytes()).hexdigest()
          == hashlib.sha256(CALC.read_bytes()).hexdigest(),
          "HF mirror index.html is byte-identical to calculator/index.html")
    readme = MIRROR_README.read_text(encoding="utf-8")
    check(readme.startswith("---\n"), "HF README begins with YAML frontmatter")
    check("\nsdk: static\n" in readme, "HF README declares sdk: static")
    check("\napp_file: index.html\n" in readme, "HF README declares app_file: index.html")
    check("REPLACE_ME" not in readme, "HF README contains no REPLACE_ME placeholder")

    # ---- Main-site navigation -------------------------------------------
    main_html = MAIN.read_text(encoding="utf-8")
    check('href="/calculator/"' in main_html,
          "main site contains a direct /calculator/ navigation link")
    check("Interactive GPU Fit" in main_html and "Cost Calculator" in main_html,
          "main-site nav uses the required calculator label")
    check(main_html.find('href="/calculator/"') < main_html.find("<h1>"),
          "calculator navigation appears above the main-site hero")

    print(f"\nALL {_PASSED} ASSERTIONS PASSED")
    print("Exit code: 0 (math, packaging, CTA and navigation all verified)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"\nFAIL  {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 - assertion harness must fail closed
        print(f"\nERROR  {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
