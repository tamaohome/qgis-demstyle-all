from PyQt5.QtWidgets import QComboBox
from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsVectorLayer

from .ui_manager import FEATURE_HEADERS


class FeatureLayerComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_layers()

    def refresh_layers(self):
        """地物レイヤをロードする"""
        # 現在の選択を記憶（更新後に復元するため）
        prev_id = self.currentData()

        self.clear()

        # インスタンスを取得
        ins = QgsProject.instance()
        if not ins:
            return

        root = ins.layerTreeRoot()
        if not root:
            message = "レイヤツリーの取得に失敗しました。"
            QgsMessageLog.logMessage(message, "demstyle_all", Qgis.MessageLevel.Critical)
            return
        ordered_nodes = root.findLayers()

        for node in ordered_nodes:
            layer = node.layer()

            # レイヤの存在判定
            if not layer:
                continue

            # ベクタレイヤ判定
            if not isinstance(layer, QgsVectorLayer):
                continue

            # 地物の存在判定
            if not layer.featureCount():
                continue

            # 属性テーブルのヘッダー名判定
            if not self._has_header(layer, FEATURE_HEADERS):
                continue

            self.addItem(layer.name(), layer.id())

        # 以前選択していたレイヤがあれば再選択
        if prev_id:
            index = self.findData(prev_id)
            if index >= 0:
                self.setCurrentIndex(index)

    @property
    def current_layer(self) -> QgsVectorLayer | None:
        """現在選択中のレイヤオブジェクトを返す"""
        try:
            layer_id = self.currentData()
            project = QgsProject.instance()
            if not project:
                return None
            layer = project.mapLayer(layer_id)
            assert isinstance(layer, QgsVectorLayer)
            return layer
        except Exception:
            return None

    def _has_header(self, layer, header: list[str]) -> bool:
        layer_field_names = [field.name() for field in layer.fields()]
        return all(name in layer_field_names for name in header)
