from __future__ import annotations

from PyQt5.QtWidgets import QSpinBox


class ElevationInputAdapter:
    """3つの標高入力スピンボックスを一体として扱うアダプタ。"""

    def __init__(self, min_spin_box: QSpinBox, mid_spin_box: QSpinBox, max_spin_box: QSpinBox):
        self.min_spin_box = min_spin_box
        self.mid_spin_box = mid_spin_box
        self.max_spin_box = max_spin_box

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

    def connect_value_changed(self, on_min_changed, on_mid_changed, on_max_changed) -> None:
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
