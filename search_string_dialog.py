from __future__ import annotations

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class SearchStringDialog(QDialog):
    """検索文字列を入力するダイアログ"""

    def __init__(self, parent=None, current_search_string: str = ""):
        super().__init__(parent)
        self.setWindowTitle("検索文字列の変更")
        self.setModal(True)
        self.setMinimumWidth(300)

        # レイアウトの作成
        layout = QVBoxLayout()

        # ラベルとLineEditのレイアウト
        input_layout = QHBoxLayout()
        label = QLabel("検索文字列：")
        self.line_edit = QLineEdit(current_search_string)
        input_layout.addWidget(label)
        input_layout.addWidget(self.line_edit)
        layout.addLayout(input_layout)

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

    def get_search_string(self) -> str:
        """入力された検索文字列を取得"""
        return self.line_edit.text()
