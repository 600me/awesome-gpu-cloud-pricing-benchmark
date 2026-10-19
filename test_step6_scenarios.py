#!/usr/bin/env python3
"""Step 6A math verification for blog/runpod-vs-vastai-h100-a100.html.

Every dollar figure printed in the three workload scenarios is recomputed from
the stated rates and quantities. Standard library only.

    python3 test_step6_scenarios.py

Exit code 0 means the article's arithmetic is exact.
"""

import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTICLE = HERE / "blog" / "runpod-vs-vastai-h100-a100.html"

# Published catalog inputs, captured 2026-10-18T16:37:25Z (USD).
VAST_H100_SXM = 2.01
RUNPOD_H100_SXM = 2.69
RUNPOD_H100_SECURE = 3.99
VAST_H100_PCIE = 2.002
RUNPOD_H100_PCIE = 1.99
VAST_A100_SXM = 1.319
RUNPOD_A100_SXM = 1.39
RUNPOD_A100_SECURE = 1.79
VAST_A100_PCIE = 0.935
RUNPOD_A100_PCIE = 1.19
VAST_A100_SXM = 1.319
VAST_INTERRUPTIBLE = 1.19
RUNPOD_SPOT = 1.50
RUNPOD_A100_INTERRUPTIBLE = 0.78

# Stated billing assumptions.
INGRESS_WEIGHT_RATE = 0.02     # Vast, per GB
EGRESS_SERVE_RATE = 0.05       # Vast, per GB
STORAGE_RATE = 0.10            # per GB-month, both providers
HOURS_MONTH = 730
RESERVE = 0.15


def money(value):
    """Round to cents the way a provider invoice does."""
    return round(value + 1e-12, 2)


class ScenarioA(unittest.TestCase):
    """150 GB model pull plus a two-hour test."""

    gpu_hours = 2.0
    weights_gb = 150
    image_gb = 25
    pull_minutes = 40
    flashboot_seconds = 60

    def vast(self):
        gpu = self.gpu_hours * VAST_H100_SXM
        ingress = self.weights_gb * INGRESS_WEIGHT_RATE
        image = self.image_gb * INGRESS_WEIGHT_RATE
        cold = self.pull_minutes / 60 * VAST_H100_SXM
        return gpu, ingress, image, cold, gpu + ingress + image + cold

    def runpod(self):
        gpu = self.gpu_hours * RUNPOD_H100_SXM
        cold = self.flashboot_seconds / 3600 * RUNPOD_H100_SXM
        return gpu, cold, gpu + cold

    def test_vast_lines(self):
        gpu, ingress, image, cold, total = self.vast()
        self.assertEqual(money(gpu), 4.02)
        self.assertEqual(money(ingress), 3.00)
        self.assertEqual(money(image), 0.50)
        self.assertEqual(money(cold), 1.34)
        self.assertEqual(money(total), 8.86)
        self.assertEqual(money(total / self.gpu_hours), 4.43)

    def test_runpod_lines(self):
        gpu, cold, total = self.runpod()
        self.assertEqual(money(gpu), 5.38)
        self.assertEqual(money(cold), 0.04)
        self.assertEqual(money(total), 5.42)
        self.assertEqual(money(total / self.gpu_hours), 2.71)

    def test_runpod_is_63_percent_cheaper(self):
        vast_total = self.vast()[4]
        runpod_total = self.runpod()[2]
        self.assertEqual(money(vast_total - runpod_total), 3.44)
        self.assertEqual(round((vast_total / runpod_total - 1) * 100), 63)

    def test_twenty_minute_variant(self):
        overhead = (self.weights_gb * INGRESS_WEIGHT_RATE
                    + self.image_gb * INGRESS_WEIGHT_RATE
                    + self.pull_minutes / 60 * VAST_H100_SXM)
        gpu = (20 / 60) * VAST_H100_SXM
        self.assertEqual(money(overhead), 4.84)
        self.assertEqual(money(gpu), 0.67)


class ScenarioB(unittest.TestCase):
    """7x24 vLLM inference node."""

    def vast(self, reserve=RESERVE):
        gpu = HOURS_MONTH * VAST_H100_SXM
        egress_gb = 6 * 1024
        egress = egress_gb * EGRESS_SERVE_RATE
        storage = 500 * STORAGE_RATE
        failover = gpu * reserve
        return gpu, egress, storage, failover, gpu + egress + storage + failover

    def runpod(self):
        gpu = HOURS_MONTH * RUNPOD_H100_SXM
        storage = 500 * STORAGE_RATE
        return gpu, storage, gpu + storage

    def test_vast_lines(self):
        gpu, egress, storage, failover, total = self.vast()
        self.assertEqual(money(gpu), 1467.30)
        self.assertEqual(money(egress), 307.20)
        self.assertEqual(money(storage), 50.00)
        self.assertEqual(money(failover), 220.10)
        self.assertEqual(money(total), 2044.60)
        self.assertEqual(money(total / HOURS_MONTH), 2.80)

    def test_runpod_lines(self):
        gpu, storage, total = self.runpod()
        self.assertEqual(money(gpu), 1963.70)
        self.assertEqual(money(total), 2013.70)
        self.assertEqual(money(total / HOURS_MONTH), 2.76)

    def test_runpod_margin_needs_the_reserve(self):
        total_vast = self.vast()[4]
        total_runpod = self.runpod()[2]
        self.assertEqual(money(total_vast - total_runpod), 30.90)
        self.assertLess(total_runpod, total_vast)
        # Without the reserve the marketplace wins.
        unreserved = self.vast(reserve=0)[4]
        self.assertEqual(money(unreserved), 1824.50)
        self.assertLess(unreserved, total_runpod)

    def test_egress_crossover(self):
        gpu, egress, storage, failover, _ = self.vast()
        total_runpod = self.runpod()[2]
        fixed = gpu + failover + storage
        self.assertEqual(money(fixed), 1737.40)
        crossover_gb = (total_runpod - fixed) / EGRESS_SERVE_RATE
        self.assertEqual(round(crossover_gb), 5526)
        self.assertEqual(round(crossover_gb / 1024, 1), 5.4)


class ScenarioC(unittest.TestCase):
    """72-hour preemptible LoRA / distillation batch on three H100s."""

    gpu_hours = 216
    weights_gb = 450
    nvme_gb = 1536
    run_hours = 72
    evictions = 2
    eviction_minutes = 12

    def vast(self):
        gpu = self.gpu_hours * VAST_INTERRUPTIBLE
        ingress = self.weights_gb * INGRESS_WEIGHT_RATE
        nvme = self.nvme_gb * STORAGE_RATE * (self.run_hours / HOURS_MONTH)
        restarts = (self.evictions * self.eviction_minutes / 60
                    * VAST_INTERRUPTIBLE)
        return gpu, ingress, nvme, restarts, gpu + ingress + nvme + restarts

    def runpod(self):
        gpu = self.gpu_hours * RUNPOD_H100_SXM
        nvme = self.nvme_gb * STORAGE_RATE * (self.run_hours / HOURS_MONTH)
        return gpu, nvme, gpu + nvme

    def test_vast_lines(self):
        gpu, ingress, nvme, restarts, total = self.vast()
        self.assertEqual(money(gpu), 257.04)
        self.assertEqual(money(ingress), 9.00)
        self.assertEqual(money(nvme), 15.15)
        self.assertEqual(money(restarts), 0.48)
        self.assertEqual(money(total), 281.67)
        self.assertEqual(money(total / self.gpu_hours), 1.30)

    def test_runpod_lines(self):
        gpu, nvme, total = self.runpod()
        self.assertEqual(money(gpu), 581.04)
        self.assertEqual(money(total), 596.19)
        self.assertEqual(money(total / self.gpu_hours), 2.76)

    def test_saving_and_shares(self):
        _, ingress, nvme, restarts, total_vast = self.vast()
        total_runpod = self.runpod()[2]
        self.assertEqual(money(total_runpod - total_vast), 314.52)
        overhead = ingress + nvme + restarts
        self.assertEqual(money(overhead), 24.63)
        self.assertEqual(round(overhead / total_vast * 100, 1), 8.7)
        self.assertEqual(round((1 - total_vast / total_runpod) * 100, 1), 52.8)

    def test_runpod_spot_narrows_the_gap(self):
        total_vast = self.vast()[4]
        nvme = self.runpod()[1]
        spot = self.gpu_hours * RUNPOD_SPOT + nvme
        self.assertEqual(money(spot), 339.15)
        self.assertEqual(money(spot - total_vast), 57.48)

    def test_a100_variant(self):
        gpu = self.gpu_hours * RUNPOD_A100_INTERRUPTIBLE
        self.assertEqual(money(gpu), 168.48)
        self.assertEqual(money(gpu + self.weights_gb * INGRESS_WEIGHT_RATE), 177.48)
        self.assertEqual(money(self.gpu_hours * VAST_A100_SXM), 284.90)


class HeadlineDiscounts(unittest.TestCase):
    """The '25% / 26% below' claims in the standfirst."""

    def test_h100_vs_community(self):
        self.assertEqual(round((1 - VAST_H100_SXM / RUNPOD_H100_SXM) * 100), 25)

    def test_a100_vs_secure(self):
        self.assertEqual(round((1 - VAST_A100_SXM / RUNPOD_A100_SECURE) * 100), 26)


class ArticleText(unittest.TestCase):
    """The HTML must print the numbers this test derives."""

    @classmethod
    def setUpClass(cls):
        cls.html = ARTICLE.read_text(encoding="utf-8")

    def test_scenario_totals_present(self):
        for figure in ("$8.86", "$5.42", "$2,044.60", "$2,013.70",
                       "$281.67", "$596.19", "$314.52"):
            self.assertIn(figure, self.html)

    def test_no_stale_figures(self):
        for figure in ("$30.89", "near <strong>$192</strong>"):
            self.assertNotIn(figure, self.html)

    def test_canonical_and_ctas(self):
        self.assertIn(
            '<link rel="canonical" href="https://gpu.mybskm.top/blog/'
            'runpod-vs-vastai-h100-a100.html">', self.html)
        self.assertIn(
            'href="https://go.272738.xyz/runpod?src=compare_runpod_vast" '
            'target="_blank" rel="sponsored noopener"', self.html)
        self.assertIn(
            'href="https://go.272738.xyz/vastai?src=compare_runpod_vast" '
            'target="_blank" rel="sponsored noopener"', self.html)
        self.assertIn("https://huggingface.co/spaces/600me/llm-gpu-cost-calculator",
                      self.html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
