"""
Automated Playwright Demo Tour Recording Script (Section 4)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Launches headed/headless Chromium, triggers Guided Demo Mode, steps through
the storyboard, records video to demo_out/mmd_demo.webm, and verifies timeline log.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT_DIR / "demo_out"


def record_demo(port: int = 8501, headless: bool = True):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target_url = f"http://localhost:{port}"

    print(f"🎬 [Demo Recorder] Connecting to {target_url}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--start-maximized", "--disable-gpu", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(OUT_DIR),
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            page.goto(target_url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)

            # Check if demo button is present
            demo_btn = page.locator("button:has-text('Run Director Demo')")
            if demo_btn.count() > 0:
                print("🎯 [Demo Recorder] Found 'Run Director Demo' button. Starting tour...")
                demo_btn.first.click()
                time.sleep(2)
            else:
                print("ℹ️ [Demo Recorder] Demo button not found or already running.")

            # Step through 12 steps
            for step_num in range(1, 13):
                print(f"📍 [Demo Recorder] Capturing Step {step_num}/12...")
                page.wait_for_timeout(2500)
                # Click next step button if available
                next_btn = page.locator("button:has-text('⏭️')")
                if next_btn.count() > 0 and step_num < 12:
                    next_btn.first.click()
                    page.wait_for_timeout(1000)

            print("✅ [Demo Recorder] Tour finished successfully.")

        except Exception as e:
            print(f"⚠️ [Demo Recorder] Recording encountered: {e}")

        finally:
            context.close()
            browser.close()

    timeline_file = OUT_DIR / "demo_timeline.json"
    if timeline_file.exists():
        print(f"📄 [Demo Recorder] Timeline confirmed: {timeline_file}")
    else:
        print("⚠️ [Demo Recorder] Note: demo_timeline.json was not created.")


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    record_demo(port=port_arg, headless=True)
