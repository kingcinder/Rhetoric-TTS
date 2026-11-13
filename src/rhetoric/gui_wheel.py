"""Wheel routing for scrollable panels: the view scrolls unless a control has focus.

Qt delivers a wheel event to the widget under the cursor. A spin box, combo box
or slider accepts that event, so the control's value changes and the enclosing
scroll area never moves -- the "mouse wheel hijack" the owner reported. The
guard installed here lets those controls consume wheel events ONLY while they
hold keyboard focus; otherwise the event is re-delivered to the enclosing
scroll area's viewport, which is what the gesture meant.

One application-wide filter covers every scrollable settings and cast panel,
including panels that do not exist yet (lazy sections, dialog-built speaker
groups), because the route is decided per event from the widget's current
state instead of from a list of widgets registered at startup.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QSlider,
    QWidget,
)

#: Controls that silently change their value under a wheel. ``QSlider`` is
#: named explicitly rather than covered by ``QAbstractSlider``: scroll bars are
#: sliders too, and they must keep receiving the wheel normally.
_WHEEL_EDITING_TYPES = (QAbstractSpinBox, QComboBox, QSlider)

_GUARD: "WheelFocusGuard | None" = None


def _enclosing_scroll_area(widget: QWidget) -> QAbstractScrollArea | None:
    """The nearest scrollable ancestor of ``widget``, if any."""
    parent = widget.parentWidget()
    while parent is not None:
        if isinstance(parent, QAbstractScrollArea):
            return parent
        parent = parent.parentWidget()
    return None


class WheelFocusGuard(QObject):
    """Application event filter implementing the focus-gated wheel rule."""

    def eventFilter(self, obj: object, event: QEvent) -> bool:
        if event.type() != QEvent.Type.Wheel:
            return False
        if not isinstance(obj, QWidget) or not isinstance(obj, _WHEEL_EDITING_TYPES):
            return False
        try:
            # Focus is the permission slip: a focused control is being edited
            # deliberately (keyboard or the wheel after a click) and keeps the
            # event. Everything else routes to the view.
            if obj.hasFocus():
                return False
            area = _enclosing_scroll_area(obj)
            if area is None:
                return False
            # Forward a fresh event: the delivered one belongs to the control
            # and Qt has already marked it accepted by the time this filter
            # runs, so re-sending it unchanged would be refused downstream.
            forwarded = QWheelEvent(
                event.position(),
                event.globalPosition(),
                event.pixelDelta(),
                event.angleDelta(),
                event.buttons(),
                event.modifiers(),
                event.phase(),
                event.inverted(),
            )
            QApplication.sendEvent(area.viewport(), forwarded)
            # Swallow the original so the control never applies its own step.
            return True
        except RuntimeError:
            # The widget's C++ object was deleted between delivery and filter.
            return False


def install_wheel_focus_guard(app: QApplication | None) -> WheelFocusGuard | None:
    """Install the wheel guard once per application and return it.

    Idempotent: the same application keeps its existing guard. A different
    QApplication (a fresh test session) gets a new guard.
    """
    if app is None:
        return None
    global _GUARD
    if _GUARD is not None and _GUARD.parent() is app:
        return _GUARD
    _GUARD = WheelFocusGuard(app)
    app.installEventFilter(_GUARD)
    return _GUARD
