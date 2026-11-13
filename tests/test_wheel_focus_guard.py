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
