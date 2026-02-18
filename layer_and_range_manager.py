from PyQt5.QtCore import Qt
from .base_qgis_dialog import BaseQgisDialog
from qgis.core import Qgis, QgsMapLayerType, QgsRaster, QgsPointXY
from PyQt5.QtWidgets import QListWidgetItem
from qgis.core import QgsMapLayer

DATA_RANGE_VALUES = [10, 20, 50, 100, 200, 500]


class LayerAndRangeManager:
    """レイヤ・データレンジ関連処理の管理クラス"""

    def __init__(self, dialog: BaseQgisDialog):
        self.dialog = dialog

    def refresh_target_layer_list(self) -> None:
        """標高設定対象のレイヤ一覧を更新する"""
        self.dialog.layerListWidget.clear()  # リストを初期化

        # レイヤリストをツリー順で取得
        root = self.dialog.layer_tree_root
        layers = [layer_node.layer() for layer_node in root.findLayers()]

        search_string = self.get_current_search_string()  # 検索文字列を取得

        for layer in layers:
            # レイヤの存在判定
            if not layer:
                continue

            # 検索文字列に該当しないレイヤはスキップ
            if search_string not in layer.name():
                continue

            # ラスタレイヤ判定
            if layer.type() != QgsMapLayerType.RasterLayer:
                continue

            item = QListWidgetItem(layer.name())  # 表示用のアイテムを作成
            item.setData(Qt.UserRole, layer.id())  # 内部処理用にレイヤIDを保持
            self.dialog.layerListWidget.addItem(item)  # リストに追加

    def get_target_layers(self) -> list[QgsMapLayer]:
        """標高設定対象のレイヤ配列を取得する"""
        layers = []
        for i in range(self.dialog.layerListWidget.count()):
            item = self.dialog.layerListWidget.item(i)
            layer_id = item.data(Qt.UserRole)
            layer = self.dialog.project.mapLayer(layer_id)
            if layer is not None:
                layers.append(layer)
        return layers

    def handle_slider_change(self, index: int) -> None:
        """スライダーの値（インデックス）変更時の処理"""
        try:
            # リストから実数値を取得
            actual_value = DATA_RANGE_VALUES[index]
            # LineEditに文字列として反映
            self.dialog.dataRangeLineEdit.setText(str(actual_value))
            # 最小値／最大値を更新
            self.dialog.elevation_manager.on_mid_elevation_changed()
        except IndexError:
            pass

    def get_current_data_range(self) -> int:
        """現在のデータレンジを取得する"""
        index = self.dialog.dataRangeSlider.value()
        return DATA_RANGE_VALUES[index]

    def get_current_search_string(self) -> str:
        """現在の検索文字列を取得する"""
        return self.dialog.search_string

    def get_elevation_from_target_layers(self, point: QgsPointXY) -> float | None:
        """全てのターゲットレイヤから標高を取得する"""
        # ターゲットレイヤ配列を取得
        layers = self.get_target_layers()

        for layer in layers:
            # クリック地点の標高値を取得
            provider = layer.dataProvider()
            if not provider:
                continue

            res = provider.identify(point, QgsRaster.IdentifyFormatValue)
            if not res.isValid():
                continue

            # 結果は辞書形式 {バンド番号: 値} で返される (通常、DEMは第1バンド)
            results = res.results()
            elevation = results.get(1)  # バンド1の値を取得

            if elevation is not None:
                return elevation

        # 標高値の取得に失敗した場合 None を返す
        return None

    def handle_get_elevation(self, point: QgsPointXY, button: int) -> None:
        """標高を取得後の処理"""
        self.dialog.canvas.unsetMapTool(self.dialog.map_tool)  # ツールを解除

        # 標高取得後にダイアログを最前面に表示
        self.dialog.raise_()
        self.dialog.activateWindow()

        # 全ターゲットレイヤから標高を取得
        elevation = self.get_elevation_from_target_layers(point)

        if elevation is None:
            title = "警告"
            message = "標高値の取得に失敗しました"
            self.dialog.message_bar.pushMessage(title, message, level=Qgis.MessageLevel.Warning, duration=3)
            return

        # 標高中心を5単位で数字丸め
        mid_elevation = round(elevation / 5) * 5

        # スピンボックスに値をセット
        self.dialog.midElevationSpinBox.setValue(mid_elevation)

        # OKボタンの状態を更新
        self.dialog._update_ok_button_state()

        # マップツールが変更されている場合は元に戻す
        if self.dialog.previous_map_tool is not None:
            self.dialog.canvas.setMapTool(self.dialog.previous_map_tool)
