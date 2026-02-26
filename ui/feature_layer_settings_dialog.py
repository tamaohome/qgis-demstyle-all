from __future__ import annotations

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton


class FeatureLayerSettingsDialog(QDialog):
    """地物レイヤの設定ダイアログ"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("地物レイヤの設定")
        self.setModal(True)
        self.setMinimumWidth(300)

        # レイアウトの作成
        layout = QVBoxLayout()

        # ボタンのレイアウト
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("キャンセル")
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # シグナルの接続
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        # LineEditにフォーカスを設定
        self.line_edit.setFocus()
        self.line_edit.selectAll()
