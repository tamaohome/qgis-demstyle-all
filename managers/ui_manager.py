from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtGui import QColor
from qgis.gui import QgsRubberBand
from PyQt5.QtCore import QTimer

if TYPE_CHECKING:
    from qgis.core import QgsFeature
    from qgis.core import QgsVectorLayer
    from qgis.gui import QgisInterface

    from ..ui.demstyle_all_dialog import DEMStyleAllDialog


class UIManager:
    """UI関連処理の管理クラス"""

    def __init__(self, dialog: DEMStyleAllDialog, iface: QgisInterface) -> None:
        self.dialog = dialog
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def init_current_feature_table_widget(self) -> None:
        """地物テーブルを初期化する"""
        self.dialog.currentFeatureTableWidget.initialize()

    def update_current_feature_table_widget(self, feature: QgsFeature | None) -> None:
        """地物テーブルを更新する"""
        self.dialog.currentFeatureTableWidget.set_feature(feature)

        # 現在の設定標高と一致する場合、ハイライト表示
        self.highlight_matching_elevation(feature)

    def highlight_matching_elevation(self, feature: QgsFeature | None) -> None:
        """現在の設定標高と地物の標高が一致する場合、ハイライト表示する"""
        state = self.dialog.currentFeatureTableWidget.highlight_by_elevation(
            feature,
            self.dialog.min_elevation,
            self.dialog.max_elevation,
        )

        if state in ("invalid", "empty", "null", "mismatch"):
            self.dialog.elevation_inputs.clear_highlight()
            return

        if state == "match":
            self.dialog.elevation_inputs.set_match_highlight(True)
            return

        self.dialog.elevation_inputs.clear_highlight()

    def highlight_feature(self, feature: QgsFeature | None, layer: QgsVectorLayer | None) -> None:
        """選択中の地物をハイライト"""
        if layer is None or feature is None or not feature.isValid():
            return
        if self.canvas is None:
            return

        geometry = feature.geometry()

        highlight_color = QColor(255, 255, 0)  # 黄色
        rubber_band = QgsRubberBand(self.canvas)
        rubber_band.setToGeometry(geometry, layer)
        rubber_band.setStrokeColor(highlight_color)
        rubber_band.setWidth(3)  # ボーダー幅

        # 一定時間後に削除
        scene = self.canvas.scene()
        if scene is None:
            return
        QTimer.singleShot(200, lambda: scene.removeItem(rubber_band))
