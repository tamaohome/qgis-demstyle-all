from PyQt5.QtWidgets import QDialog
from qgis.core import QgsLayerTree, QgsProject
from abc import ABC

from qgis.gui import QgisInterface, QgsLayerTreeView, QgsMapCanvas, QgsMessageBar


class BaseQgisDialog(QDialog, ABC):
    """QGISプラグイン共通のダイアログベースクラス"""

    def __init__(self, iface: QgisInterface, parent=None):
        super().__init__(parent)
        self._iface = iface

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
        root = self.iface.layerTreeRoot()
        if root is None:
            raise RuntimeError("レイヤツリーのルートノードを取得できません。")
        return root

    @property
    def iface(self) -> QgisInterface:
        """QGISインターフェース"""
        return self._iface
