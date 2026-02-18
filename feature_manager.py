from .base_qgis_dialog import BaseQgisDialog
from qgis.core import QgsMapLayerType
from qgis.core import Qgis
from qgis.core import QgsFeature

from .layer_and_range_manager import DATA_RANGE_VALUES


class FeatureManager:
    """地物関連処理の管理クラス"""

    def __init__(self, dialog: BaseQgisDialog, iface):
        self.dialog = dialog
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def on_attribute_selection_changed(self):
        """属性テーブルの選択変更時の処理"""
        # ウィンドウが非表示の場合は中止
        if not self.dialog.isVisible():
            return

        # 現在のレイヤを取得
        layer = self.dialog.current_layer
        if not layer:
            return

        # 選択済み地物を取得
        selected_ids = layer.selectedFeatureIds()
        if not selected_ids:
            return

        # 最初の選択済み地物を取得
        feature_id = selected_ids[0]

        # 地物オブジェクトを取得
        self.dialog.current_feature = layer.getFeature(feature_id)
        feature = self.dialog.current_feature
        if not feature:
            return
        if not feature.isValid():
            return

        # "No"列のデータを取得
        feature_no = feature.attribute("No")

        # メッセージバーを表示
        title = "地物選択変更"
        message = f"レイヤ={layer.name()}, 地物No={feature_no}"
        self.iface.messageBar().pushMessage(title, message, level=Qgis.MessageLevel.Info, duration=1)

        # 選択(黄色フィル表示)を解除
        layer.removeSelection()

        # 標高設定を更新
        self.load_elevation_settings(feature)

        # 地物テーブルを更新
        self.dialog.ui_manager.update_current_feature_table_widget(feature)

        # 地物にパン
        self.pan_to_feature()

        # 地物を強調表示
        self.dialog.ui_manager.highlight_feature(feature, layer)

        # ダイアログを最前面に表示
        self.dialog.raise_()
        self.dialog.activateWindow()

    def load_elevation_settings(self, feature: QgsFeature) -> None:
        """標高設定およびデータレンジを更新"""
        # チェックボックスで無効化の場合は中止
        if not self.dialog.enableCurrentFeatureElevCheckBox.isChecked():
            return

        # 標高を取得 (失敗する場合は中止)
        try:
            min_elev = feature.attribute("標高下")
            max_elev = feature.attribute("標高上")
            mid_elev = round((min_elev + max_elev) / 2)
        except Exception:
            return

        # データレンジを設定
        data_range = round((max_elev - min_elev) / 2)
        data_range_idx = DATA_RANGE_VALUES.index(data_range)
        self.dialog.dataRangeSlider.setValue(data_range_idx)

        # 標高中心を設定
        self.dialog.midElevationSpinBox.setValue(mid_elev)

    def pan_to_feature(self) -> None:
        """地物の中心にキャンバスをパンする"""
        # 「地物中心にパン」が有効化されていない場合は中止
        if not self.dialog.enableAutoPanCheckBox.isChecked():
            return

        # 選択中の地物が存在しない場合は中止
        if not self.dialog.current_feature:
            return
        if not self.dialog.current_feature.isValid():
            return

        geometry = self.dialog.current_feature.geometry()
        center_point = geometry.centroid().asPoint()
        self.canvas.setCenter(center_point)
        self.canvas.refresh()

    def write_attr_elev_table(self, max_elev: int, min_elev: int) -> None:
        """属性テーブルの標高値を書き出す"""
        # 属性テーブル書き換えを有効化 がOFFの場合は中止
        if not self.dialog.enableAttrTableUpdateCheckBox.isChecked():
            return

        # 現在のレイヤを取得
        layer = self.dialog.current_layer
        if not layer:
            return

        # ベクタレイヤでない場合は中止
        if layer.type() != QgsMapLayerType.VectorLayer:
            return

        # 現在選択されている地物を取得
        feature = self.dialog.current_feature
        if not feature:
            return
        if not feature.isValid():
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

        layer.dataChanged.emit()  # 属性テーブルの表示を更新
