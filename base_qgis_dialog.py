from PyQt5.QtWidgets import QDialog
from qgis.core import QgsFeature, QgsLayerTree, QgsMapLayer, QgsProject, QgsVectorLayer
from qgis.gui import QgisInterface, QgsLayerTreeView, QgsMapCanvas, QgsMessageBar


class BaseQgisDialog(QDialog):
    """QGISプラグイン共通のダイアログベースクラス"""

    def __init__(self, iface: QgisInterface, parent=None):
        super().__init__(parent)
        self._iface = iface
        self._current_feature: QgsFeature | None = None

    @property
    def project(self) -> QgsProject:
        """QGISプロジェクトインスタンス"""
        inst = QgsProject.instance()
        if inst is None:
            raise RuntimeError("QGISプロジェクトのインスタンス取得に失敗しました。")
        return inst

    @property
    def message_bar(self) -> QgsMessageBar:
        """QGISメッセージバー"""
        bar = self._iface.messageBar()
        if bar is None:
            raise RuntimeError("QGISメッセージバーが利用できません。")
        return bar

    @property
    def canvas(self) -> QgsMapCanvas:
        """QGISメインキャンバス"""
        c = self.iface.mapCanvas()
        if c is None:
            raise RuntimeError("QGISマップキャンバスが取得できません。")
        return c

    @property
    def layer_tree_view(self) -> QgsLayerTreeView:
        """QGISレイヤツリービュー"""
        view = self.iface.layerTreeView()
        if view is None:
            raise RuntimeError("レイヤツリービューを取得できません。")
        return view

    @property
    def layer_tree_root(self) -> QgsLayerTree:
        """QGISレイヤツリー ルートノード"""
        root = self.project.layerTreeRoot()
        if root is None:
            raise RuntimeError("レイヤツリーのルートノードを取得できません。")
        return root

    @property
    def iface(self) -> QgisInterface:
        """QGISインターフェース"""
        return self._iface

    @property
    def current_layer(self) -> QgsMapLayer | None:
        """現在選択中のレイヤ"""
        return self.iface.activeLayer()

    @property
    def current_vector_layer(self) -> QgsVectorLayer | None:
        """現在選択中のベクタレイヤ"""
        if not isinstance(self.current_layer, QgsVectorLayer):
            return None
        return self.current_layer

    @property
    def current_feature(self) -> QgsFeature | None:
        """現在選択中のフィーチャ（属性テーブルのレコード）"""
        layer = self.current_layer
        if not isinstance(layer, QgsVectorLayer):
            return None

        selected = layer.selectedFeatures()
        return selected[0] if selected else None

    @current_feature.setter
    def current_feature(self, feature: QgsFeature) -> None:
        self._current_feature = feature
