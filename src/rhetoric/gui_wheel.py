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

import shiboken6
from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QAbstractSpinBox,
    QComboBox,
    QSlider,
)

#: Controls that silently change their value under a wheel. ``QSlider`` is
#: named explicitly rather than covered by ``QAbstractSlider``: scroll bars are
#: sliders too, and they must keep receiving the wheel normally.
_WHEEL_EDITING_TYPES = (QAbstractSpinBox, QComboBox, QSlider)

_GUARD: "WheelFocusGuard | None" = None


def _enclosing_scroll_area(widget) -> QAbstractScrollArea | None:
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
        # An application-wide filter sees every event of every object, including
        # objects whose C++ side is already gone. Ask shiboken before any type
        # test: isinstance() on a dangling wrapper resolves its C++ type and
        # segfaults, which is how this crashed a hosted runner during window
        # construction.
        try:
            if event.type() != QEvent.Type.Wheel:
                return False
            if not shiboken6.isValid(obj) or not shiboken6.isValid(event):
                return False
            if not isinstance(obj, _WHEEL_EDITING_TYPES):
                return False
            # Focus is the permission slip: a focused control is being edited
            # deliberately (keyboard or the wheel after a click) and keeps the
            # event. Everything else routes to the enclosing view.
            if obj.hasFocus():
                return False
            area = _enclosing_scroll_area(obj)
            if area is None:
                return False
            delta = event.angleDelta().y()
            if delta:
                # Scroll the view directly instead of re-sending a Python-built
                # QWheelEvent: a constructed event has no platform device
                # behind it, and handing one to Qt's scroll machinery is not a
                # supported path.
                bar = area.verticalScrollBar()
                bar.setValue(bar.value() - delta)
            # Swallow the original so the control never applies its own step.
            return True
        except (RuntimeError, AttributeError, TypeError):
            # The widget's C++ object was deleted between delivery and filter.
            return False


def install_wheel_focus_guard(app) -> WheelFocusGuard | None:
    """Attach the wheel guard to every editing control that exists now.

    Deliberately NOT an application-wide event filter. Qt dispatches every
    event of every object through an application filter, including events for
    objects whose C++ side is already gone, and a hosted runner segfaulted
    inside that dispatch while a window was being built. Attaching to the
    controls themselves keeps the decision identical while the filter only ever
    sees events addressed to a live control it was installed on.

    Idempotent: a widget is attached once, and the same guard object serves the
    whole application (a fresh QApplication gets a fresh guard). Call it again
    after building widgets later than the window (lazy sections, dialogs).
    """
    if app is None:
        return None
    global _GUARD
    if _GUARD is None or not shiboken6.isValid(_GUARD):
        _GUARD = WheelFocusGuard()
    for widget in app.allWidgets():
        try:
            if not isinstance(widget, _WHEEL_EDITING_TYPES):
                continue
            if widget.property("_rhetoricWheelGuard"):
                continue
            widget.setProperty("_rhetoricWheelGuard", True)
            widget.installEventFilter(_GUARD)
        except RuntimeError:
            continue
    return _GUARD
