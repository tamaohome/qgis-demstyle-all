from PyQt5.QtGui import QColor
from qgis.gui import QgsRubberBand
from PyQt5.QtCore import QTimer


class UIManager:
    """UI関連処理の管理クラス"""

    def __init__(self, dialog, iface):
        self.dialog = dialog
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def init_current_feature_table_widget(self) -> None:
        """地物テーブルを初期化する"""
        self.dialog.currentFeatureTableWidget.initialize()

    def update_current_feature_table_widget(self, feature) -> None:
        """地物テーブルを更新する"""
        self.dialog.currentFeatureTableWidget.set_feature(feature)

        # 現在の設定標高と一致する場合、ハイライト表示
        self.highlight_matching_elevation(feature)

    def highlight_matching_elevation(self, feature) -> None:
        """現在の設定標高と地物の標高が一致する場合、ハイライト表示する"""
        state = self.dialog.currentFeatureTableWidget.highlight_by_elevation(
            feature,
            self.dialog.min_elevation,
            self.dialog.max_elevation,
        )

        if state in ("invalid", "empty", "null", "mismatch"):
            self.dialog.minElevationSpinBox.setStyleSheet("")
            self.dialog.maxElevationSpinBox.setStyleSheet("")
            return

        if state == "match":
            cyan_color_hex = "#d6f4ff"
            self.dialog.minElevationSpinBox.setStyleSheet(
                f"QSpinBox {{ background-color: {cyan_color_hex}; }}"
            )
            self.dialog.maxElevationSpinBox.setStyleSheet(
                f"QSpinBox {{ background-color: {cyan_color_hex}; }}"
            )
            return

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
