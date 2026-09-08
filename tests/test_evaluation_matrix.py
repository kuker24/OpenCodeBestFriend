#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvaluationMatrixTests(unittest.TestCase):
    """
    Validates the 12 required evaluation scenarios defined in Section 11 of
    OCBF-Prompt-Implementasi-Final.md.
    """

    def setUp(self):
        self.agents = (ROOT / "templates" / "AGENTS.md").read_text(encoding="utf-8")
        self.routing = (ROOT / "rules" / "00-routing.md").read_text(encoding="utf-8")
        self.verification = (ROOT / "rules" / "01-verification.md").read_text(encoding="utf-8")
        self.playwright_qa = (ROOT / "skills" / "playwright-qa" / "SKILL.md").read_text(encoding="utf-8")
        self.taste_guard = (ROOT / "skills" / "impeccable" / "reference" / "taste-guard.md").read_text(encoding="utf-8")
        self.browser_act = (ROOT / "skills" / "browser-act" / "SKILL.md").read_text(encoding="utf-8")
        self.scroll_craft = (ROOT / "skills" / "scroll-craft" / "SKILL.md").read_text(encoding="utf-8")
        self.impeccable = (ROOT / "skills" / "impeccable" / "SKILL.md").read_text(encoding="utf-8")

    def test_case_01_backend_python_api_no_browser(self):
        # Scenario 1: Perbaiki API Python tanpa UI -> no browser launched, no taste
        self.assertIn("Never launch for backend/non-UI", self.routing)
        self.assertIn("Never start browser sessions when only backend, API, database, or non-UI code changed", self.playwright_qa)

    def test_case_02_login_validation_project_with_playwright(self):
        # Scenario 2: Perbaiki validasi login pada project yang sudah memakai Playwright
        self.assertIn("Project E2E suites (Playwright Test/Cypress) stay authoritative for regressions", self.agents)
        self.assertIn("Respect Project Test Suites", self.playwright_qa)

    def test_case_03_local_app_ui_check_without_e2e_suite(self):
        # Scenario 3: Cek UI aplikasi lokal tanpa suite E2E -> Playwright CLI exploratory QA, no app dependency
        self.assertIn("Browser QA → skill `playwright-qa`", self.agents)
        self.assertIn("Playwright CLI is an agent verification tool, NOT an application runtime or production dependency", (ROOT / "skills" / "playwright-qa" / "references" / "setup.md").read_text(encoding="utf-8"))

    def test_case_04_cypress_project_regression_respected(self):
        # Scenario 4: Jalankan regresi pada project yang sudah memakai Cypress -> Cypress respected, not replaced
        self.assertIn("Run existing project test suites (Playwright Test, Cypress) for regression", self.verification)
        self.assertIn("Playwright Test, Cypress, or another runner, run regressions through the project's own package manager", self.playwright_qa)

    def test_case_05_public_service_dashboard_operate_mode(self):
        # Scenario 5: Buat dashboard layanan publik yang sederhana -> Impeccable Operate, taste guard, no decorative motion
        self.assertIn("Operate:", self.impeccable)
        self.assertIn("dashboards", self.impeccable)
        self.assertIn("Operate demands scanability, high utility, and native conventions", self.taste_guard)

    def test_case_06_premium_landing_new_visual_world(self):
        # Scenario 6: Buat landing premium dengan keputusan visual baru -> Impeccable Persuade + taste guard + taste modules
        self.assertIn("Persuade:", self.impeccable)
        self.assertIn("taste/direction.md", (ROOT / "skills" / "impeccable" / "reference" / "new-work.md").read_text(encoding="utf-8"))

    def test_case_07_change_one_button_color_existing_landing(self):
        # Scenario 7: Ganti satu warna tombol pada landing yang sudah ada -> Refinement preserves incumbent identity
        self.assertIn("Refinement preserves; redesign replaces", self.impeccable)
        self.assertIn("Do not trigger a concept redesign or replace DESIGN.md for a narrow bug fix", (ROOT / "skills" / "impeccable" / "reference" / "taste" / "redesign.md").read_text(encoding="utf-8"))

    def test_case_08_portfolio_editorial_composition(self):
        # Scenario 8: Buat portfolio dengan komposisi editorial -> Impeccable Experience + taste composition
        self.assertIn("Experience:", self.impeccable)
        self.assertIn("Portfolios, galleries, showcases", self.impeccable)
        self.assertIn("Taste: Composition & Layout Diversity", (ROOT / "skills" / "impeccable" / "reference" / "taste" / "composition.md").read_text(encoding="utf-8"))

    def test_case_09_scroll_led_storytelling(self):
        # Scenario 9: Buat scroll-led story -> Scroll Craft; lightweight engine; no Playwright in bundle
        self.assertIn("Scroll-led storytelling", self.routing)
        self.assertIn("No KIE, Higgsfield, ffmpeg, Playwright", self.scroll_craft)

    def test_case_10_continuous_camera_world(self):
        # Scenario 10: Buat continuous camera world -> scroll-world
        self.assertIn("Continuous camera", self.scroll_craft)
        self.assertIn("scroll-world", self.scroll_craft)
        self.assertIn("Continuous camera fly-through, diorama, or 3D-world landing: `/scroll-world`", self.routing)

    def test_case_11_keep_brand_purple_and_inter_when_requested(self):
        # Scenario 11: Pertahankan brand ungu dan font Inter karena diminta -> user brief wins over taste heuristics
        self.assertIn("Explicit brief, pinned aesthetic, brand guidelines, and user constraints always win", self.taste_guard)
        self.assertIn("Purple accents, Inter font, SVG icons", self.taste_guard)
        self.assertIn("The brief wins.", self.impeccable)

    def test_case_12_browser_act_on_user_named_session(self):
        # Scenario 12: Gunakan BrowserAct pada sesi yang disebut pengguna
        self.assertIn("Explicit/session BrowserAct → `browser-act`", self.agents)
        self.assertIn("Explicit multi-account or persistent browser sessions: `/browser-act`", self.routing)
        self.assertIn("Use only when the user explicitly requests BrowserAct, specifies a browser-act CLI command, or requires pre-configured persistent/multi-account sessions", self.browser_act)


if __name__ == "__main__":
    unittest.main()
