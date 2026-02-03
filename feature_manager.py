from qgis.core import QgsMapLayerType
from qgis.core import Qgis


class FeatureManager:
    """地物関連処理の管理クラス"""

    def __init__(self, dialog, iface):
        self.dialog = dialog
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def on_attribute_selection_changed(self):
        """属性テーブルの選択変更時の処理"""
        # ウィンドウが非表示の場合は中止
        if not self.dialog.isVisible():
            return

        # アクティブレイヤが存在しない場合は中止
        if self.dialog.current_layer is None:
            return

        # 選択済み地物を取得
        selected_ids = self.dialog.current_layer.selectedFeatureIds()
        if not selected_ids:
            return

        # 最初の選択済み地物を取得
        feature_id = selected_ids[0]

        # 地物オブジェクトを取得
        self.dialog._current_feature = self.dialog.current_layer.getFeature(feature_id)
        if not self.dialog._current_feature.isValid():
            return

        # "No"列のデータを取得
        feature_no = self.dialog._current_feature.attribute("No")

        # メッセージバーを表示
        title = "地物選択変更"
        message = f"レイヤ={self.dialog.current_layer.name()}, 地物No={feature_no}"
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(title, message, level=Qgis.Info, duration=3)

        # 選択(黄色フィル表示)を解除
        self.dialog.current_layer.removeSelection()

        # 地物テーブルを更新
        self.dialog.ui_manager.update_current_feature_table_widget(self.dialog._current_feature)

        # 地物にパン
        self.pan_to_feature()

        # 地物を強調表示
        self.dialog.ui_manager.highlight_feature(self.dialog._current_feature, self.dialog.current_layer)

        # ダイアログを最前面に表示
        self.dialog.raise_()
        self.dialog.activateWindow()

    def pan_to_feature(self) -> None:
        """地物の中心にキャンバスをパンする"""
        # 「盛土中心にパン」が有効化されていない場合は中止
        if not self.dialog.enableAutoPanCheckBox.isChecked():
            return

        # 選択中の地物が存在しない場合は中止
        if not self.dialog._current_feature or not self.dialog._current_feature.isValid():
            return

        geometry = self.dialog._current_feature.geometry()
        center_point = geometry.centroid().asPoint()
        self.canvas.setCenter(center_point)
        self.canvas.refresh()

    def write_attr_elev_table(self, max_elev: int, min_elev: int) -> None:
        """属性テーブルの標高値を書き出す"""
        # 現在のレイヤを取得
        try:
            layer = self.dialog.current_layer
        except Exception:
            return

        if layer is None:
            return

        # ベクタレイヤでない場合は中止
        if layer.type() != QgsMapLayerType.VectorLayer:
            return

        # 現在選択されている地物を取得
        feature = self.dialog._current_feature
        if not feature or not feature.isValid():
            return

        # フィールド名のインデックスを取得
        min_field_idx = layer.fields().indexOf("標高下")
        max_field_idx = layer.fields().indexOf("標高上")

        # フィールドが存在しない場合は中止
        if min_field_idx == -1 or max_field_idx == -1:
            return

        # 選択中の地物のみ属性を更新
        changes = {feature.id(): {min_field_idx: min_elev, max_field_idx: max_elev}}
        layer.beginEditCommand("標高値を更新")
        layer.dataProvider().changeAttributeValues(changes)
        layer.endEditCommand()
