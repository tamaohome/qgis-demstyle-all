from qgis.PyQt.QtWidgets import QComboBox
from qgis.core import QgsProject, QgsMapLayerType, QgsWkbTypes, QgsVectorLayer

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

        root = QgsProject.instance().layerTreeRoot()
        ordered_nodes = root.findLayers()

        for node in ordered_nodes:
            layer = node.layer()

            # 除外判定
            if not layer:
                continue
            if layer.type() != QgsMapLayerType.VectorLayer:
                continue
            if not layer.featureCount():
                continue
            if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
                continue
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
        """現在選択されているレイヤオブジェクトを返す"""
        try:
            layer_id = self.currentData()
            layer = QgsProject.instance().mapLayer(layer_id)
            assert isinstance(layer, QgsVectorLayer)
            return layer
        except Exception:
            return None

    def _has_header(self, layer, header: list[str]) -> bool:
        layer_field_names = [field.name() for field in layer.fields()]
        return all(name in layer_field_names for name in header)
