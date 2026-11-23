# Guided Executive Demo Mode (Section 4)
**Team 11:59 · Xovate'26 Management Hackathon**

## Overview
The demo subsystem is fully decoupled from the core calculation engines. It provides an autonomous, synchronized 60-second tour of the entire decision engine for hackathon judges and executive leadership.

## How to Run
1. **Interactive Tour in UI:**
   - Launch the Streamlit application:
     ```bash
     streamlit run app.py
     ```
   - In the sidebar, click the **🎬 Run Director Demo (60s)** button.
   - Use the lower-third overlay controls to pause (`⏸️`), advance (`⏭️`), step back (`⏮️`), or stop (`⏹️`).

2. **Automated Headless Video Recording:**
   - Run the Playwright recording script:
     ```bash
     python scripts/record_demo.py
     ```
   - The recording will be saved to `demo_out/mmd_demo.webm` alongside `demo_out/demo_timeline.json`.

## How to Configure
- **Storyboard:** Edit `demo/storyboard.yaml` to adjust step titles, dynamic narrative captions, actions, or preset triggers.
- **Settings & Speed:** Adjust `config/demo.yaml`:
  ```yaml
  enabled: true
  step_duration_sec: 4.5
  speed_scale: 1.0
  ```
- **Environment Override:** Disable instantly by launching with `MMD_DEMO=0`:
  ```bash
  MMD_DEMO=0 streamlit run app.py
  ```

## How to Uninstall / Remove Completely (2 Minutes)
The demo module is strictly isolated with zero runtime dependencies in the math engine:
1. Delete the `demo/` directory and `config/demo.yaml`.
2. Remove the 6-line guarded hook from `app.py`:
   ```python
   try:
       from demo import maybe_run_demo
   except ImportError:
       maybe_run_demo = None
   if maybe_run_demo:
       maybe_run_demo()
   ```
Core calculation engines and acceptance test suites will remain 100% green and unaffected.
