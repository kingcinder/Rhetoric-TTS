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

# The three controls the wheel fix subclasses. A plain one in a scrollable panel
# silently restores the value hijack, so src/rhetoric may only build these three
# names inside gui_wheel.py (as the subclasses' bases).
_PLAIN_WHEEL_WIDGETS = frozenset({"QSpinBox", "QComboBox", "QSlider"})


def _check_no_plain_widgets() -> None:
    """Fail if src/rhetoric constructs a plain QSpinBox, QComboBox or QSlider.

    Parses with ``ast`` rather than grepping lines: docstrings, comments and
    multi-line stylesheet strings mention these names (gui_themes.py does), so a
    line scan both misses real calls inside multi-line expressions and flags
    text. A call whose callee is one of the three names anywhere but
    gui_wheel.py is a regression of the wheel fix.
    """
    import ast
    from pathlib import Path

    rhetoric_dir = Path(__file__).resolve().parents[1] / "src" / "rhetoric"
    offenders: list[str] = []
    for py_file in sorted(rhetoric_dir.rglob("*.py")):
        if py_file.name == "gui_wheel.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            else:
                continue
            if name in _PLAIN_WHEEL_WIDGETS:
                offenders.append(f"{py_file.relative_to(rhetoric_dir)}:{node.lineno}: {name}()")
    assert not offenders, (
        "plain wheel-sensitive widgets built outside gui_wheel.py; use "
        "WheelSpinBox/WheelComboBox/WheelSlider instead: " + ", ".join(offenders)
    )


def test_no_plain_widgets_outside_gui_wheel() -> None:
    """A plain QSpinBox/QComboBox/QSlider outside gui_wheel.py re-breaks the wheel."""
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


def _wheel_pixels(widget: QWidget, pixels: int = -120) -> QWheelEvent:
    """A wheel event with pixelDelta only, as a smooth touchpad sends it."""
    centre = widget.rect().center()
    return QWheelEvent(
        QPointF(centre),
        QPointF(widget.mapToGlobal(centre)),
        QPoint(0, pixels),
        QPoint(0, 0),  # no angleDelta: the notched-wheel half is absent
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )


def test_a_pixel_delta_only_wheel_scrolls_the_panel(qt_app) -> None:
    """A touchpad wheel over an unfocused control scrolls the panel.

    ``_WheelScrollsPanel.wheelEvent`` falls back to ``pixelDelta().y()`` when
    ``angleDelta`` is empty. The control's value must not move and the panel
    must move, which is the touchpad half of the fix.
    """
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()
    layout = QVBoxLayout(content)
    slider = WheelSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(50)
    layout.addWidget(slider)
    content.setMinimumHeight(1200)
    scroll.setWidget(content)
    scroll.resize(320, 200)
    scroll.show()
    scroll.setFocus(Qt.FocusReason.OtherFocusReason)
    QApplication.processEvents()

    assert not slider.hasFocus()
    before = slider.value()
    scroll.verticalScrollBar().setValue(0)

    QApplication.sendEvent(slider, _wheel_pixels(slider, pixels=-120))
    QApplication.processEvents()

    assert slider.value() == before, "the unfocused slider must not consume the wheel"
    assert scroll.verticalScrollBar().value() > 0, "the panel must scroll on pixelDelta"
    scroll.close()
    scroll.deleteLater()


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


class _FocusedWheelSpinBox(WheelSpinBox):
    """A spin box that reports focus without a window manager granting it.

    ``setFocus`` only takes effect in an active window. On this desktop's xcb
    session the test window is never activated (another window holds focus), so
    the real focused branch was unreachable there even though it worked under
    offscreen. The rule under test is the mixin's branch on ``hasFocus()``, so
    report it directly and keep the test independent of window activation.
    """

    def hasFocus(self) -> bool:  # noqa: N802 (Qt casing)
        return True


class _FocusedWheelSlider(WheelSlider):
    """A slider that reports focus; see ``_FocusedWheelSpinBox``."""

    def hasFocus(self) -> bool:  # noqa: N802 (Qt casing)
        return True


@pytest.mark.parametrize(
    "widget_type", [_FocusedWheelSpinBox, _FocusedWheelSlider], ids=["spin", "slider"]
)
def test_a_focused_control_keeps_the_wheel(qt_app, widget_type):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()
    layout = QVBoxLayout(content)
    widget = widget_type()
    widget.setRange(0, 100)
    widget.setValue(50)
    layout.addWidget(widget)
    content.setMinimumHeight(1200)
    scroll.setWidget(content)
    scroll.resize(320, 200)
    scroll.show()
    QApplication.processEvents()

    assert widget.hasFocus()
    before = widget.value()
    scroll.verticalScrollBar().setValue(0)

    QApplication.sendEvent(widget, _wheel(widget, steps=120))
    QApplication.processEvents()

    assert widget.value() != before, "a focused control must keep the wheel"
    assert scroll.verticalScrollBar().value() == 0, (
        "a focused control must not hand the wheel to the panel"
    )
    scroll.close()
    scroll.deleteLater()


def test_a_control_outside_a_scroll_area_keeps_its_value(qt_app):
    spin = WheelSpinBox()
    spin.setRange(0, 100)
    spin.setValue(50)

    QApplication.sendEvent(spin, _wheel(spin, steps=120))

    assert spin.value() == 50


def test_no_event_filter_is_installed_for_wheel_routing(qt_app):
    """An application-wide filter crashed Qt's dispatch on hosted runners."""
    assert not [name for name in dir(gui_wheel) if "Filter" in name]
