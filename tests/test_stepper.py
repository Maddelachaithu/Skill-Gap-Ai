"""
Unit Tests for Skill Gap AI - Stepper Component
Verifies that:
1. Stepper renders proper HTML with no lines having 4+ leading spaces.
2. Active, completed, and pending step classes are accurately computed.
3. Step labels match the required 5 stages.
"""

import pytest
from unittest.mock import patch, MagicMock

from components.stepper import render_stepper, STEPS


class TestStepperComponent:
    """Tests for the 5-step workflow progress indicator."""

    def test_stepper_labels(self):
        labels = [s[1] for s in STEPS]
        assert labels == [
            "Upload Resume",
            "Job Description",
            "Analyze Resume",
            "Skill Gap Report",
            "Learning Resources",
        ]

    @patch("components.stepper.st.markdown")
    def test_step_1_active_no_code_block_indentation(self, mock_markdown):
        render_stepper(1)
        assert mock_markdown.called
        rendered_html, kwargs = mock_markdown.call_args
        html_str = rendered_html[0]

        # Verify HTML contains workflow container and step 1 is active
        assert '<div class="workflow-container">' in html_str
        assert "step-item active" in html_str
        assert "Upload Resume" in html_str

        # CRITICAL TEST: No line should begin with 4 or more spaces,
        # which would trigger Markdown indented code blocks (<pre><code>)
        for line in html_str.splitlines():
            if line.strip():
                assert not line.startswith("    "), f"Indented line would render as code block: {line}"

        assert kwargs.get("unsafe_allow_html") is True

    @patch("components.stepper.st.markdown")
    def test_step_2_active_step_1_completed(self, mock_markdown):
        render_stepper(2)
        assert mock_markdown.called
        rendered_html, kwargs = mock_markdown.call_args
        html_str = rendered_html[0]

        assert "step-item completed" in html_str
        assert "step-item active" in html_str
        assert "✓" in html_str
        assert "Job Description" in html_str

        # Check divider completion
        assert "step-divider completed" in html_str
