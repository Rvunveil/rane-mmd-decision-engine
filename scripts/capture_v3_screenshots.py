"""
Full-Page Playwright Visual Audit & Screenshot Suite (V3)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Captures full-page screenshots at 1920x1080 and 1366x768 across all pages
for Base Case and Red Sea / Hormuz crisis preset.
Saves to qa/v3/screenshots/ and evidence pairs in qa/v3/.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "qa" / "v3" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("1080p", 1920, 1080),
    ("768p", 1366, 768)
]

PAGES = [
    ("0_command_centre", "Materials Control Room", "0_Command_Centre"),
    ("1_forecast", "Price & Freight Forecast", "1_Forecast"),
    ("2_scenario_simulator", "What-if Scenario Simulator", "2_Scenario_Simulator"),
    ("3_profit_chain", "Live Recalculation Chain", "3_Profit_Chain"),
    ("4_containers_inventory", "Containers & Inventory", "4_Containers_Inventory"),
    ("5_action_matrix", "Prescriptive Action Matrix", "5_Action_Matrix"),
    ("6_assumptions", "Assumptions & Data Trace", "6_Assumptions_Data_Trace_About")
]


def run_capture(port: int = 8501):
    target_url = f"http://localhost:{port}"
    print(f"📸 Starting V3 Playwright Screenshot Sweep on {target_url}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])

        for vp_label, width, height in VIEWPORTS:
            print(f"\n🖥️  Capturing at {vp_label} ({width}x{height})...")
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()

            # 1. Base Case Sweep
            page.goto(target_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)

            for page_slug, nav_text, file_name in PAGES:
                print(f"  -> Navigating to {nav_text} (Base Case)...")
                # Look for link in sidebar navigation
                nav_link = page.locator(f"a:has-text('{nav_text}')")
                if nav_link.count() > 0:
                    nav_link.first.click()
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(2)
                else:
                    # Direct query param fallback if needed
                    page.goto(f"{target_url}/{file_name}", timeout=20000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(2)

                out_path = OUT_DIR / f"{page_slug}_base_{vp_label}.png"
                page.screenshot(path=str(out_path), full_page=True)
                print(f"     Saved: {out_path.name}")

            # 2. Red Sea / Hormuz Crisis Preset Sweep
            print(f"\n🌊 Capturing Red Sea / Hormuz Crisis Preset at {vp_label}...")
            # Return to Command Centre
            page.locator("a:has-text('Materials Control Room')").first.click()
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)

            # Click Red Sea preset button
            rs_btn = page.locator("button:has-text('Red Sea / Hormuz')")
            if rs_btn.count() > 0:
                rs_btn.first.click()
                time.sleep(2)

            for page_slug, nav_text, file_name in PAGES:
                print(f"  -> Navigating to {nav_text} (Red Sea Crisis)...")
                nav_link = page.locator(f"a:has-text('{nav_text}')")
                if nav_link.count() > 0:
                    nav_link.first.click()
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(2)

                out_path = OUT_DIR / f"{page_slug}_red_sea_{vp_label}.png"
                page.screenshot(path=str(out_path), full_page=True)
                print(f"     Saved: {out_path.name}")

            context.close()

        browser.close()

    print("\n✅ [Screenshot Suite] All viewports and scenarios captured successfully!")


if __name__ == "__main__":
    run_capture(8501)
