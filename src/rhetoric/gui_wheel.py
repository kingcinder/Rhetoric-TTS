"""Wheel routing for scrollable panels: the view scrolls unless a control has focus.

Qt delivers a wheel event to the widget under the cursor. A spin box, combo box
or slider accepts that event, so the control's value changes and the enclosing
scroll area never moves -- the "mouse wheel hijack" the owner reported.

The rule is implemented by the control, not by an event filter: an unfocused
control ignores the wheel, and Qt then propagates it to the enclosing scroll
area, which is what the gesture meant. A focused control keeps the event,
because a focused control is being edited deliberately.

Event filters were tried first and abandoned: an application-wide filter (and
then a per-widget one) crashed both hosted platforms with an access violation
inside the filter dispatch while windows were being built and torn down. The
subclass route touches no dispatch machinery at all -- only the controls this
application constructs.
"""

from __future__ import annotations

from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QComboBox,
    QDoubleSpinBox,
    QSlider,
    QSpinBox,
)


class _FocusGatedWheel:
    """Mixin: keep the wheel only while focused, else let the panel have it."""

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802 - Qt's name
        if self.hasFocus():  # type: ignore[attr-defined]
            super().wheelEvent(event)  # type: ignore[misc]
        else:
            # Scroll the enclosing view directly. Qt's own propagation of an
            # ignored wheel is only reliable for platform-delivered events, and
            # the behaviour must be identical for a synthetic one.
            area = self._enclosing_scroll_area()
            delta = event.angleDelta().y()
            if area is not None and delta:
                bar = area.verticalScrollBar()
                bar.setValue(bar.value() - delta)
                event.accept()
            else:
                event.ignore()

    def _enclosing_scroll_area(self) -> QAbstractScrollArea | None:
        parent = self.parentWidget()  # type: ignore[attr-defined]
        while parent is not None:
            if isinstance(parent, QAbstractScrollArea):
                return parent
            parent = parent.parentWidget()
        return None


class WheelSpinBox(_FocusGatedWheel, QSpinBox):
    """``QSpinBox`` whose wheel scrolls the panel unless the box has focus."""


class WheelDoubleSpinBox(_FocusGatedWheel, QDoubleSpinBox):
    """``QDoubleSpinBox`` whose wheel scrolls the panel unless it has focus."""


class WheelComboBox(_FocusGatedWheel, QComboBox):
    """``QComboBox`` whose wheel scrolls the panel unless the box has focus."""


class WheelSlider(_FocusGatedWheel, QSlider):
    """``QSlider`` whose wheel scrolls the panel unless the slider has focus."""
