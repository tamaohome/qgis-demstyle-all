from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem

FEATURE_HEADERS = ["No", "標高下", "標高上"]


class CurrentFeatureTableWidget(QTableWidget):
    """現在地物の表示専用テーブル。表示・検証ロジックを内包する。"""

    def initialize(self) -> None:
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(3)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(FEATURE_HEADERS)
        self.setColumnWidth(0, 96)
        self.setColumnWidth(1, 52)
        self.setColumnWidth(2, 52)

    def set_feature(self, feature) -> None:
        """地物1件を表示する。無効な地物なら内容をクリアする。"""
        self.setRowCount(0)

        if not feature or not feature.isValid():
            return

        feature_no = feature.attribute("No")
        min_elev = self.validate_elevation_value(feature.attribute("標高下"))
        max_elev = self.validate_elevation_value(feature.attribute("標高上"))

        self.insertRow(0)
        self.setItem(0, 0, QTableWidgetItem(str(feature_no)))
        self.setItem(0, 1, self._create_numeric_table_item(min_elev))
        self.setItem(0, 2, self._create_numeric_table_item(max_elev))

    def highlight_by_elevation(self, feature, min_elev: int, max_elev: int) -> str:
        """標高一致状態に応じてセル背景を更新し、状態文字列を返す。"""
        if not feature or not feature.isValid():
            return "invalid"

        if self.rowCount() == 0:
            return "empty"

        feature_min = self.validate_elevation_value(feature.attribute("標高下"))
        feature_max = self.validate_elevation_value(feature.attribute("標高上"))

        if feature_min == 0 and feature_max == 0:
            gray = QColor(Qt.lightGray)
            self.item(0, 1).setBackground(gray)
            self.item(0, 2).setBackground(gray)
            return "null"

        if feature_min == min_elev and feature_max == max_elev:
            cyan = QColor("#d6f4ff")
            self.item(0, 1).setBackground(cyan)
            self.item(0, 2).setBackground(cyan)
            return "match"

        self.item(0, 1).setBackground(QColor(Qt.white))
        self.item(0, 2).setBackground(QColor(Qt.white))
        return "mismatch"

    @staticmethod
    def _create_numeric_table_item(value) -> QTableWidgetItem:
        try:
            text = str(int(value)) if value is not None else "-"
        except (ValueError, TypeError):
            text = "-"

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item

    @staticmethod
    def validate_elevation_value(value: float) -> int:
        try:
            validated = round(value / 5) * 5
            return int(validated)
        except (ValueError, TypeError):
            return 0
