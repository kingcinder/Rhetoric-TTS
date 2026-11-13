"""Mouse-wheel routing: scrollable panels scroll unless a control has focus.

The owner's report: wheeling over a spin box / combo box / slider in a
scrollable settings panel changed the control's value instead of scrolling the
view, and the view often would not scroll at all until the user clicked off the
control. The guard in rhetoric.gui_wheel fixes that globally; these tests pin
both halves of the rule (unfocused control => view scrolls, value untouched;
focused control => the control keeps the wheel).
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from rhetoric.gui_wheel import WheelFocusGuard, install_wheel_focus_guard


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


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


@pytest.fixture()
def panel(qt_app):
    """A scroll area whose content is taller than the viewport."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()
    layout = QVBoxLayout(content)
    spin = QSpinBox()
    spin.setRange(0, 100)
    spin.setValue(50)
    combo = QComboBox()
    combo.addItems(["first", "second", "third"])
    combo.setCurrentIndex(1)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(50)
    layout.addWidget(spin)
    layout.addWidget(combo)
    layout.addWidget(slider)
    layout.addWidget(QLabel("tall content"))
    layout.addWidget(QWidget())
    content.setMinimumHeight(1200)
    scroll.setWidget(content)
    scroll.resize(320, 200)
    scroll.show()
    QApplication.processEvents()
    # Showing the panel gives its first focusable child keyboard focus. The
    # hijack happens precisely when a control has NO focus, so start from the
    # view owning focus (a click on the panel background in real use).
    scroll.setFocus(Qt.FocusReason.OtherFocusReason)
    QApplication.processEvents()
    yield scroll, spin, combo, slider
    scroll.close()
    scroll.deleteLater()


@pytest.fixture()
def guard(qt_app):
    return install_wheel_focus_guard(qt_app)


def test_unfocused_spin_box_does_not_change_value(qt_app, panel, guard):
    scroll, spin, _combo, _slider = panel
    assert not spin.hasFocus()

    QApplication.sendEvent(spin, _wheel(spin))

    assert spin.value() == 50


def test_unfocused_control_scrolls_the_view(qt_app, panel, guard):
    scroll, spin, _combo, _slider = panel
    scroll.verticalScrollBar().setValue(0)

    QApplication.sendEvent(spin, _wheel(spin))
    QApplication.processEvents()

    assert scroll.verticalScrollBar().value() > 0


def test_unfocused_combo_box_does_not_change_selection(qt_app, panel, guard):
    _scroll, _spin, combo, _slider = panel

    QApplication.sendEvent(combo, _wheel(combo, steps=120))

    assert combo.currentIndex() == 1


def test_unfocused_slider_does_not_change_value(qt_app, panel, guard):
    _scroll, _spin, _combo, slider = panel

    QApplication.sendEvent(slider, _wheel(slider, steps=120))

    assert slider.value() == 50


def test_focused_spin_box_keeps_the_wheel(qt_app, panel, guard):
    scroll, spin, _combo, _slider = panel
    scroll.activateWindow()
    spin.setFocus(Qt.FocusReason.OtherFocusReason)
    QApplication.processEvents()
    assert spin.hasFocus()

    QApplication.sendEvent(spin, _wheel(spin, steps=120))

    assert spin.value() == 51


def test_guard_is_installed_once_per_application(qt_app):
    first = install_wheel_focus_guard(qt_app)
    second = install_wheel_focus_guard(qt_app)
    assert first is second
    assert isinstance(first, WheelFocusGuard)


def test_non_editing_widgets_are_left_alone(qt_app, panel, guard):
    scroll, _spin, _combo, _slider = panel
    label = scroll.widget().findChildren(QLabel)[0]

    # A plain label neither edits nor blocks: Qt scrolls the view itself and
    # the guard must not interfere.
    assert guard.eventFilter(label, _wheel(label)) is False
