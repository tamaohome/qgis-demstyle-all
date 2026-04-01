from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QWidget


class ElevationInputWidget(QWidget):
    """min/mid/max の標高入力を 1 つにまとめたカスタムウィジェット。"""

    def __init__(self, parent=None):
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

    @staticmethod
    def _build_spin_box() -> QSpinBox:
        spin = QSpinBox()
        spin.setMinimum(-9999)
        spin.setMaximum(9999)
        spin.setSingleStep(5)
        spin.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        return spin
