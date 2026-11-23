"""
Demo Mode Lower-Third Overlay & Executive Caption Bar (Section 4)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine
"""

import streamlit as st
from typing import Any


def render_demo_overlay(
    step_info: dict[str, Any],
    total_steps: int,
    is_paused: bool,
    on_next=None,
    on_prev=None,
    on_toggle_pause=None,
    on_stop=None
):
    """
    Renders an elegant floating lower-third caption bar for hackathon judges and executive demos.
    Includes progress indicator, step counter, live narrative caption, and interactive controls.
    """
    step_idx = step_info.get("id", 1)
    step_title = step_info.get("title", "")
    caption = step_info.get("caption", "")
    progress_pct = int((step_idx / total_steps) * 100)

    # Floating CSS for lower-third container
    st.markdown(
        f"""
        <style>
        .mmd-demo-banner {{
            position: fixed;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            width: 86%;
            max-width: 1100px;
            background: rgba(29, 38, 44, 0.95);
            backdrop-filter: blur(8px);
            border: 1px solid #4B5A63;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
            padding: 12px 18px;
            z-index: 99999;
            color: #EEF1F2;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .mmd-demo-progress-track {{
            height: 3px;
            width: 100%;
            background: #4B5A63;
            border-radius: 2px;
            margin-bottom: 8px;
            overflow: hidden;
        }}
        .mmd-demo-progress-fill {{
            height: 100%;
            width: {progress_pct}%;
            background: #2F5D7C;
            transition: width 0.4s ease;
        }}
        .mmd-demo-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.78rem;
            color: #8E9AA2;
            margin-bottom: 4px;
        }}
        .mmd-demo-caption {{
            font-size: 0.92rem;
            font-weight: 500;
            color: #FFFFFF;
            line-height: 1.35;
        }}
        .mmd-demo-badge {{
            background: #2F5D7C;
            color: #FFFFFF;
            padding: 2px 7px;
            border-radius: 3px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}
        </style>

        <div class="mmd-demo-banner">
            <div class="mmd-demo-progress-track">
                <div class="mmd-demo-progress-fill"></div>
            </div>
            <div class="mmd-demo-header">
                <div>
                    <span class="mmd-demo-badge">DIRECTOR DEMO</span>
                    <span style="margin-left: 8px; font-weight: 600; color: #EEF1F2;">{step_title}</span>
                </div>
                <div>
                    <span>Step {step_idx} of {total_steps}</span>
                </div>
            </div>
            <div class="mmd-demo-caption">
                {caption}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Optional control button bar in bottom sidebar or top corner
    with st.sidebar:
        st.markdown("---")
        st.markdown("#### :material/smart_display: Guided Tour Controls")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("⏮️", help="Previous step", key="demo_btn_prev"):
                if on_prev:
                    on_prev()
        with c2:
            pause_label = "▶️" if is_paused else "⏸️"
            if st.button(pause_label, help="Pause/Resume playback", key="demo_btn_pause"):
                if on_toggle_pause:
                    on_toggle_pause()
        with c3:
            if st.button("⏭️", help="Next step", key="demo_btn_next"):
                if on_next:
                    on_next()
        with c4:
            if st.button("⏹️", help="Exit guided demo", key="demo_btn_stop"):
                if on_stop:
                    on_stop()
