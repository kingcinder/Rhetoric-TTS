"""Wheel routing for scrollable panels: the view scrolls unless a control has focus.

Qt delivers a wheel event to the widget under the cursor, and a spin box, combo
box or slider accepts it, so the control's value changes and the enclosing
panel never moves -- the hijack the owner reported. These subclasses invert
that: an unfocused control passes the wheel to the enclosing scroll area, and a
focused one keeps it, because a focused control is being edited deliberately.

The rule lives in the control rather than in an event filter: application-wide
and per-widget filters both crashed Qt's dispatch on hosted runners while
windows were built and torn down. The GUI constructs only these classes; no
plain ``QSpinBox``, ``QComboBox`` or ``QSlider`` remains in ``src/rhetoric``.
"""

from __future__ import annotations

from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QAbstractScrollArea, QComboBox, QSlider, QSpinBox


class _WheelScrollsPanel:
    """Mixin: keep the wheel while focused, otherwise hand it to the panel."""

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802 (Qt casing)
        if self.hasFocus():  # type: ignore[attr-defined]
            super().wheelEvent(event)  # type: ignore[misc]
            return
        panel = self._enclosing_scroll_area()  # type: ignore[attr-defined]
        if panel is None:
            event.ignore()
            return
        # Scroll the panel here rather than ignoring the event: Qt only retries
        # an ignored wheel higher up the tree for a platform-delivered event,
        # and letting the panel handle it would add its scroll-lines setting on
        # top of the delta the user actually produced. angleDelta carries
        # notched wheels; pixelDelta carries smooth touchpads.
        delta = event.angleDelta().y() or event.pixelDelta().y()
        if delta:
            bar = panel.verticalScrollBar()
            bar.setValue(bar.value() - delta)
            event.accept()
        else:
            event.ignore()

    def _enclosing_scroll_area(self) -> QAbstractScrollArea | None:
        parent = self.parentWidget()
        while parent is not None:
            if isinstance(parent, QAbstractScrollArea):
                return parent
            parent = parent.parentWidget()
        return None


class WheelSpinBox(_WheelScrollsPanel, QSpinBox):
    """``QSpinBox`` whose wheel scrolls the panel unless the box has focus."""


class WheelComboBox(_WheelScrollsPanel, QComboBox):
    """``QComboBox`` whose wheel scrolls the panel unless the box has focus."""


class WheelSlider(_WheelScrollsPanel, QSlider):
    """``QSlider`` whose wheel scrolls the panel unless the slider has focus."""
