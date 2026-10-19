"""
Stepper Component for Skill Gap AI
Displays the 5-step workflow with completed, active, and pending states.
Renders clean HTML without leading indentation so Streamlit displays
the visual component properly rather than treating it as an indented code block.
"""

from typing import List, Tuple
import html
import streamlit as st

STEPS: List[Tuple[int, str, str]] = [
    (1, "Upload Resume", "📄"),
    (2, "Job Description", "📝"),
    (3, "Analyze Resume", "⚡"),
    (4, "Skill Gap Report", "📊"),
    (5, "Learning Resources", "🎓"),
]


def render_stepper(current_step: int):
    """
    Renders a modern, connected 5-step workflow progress bar.
    current_step: 1 to 5 indicating the current active stage.
    """
    total_steps = len(STEPS)
    items = []

    for idx, (step_num, label, icon) in enumerate(STEPS):
        if step_num < current_step:
            status_class = "completed"
            circle_content = "✓"
        elif step_num == current_step:
            status_class = "active"
            circle_content = str(step_num)
        else:
            status_class = "pending"
            circle_content = str(step_num)

        escaped_label = html.escape(label)
        step_html = (
            f'<div class="step-item {status_class}">'
            f'<div class="step-circle">{circle_content}</div>'
            f'<span class="step-label">{icon} {escaped_label}</span>'
            f'</div>'
        )
        items.append(step_html)

        if idx < total_steps - 1:
            div_class = "completed" if step_num < current_step else ""
            divider_html = f'<div class="step-divider {div_class}"></div>'
            items.append(divider_html)

    stepper_html = f'<div class="workflow-container">{"".join(items)}</div>'
    st.markdown(stepper_html, unsafe_allow_html=True)
