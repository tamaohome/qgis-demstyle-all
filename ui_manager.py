from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsRubberBand
from qgis.PyQt.QtWidgets import QTableWidgetItem

FEATURE_HEADERS = ["No", "標高下", "標高上"]


class UIManager:
    """UI関連処理の管理クラス"""

    def __init__(self, dialog, iface):
        self.dialog = dialog
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def init_current_feature_table_widget(self) -> None:
        """地物テーブルを初期化する"""
        self.dialog.currentFeatureTableWidget.clear()
        self.dialog.currentFeatureTableWidget.setRowCount(0)
        self.dialog.currentFeatureTableWidget.setColumnCount(3)

        # 行番号を非表示
        self.dialog.currentFeatureTableWidget.verticalHeader().setVisible(False)

        # ヘッダを設定
        self.dialog.currentFeatureTableWidget.setHorizontalHeaderLabels(FEATURE_HEADERS)

        # 列幅を設定
        self.dialog.currentFeatureTableWidget.setColumnWidth(0, 96)
        self.dialog.currentFeatureTableWidget.setColumnWidth(1, 52)
        self.dialog.currentFeatureTableWidget.setColumnWidth(2, 52)

    def update_current_feature_table_widget(self, feature) -> None:
        """地物テーブルを更新する"""
        # テーブル行を初期化
        self.dialog.currentFeatureTableWidget.setRowCount(0)

        # 選択中の地物が存在しない場合は中止
        if not feature or not feature.isValid():
            return

        # 1行データを取得
        feature_no = feature.attribute("No")
        min_elev_raw = feature.attribute("標高下")
        max_elev_raw = feature.attribute("標高上")

        # 標高値を検証（5の倍数に丸める）
        min_elev = self._validate_elevation_value(min_elev_raw)
        max_elev = self._validate_elevation_value(max_elev_raw)

        # テーブルに1行追加
        self.dialog.currentFeatureTableWidget.insertRow(0)

        # 各セルにデータを設定
        self.dialog.currentFeatureTableWidget.setItem(0, 0, QTableWidgetItem(str(feature_no)))
        self.dialog.currentFeatureTableWidget.setItem(0, 1, self._create_numeric_table_item(min_elev))
        self.dialog.currentFeatureTableWidget.setItem(0, 2, self._create_numeric_table_item(max_elev))

        # 現在の設定標高と一致する場合、ハイライト表示
        self.highlight_matching_elevation(feature)

    def highlight_matching_elevation(self, feature) -> None:
        """現在の設定標高と地物の標高が一致する場合、ハイライト表示する"""
        if not feature or not feature.isValid():
            return

        # テーブルに行が存在しない場合は中止
        if self.dialog.currentFeatureTableWidget.rowCount() == 0:
            return

        # 1行データを取得
        min_elev = feature.attribute("標高下")
        max_elev = feature.attribute("標高上")

        # 現在の設定標高と一致する場合、ハイライト表示
        if min_elev == self.dialog.min_elevation and max_elev == self.dialog.max_elevation:
            cyan_color_hex = "#d6f4ff"
            # 地物テーブルをハイライト
            self.dialog.currentFeatureTableWidget.item(0, 1).setBackground(QColor(cyan_color_hex))
            self.dialog.currentFeatureTableWidget.item(0, 2).setBackground(QColor(cyan_color_hex))

            # スピンボックスをハイライト
            self.dialog.minElevationSpinBox.setStyleSheet(
                f"QSpinBox {{ background-color: {cyan_color_hex}; }}"
            )
            self.dialog.maxElevationSpinBox.setStyleSheet(
                f"QSpinBox {{ background-color: {cyan_color_hex}; }}"
            )
        else:
            # マッチしていない場合はスタイルをリセット
            if self.dialog.currentFeatureTableWidget.rowCount() > 0:
                self.dialog.currentFeatureTableWidget.item(0, 1).setBackground(QColor(Qt.white))
                self.dialog.currentFeatureTableWidget.item(0, 2).setBackground(QColor(Qt.white))
            self.dialog.minElevationSpinBox.setStyleSheet("")
            self.dialog.maxElevationSpinBox.setStyleSheet("")

    def highlight_feature(self, feature, layer) -> None:
        """選択中の地物をハイライト"""
        if not layer or not feature or not feature.isValid():
            return

        geometry = feature.geometry()

        highlight_color = QColor(255, 255, 0)  # 黄色
        rubber_band = QgsRubberBand(self.canvas)
        rubber_band.setToGeometry(geometry, layer)
        rubber_band.setStrokeColor(highlight_color)
        rubber_band.setWidth(3)  # ボーダー幅

        # 一定時間後に削除
        QTimer.singleShot(200, lambda: self.canvas.scene().removeItem(rubber_band))

    @staticmethod
    def _create_numeric_table_item(value) -> QTableWidgetItem:
        """数値セルを作成する（右揃え、無効な値は"-"を表示）"""
        try:
            text = str(int(value)) if value is not None else "-"
        except (ValueError, TypeError):
            text = "-"

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item

    @staticmethod
    def _validate_elevation_value(value: float) -> int:
        """標高値を検証し、5の倍数に丸める"""
        try:
            validated = round(value / 5) * 5
            return int(validated)
        except (ValueError, TypeError):
            return 0
