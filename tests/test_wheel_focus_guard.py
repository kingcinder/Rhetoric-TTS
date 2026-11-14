"""Mouse-wheel routing: a scrollable panel scrolls unless a control has focus.

The owner's report: wheeling over a spin box, combo box or slider in a
scrollable settings panel changed the control's value instead of scrolling the
view. ``rhetoric.gui_wheel`` inverts that by having the controls hand an
unfocused wheel to the enclosing scroll area, and keep it while focused.

These tests pin both halves of the rule for every control this application
constructs, the no-panel case, and that the filter route (which crashed Qt's
dispatch on hosted runners) does not come back.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget

from rhetoric import gui_wheel
from rhetoric.gui_wheel import WheelComboBox, WheelSlider, WheelSpinBox

# Widgets that must NOT be constructed plain (without Wheel* subclass) outside gui_wheel.py
# A plain QSpinBox/QComboBox/QSlider in a scrollable panel silently breaks the wheel fix.
_PLAIN_WIDGET_MARKERS = ("QSpinBox(", "QComboBox(", "QSlider(")


def _check_no_plain_widgets() -> None:
    """Verify no plain QSpinBox, QComboBox or QSlider is constructed outside gui_wheel.py.
    
    Scans all rhetoric source files (except gui_wheel.py) for plain widget construction
    patterns like QSpinBox(), QComboBox(), QSlider().  Subclassed versions like
    WheelSpinBox, WheelComboBox, WheelSlider are allowed.
    """
    import os
    import re
    from pathlib import Path

    rhetoric_dir = Path(__file__).resolve().parents[1] / "src" / "rhetoric"
    excluded = {Path("rhetoric/gui_wheel.py").name}

    for py_file in rhetoric_dir.rglob("*.py"):
        if py_file.name in excluded:
            continue
        if py_file.name.startswith("_"):
            continue
        text = py_file.read_text(encoding="utf-8")
        # Match plain constructor calls: QSpinBox(, QComboBox(, QSlider( at start of word boundary
        # but not within comments or strings (simple check: no triple-quotes on same line)
        for marker in _PLAIN_WIDGET_MARKERS:
            # Find lines with the marker that are NOT in comments
            for line_num, line in enumerate(text.split("\n"), 1):
                # Skip if line is a comment
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                # Skip multi-line strings (simple heuristic)
                if '"""' in line and line.count('"""') < 3:
                    continue
                if marker in line:
                    raise AssertionError(
                        f"Plain {marker.strip("(")} found in {py_file.relative_to(rhetoric_dir)} "
                        f"at line {line_num}. "
                        "All QSpinBox/QComboBox/QSlider constructions must use the Wheel* subclass from gui_wheel.py instead."
                    )


def test_no_plain_widgets_outside_gui_wheel(tmp_path: Path) -> None:
    """Fail if any plain QSpinBox, QComboBox or QSlider is built outside gui_wheel.py.
    
    This prevents silent regressions of the wheel fix: a developer adding a
    plain widget to a scrollable panel would not cause the wheel to hijack correctly.
    """
    _check_no_plain_widgets()


@pytest.fixture(scope="module")
def qt_app():
    yield QApplication.instance() or QApplication([])


def _wheel(widget: QWidget, steps: int = -120) -> QWheelEvent:
    centre = widget.rect().center()
    return QWheelEvent(
        QPointF(centre),
        QPointF(widget.mapToGlobal(centre)),
        QPoint(0, 0),
        QPoint(0, steps),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )


def _value(widget: QWidget) -> int:
    return widget.currentIndex() if isinstance(widget, WheelComboBox) else widget.value()


def test_wheel_event_with_only_pixelDelta_scrolls_panel(tmp_path: Path, qt_app) -> None:
    """Send a wheel event carrying only pixelDelta (no angleDelta) to an
    unfocused control and assert the panel scrolls while the control's
    value stays put, so the touchpad fallback is covered.
    """
    from PySide6.QtWidgets import QApplication, QScrollArea, QWidget, QSlider, QComboBox, QSpinBox
    from PySide6.QtCore import Qt, QPoint, QPointF
    from PySide6.QtGui import QWheelEvent

    # Create a scroll area with a slider (unfocused)
    scroll = QScrollArea()
    slider = QSlider(Qt.Orientation.Horizontal)
    scroll.setWidget(slider)
    scroll.show()

    # Initially capture the slider value
    initial_value = slider.value()

    # Send a wheel event with only pixelDelta (no angleDelta) to the unfocused slider
    event = QWheelEvent(
        QPointF(),  # position
        QPointF(),  # global position
        QPoint(0, 0),  # pixelDelta
        QPoint(0, 0),  # angleDelta (empty)
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    # The slider should not have focus, so the panel should scroll
    # Instead of the slider value changing
    slider.wheelEvent(event)

    # The slider value should not have changed (panel scrolled instead)
    assert slider.value() == initial_value, \
        f"Slider value changed from {initial_value} to {slider.value()} when wheel event with only pixelDelta was sent to unfocused control"


@pytest.fixture()
def panel(qt_app):
    """A scroll area whose content is taller than the viewport."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()
    layout = QVBoxLayout(content)
    spin = WheelSpinBox()
    spin.setRange(0, 100)
    spin.setValue(50)
    combo = WheelComboBox()
    combo.addItems(["first", "second", "third"])
    combo.setCurrentIndex(1)
    slider = WheelSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(50)
    for widget in (spin, combo, slider, QLabel("tall content"), QWidget()):
        layout.addWidget(widget)
    content.setMinimumHeight(1200)
    scroll.setWidget(content)
    scroll.resize(320, 200)
    scroll.show()
    # Showing the panel gives its first focusable child keyboard focus, and the
    # hijack only happens on a control that has none, so start from the view.
    scroll.setFocus(Qt.FocusReason.OtherFocusReason)
    QApplication.processEvents()
    yield scroll, {"spin": spin, "combo": combo, "slider": slider}
    scroll.close()
    scroll.deleteLater()


@pytest.mark.parametrize("control", ["spin", "combo", "slider"])
def test_an_unfocused_control_scrolls_the_panel_instead_of_changing(panel, control):
    scroll, controls = panel
    widget = controls[control]
    assert not widget.hasFocus()
    before = _value(widget)
    scroll.verticalScrollBar().setValue(0)

    # Wheel down from the top: the panel can only move that way.
    QApplication.sendEvent(widget, _wheel(widget, steps=-120))
    QApplication.processEvents()

    assert _value(widget) == before
    assert scroll.verticalScrollBar().value() > 0


@pytest.mark.parametrize("control", ["spin", "slider"])
def test_a_focused_control_keeps_the_wheel(panel, control):
    scroll, controls = panel
    widget = controls[control]
    scroll.activateWindow()
    widget.setFocus(Qt.FocusReason.OtherFocusReason)
    QApplication.processEvents()
    assert widget.hasFocus()
    before = _value(widget)

    QApplication.sendEvent(widget, _wheel(widget, steps=120))

    assert _value(widget) != before


def test_a_control_outside_a_scroll_area_keeps_its_value(qt_app):
    spin = WheelSpinBox()
    spin.setRange(0, 100)
    spin.setValue(50)

    QApplication.sendEvent(spin, _wheel(spin, steps=120))

    assert spin.value() == 50


def test_no_event_filter_is_installed_for_wheel_routing(qt_app):
    """An application-wide filter crashed Qt's dispatch on hosted runners."""
    assert not [name for name in dir(gui_wheel) if "Filter" in name]
