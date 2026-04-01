from __future__ import annotations

from collections.abc import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QWidget


class ElevationInputWidget(QWidget):
    """min/mid/max の標高入力を 1 つにまとめたカスタムウィジェット。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.min_spin_box = self._build_spin_box()
        self.mid_spin_box = self._build_spin_box()
        self.max_spin_box = self._build_spin_box()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.min_spin_box)
        layout.addWidget(self.mid_spin_box)
        layout.addWidget(self.max_spin_box)
        self.setLayout(layout)

    @property
    def min_value(self) -> int:
        return self.min_spin_box.value()

    @property
    def mid_value(self) -> int:
        return self.mid_spin_box.value()

    @property
    def max_value(self) -> int:
        return self.max_spin_box.value()

    def set_read_only(self, read_only: bool) -> None:
        self.min_spin_box.lineEdit().setReadOnly(read_only)
        self.mid_spin_box.lineEdit().setReadOnly(read_only)
        self.max_spin_box.lineEdit().setReadOnly(read_only)

    def connect_value_changed(
        self,
        on_min_changed: Callable[[int], None],
        on_mid_changed: Callable[[int], None],
        on_max_changed: Callable[[int], None],
    ) -> None:
        self.min_spin_box.valueChanged.connect(on_min_changed)
        self.mid_spin_box.valueChanged.connect(on_mid_changed)
        self.max_spin_box.valueChanged.connect(on_max_changed)

    def set_values_blocking(self, min_value: int, mid_value: int, max_value: int) -> None:
        self.min_spin_box.blockSignals(True)
        self.mid_spin_box.blockSignals(True)
        self.max_spin_box.blockSignals(True)
        try:
            self.min_spin_box.setValue(min_value)
            self.mid_spin_box.setValue(mid_value)
            self.max_spin_box.setValue(max_value)
        finally:
            self.min_spin_box.blockSignals(False)
            self.mid_spin_box.blockSignals(False)
            self.max_spin_box.blockSignals(False)

    def set_match_highlight(self, enabled: bool) -> None:
        if enabled:
            color_hex = "#d6f4ff"
            style = f"QSpinBox {{ background-color: {color_hex}; }}"
            self.min_spin_box.setStyleSheet(style)
            self.max_spin_box.setStyleSheet(style)
            return
        self.clear_highlight()

    def clear_highlight(self) -> None:
        self.min_spin_box.setStyleSheet("")
        self.max_spin_box.setStyleSheet("")

    def set_mid_value(self, mid_value: int) -> None:
        self.mid_spin_box.setValue(mid_value)

    def step_mid_up(self) -> None:
        self.mid_spin_box.stepUp()

    def step_mid_down(self) -> None:
        self.mid_spin_box.stepDown()

    @staticmethod
    def _build_spin_box() -> QSpinBox:
        spin = QSpinBox()
        spin.setMinimum(-9999)
        spin.setMaximum(9999)
        spin.setSingleStep(5)
        spin.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        return spin
