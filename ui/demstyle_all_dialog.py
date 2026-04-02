from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import override

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtGui import QShowEvent
from qgis.core import Qgis
from qgis.core import QgsFeature
from qgis.core import QgsMapLayer
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterShader
from qgis.core import QgsColorRampShader
from qgis.PyQt import uic
from qgis.gui import QgisInterface, QgsMapTool

from ..ui.base_qgis_dialog import BaseQgisDialog
from ..ui.settings import DialogSettings
from ..core import COLOR_PALETTE
from ..managers.ui_manager import UIManager
from ..managers.elevation_manager import ElevationManager
from ..managers.feature_manager import FeatureManager
from ..managers.dem_layer_and_range_manager import DEMLayerAndRangeManager
from ..managers.dialog_signal_coordinator import DialogSignalCoordinator
from ..ui.mouse_release_map_tool import MouseReleaseMapTool
from ..ui.search_string_dialog import SearchStringDialog
from ..utils import get_version

if TYPE_CHECKING:
    from ..ui.elevation_input_widget import ElevationInputWidget

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(str(Path(__file__).parent / "demstyle_all_dialog_base.ui"))


class DEMStyleAllDialog(BaseQgisDialog, FORM_CLASS):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.settings = DialogSettings()
        self.setupUi(self)

        # ウィンドウを常に手前に表示
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # ウィンドウタイトルにバージョン情報を追加
        version = get_version()
        self.setWindowTitle(f"DEMスタイル一括設定 (v{version})")

        # インスタンス変数を初期化
        self.map_tool = MouseReleaseMapTool(self.canvas)
        self.previous_map_tool: QgsMapTool | None = None  # 以前の地図ツールを保存
        self.search_string = self.settings.restore_search_string()  # 検索文字列
        self.current_feature: QgsFeature | None = None
        self._connected_selection_layer: QgsVectorLayer | None = None

        # マネージャーを初期化
        self.ui_manager = UIManager(self, iface)
        self.elevation_manager = ElevationManager(self)
        self.feature_manager = FeatureManager(self, iface)
        self.dem_layer_range_manager = DEMLayerAndRangeManager(self)
        self.signal_coordinator = DialogSignalCoordinator(self)
        self.elevation_inputs: ElevationInputWidget = self.elevationInputWidget

        # 初回起動時のデータレンジ値設定
        self.dataRangeSlider.setValue(2)

        # スピンボックスの直接入力を無効化
        self._set_elevation_spin_boxes_read_only()

        self.ui_manager.init_current_feature_table_widget()  # 地物テーブルを初期化

        self._connect_signals()
        self.refresh_layer_contexts()

        # OKボタンの初期状態を設定
        self._update_ok_button_state()

    def _set_elevation_spin_boxes_read_only(self) -> None:
        self.elevation_inputs.set_read_only(True)

    def _connect_signals(self) -> None:
        self.signal_coordinator.bind()

    def refresh_feature_layer_context(self) -> None:
        """地物レイヤ一覧を再読込し、selectionChanged 接続を同期する。"""
        self.signal_coordinator.refresh_feature_layers()

    def refresh_layer_contexts(self) -> None:
        """DEM/Feature のレイヤ更新処理をまとめて実行する。"""
        self.signal_coordinator.refresh_layer_contexts()

    def on_feature_layer_changed(self, _index: int) -> None:
        """地物レイヤ選択変更時に selectionChanged 接続を更新する。"""
        self.reconnect_current_layer_selection_signal()
        self.feature_manager.on_attribute_selection_changed()

    def reconnect_current_layer_selection_signal(self) -> None:
        """現在の地物レイヤに selectionChanged を再接続する。"""
        if self._connected_selection_layer is not None:
            try:
                self._connected_selection_layer.selectionChanged.disconnect(
                    self.feature_manager.on_attribute_selection_changed
                )
            except (TypeError, RuntimeError):
                pass

        layer = self.current_layer
        self._connected_selection_layer = layer

        if layer is not None:
            layer.selectionChanged.connect(self.feature_manager.on_attribute_selection_changed)

    def get_current_data_range(self) -> int:
        """現在のデータレンジを取得する"""
        return self.dem_layer_range_manager.get_current_data_range()

    def get_current_search_string(self) -> str:
        """現在の検索文字列を取得する"""
        return self.search_string

    def refresh_target_layer_list(self) -> None:
        """標高設定対象のレイヤ一覧を更新する"""
        self.signal_coordinator.refresh_dem_layers()

    def get_target_layers(self) -> list[QgsMapLayer]:
        """標高設定対象のレイヤ配列を取得する"""
        return self.dem_layer_range_manager.get_target_layers()

    def set_mid_elevation(self, mid_value: int) -> None:
        """標高中心を更新する。"""
        self.elevation_inputs.set_mid_value(mid_value)

    def is_current_feature_elev_enabled(self) -> bool:
        """属性テーブル標高読込の有効状態を返す。"""
        return self.enableCurrentFeatureElevCheckBox.isChecked()

    def is_auto_pan_enabled(self) -> bool:
        """地物中心パンの有効状態を返す。"""
        return self.enableAutoPanCheckBox.isChecked()

    def is_attr_table_update_enabled(self) -> bool:
        """属性テーブル書き換えの有効状態を返す。"""
        return self.enableAttrTableUpdateCheckBox.isChecked()

    @property
    def min_elevation(self) -> int:
        return self.elevation_inputs.min_value

    @property
    def mid_elevation(self) -> int:
        return self.elevation_inputs.mid_value

    @property
    def max_elevation(self) -> int:
        return self.elevation_inputs.max_value

    @property
    def has_elevation(self) -> bool:
        """標高がセットされている場合 True を返す"""
        return any([self.min_elevation, self.mid_elevation, self.max_elevation])

    @property
    def current_layer(self) -> QgsVectorLayer | None:
        return self.featureLayerComboBox.current_layer

    def _update_ok_button_state(self) -> None:
        """has_elevation の値に基づいてOKボタンの有効/無効を更新"""
        self.okButton.setEnabled(self.has_elevation)

    @override
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        # ダイアログ設定を復元
        self.settings.restore_dialog_state(self)

        # 検索文字列を復元
        search_string = self.settings.restore_search_string()
        if search_string:
            self.search_string = search_string
        self.update_search_string_label()

        # チェックボックス状態を復元
        (
            enable_attr_table_update,
            enable_auto_pan,
            enable_current_feature_elev,
        ) = self.settings.restore_checkbox_states()
        self.enableAttrTableUpdateCheckBox.setChecked(enable_attr_table_update)
        self.enableAutoPanCheckBox.setChecked(enable_auto_pan)
        self.enableCurrentFeatureElevCheckBox.setChecked(enable_current_feature_elev)

        # DEM/Feature のレイヤ一覧と接続を同期
        self.refresh_layer_contexts()

        # OKボタンへフォーカスを設定
        self.okButton.setFocus()

        # アクティブレイヤおよび選択中の地物を更新
        self.feature_manager.on_attribute_selection_changed()

        # ダイアログを最前面に表示
        self.raise_()
        self.activateWindow()

    def on_ok_clicked(self) -> None:
        """OKボタン押下時の処理"""
        # スタイルファイルをレイヤに適用
        layers = self.get_target_layers()
        self._apply_dem_style(layers)

        # 属性テーブルの標高を書き出す
        max_elev = self.max_elevation
        min_elev = self.min_elevation
        self.feature_manager.write_attr_elev_table(max_elev, min_elev)

        # 描画を更新
        self.canvas.refreshAllLayers()

    def _apply_dem_style(self, layers: list[QgsMapLayer]) -> None:
        """DEM スタイルをメモリ上のレイヤに適用"""
        min_elev = self.min_elevation
        max_elev = self.max_elevation
        pitch = 20

        for layer in layers:
            # 標高レンジに対応した色アイテムを生成
            step = (max_elev - min_elev) // pitch if pitch > 0 else 1
            values = list(range(min_elev, max_elev + 1, step))

            # カラーランプシェーダを作成
            color_shader = QgsColorRampShader()

            # 色アイテムを構築して追加
            color_items = []
            for i, color_hex in enumerate(COLOR_PALETTE):
                if i < len(values):
                    value = values[i]
                    item = QgsColorRampShader.ColorRampItem(value, QColor(color_hex), str(value))
                    color_items.append(item)

            color_shader.setColorRampItemList(color_items)
            color_shader.setColorRampType(QgsColorRampShader.Interpolated)

            # QgsRasterShader ラッパーを作成
            raster_shader = QgsRasterShader()
            raster_shader.setRasterShaderFunction(color_shader)

            # レイヤのレンダラを取得して新しいシェーダを適用
            renderer = layer.renderer()
            if renderer is not None:
                renderer.setShader(raster_shader)
                layer.triggerRepaint()

            # レイヤツリービューのシンボルを更新
            self.layer_tree_view.refreshLayerSymbology(layer.id())

        # メッセージバーに表示
        message = "DEMスタイルの設定が完了しました"
        self.message_bar.pushMessage("info", message, Qgis.MessageLevel.Info, duration=3)

    def on_cancel_clicked(self) -> None:
        """キャンセルボタン押下時の処理"""
        # マップツールが変更されている場合は元に戻す
        if self.previous_map_tool is not None:
            self.canvas.setMapTool(self.previous_map_tool)
        self.reject()  # ダイアログを閉じる

    def on_search_string_rename_button_clicked(self) -> None:
        """検索文字列の変更ボタン押下時の処理"""
        dialog = SearchStringDialog(self, self.search_string)
        if dialog.exec() == SearchStringDialog.Accepted:
            self.search_string = dialog.get_search_string()
            self.settings.save_search_string(self.search_string)
            self.update_search_string_label()
            self.refresh_layer_contexts()

    def update_search_string_label(self) -> None:
        """検索文字列ラベルを更新"""
        self.searchStringLabel.setText("検索文字列：" + self.search_string)

    def start_capture_mode(self) -> None:
        """地図キャンバス上の標高をマウスクリックで取得するモード"""
        # 選択中の地物をハイライト
        self.ui_manager.highlight_feature(self.current_feature, self.current_layer)

        # 現在の地図ツールを保存
        self.previous_map_tool = self.canvas.mapTool()

        self.canvas.setMapTool(self.map_tool)

    def _save_dialog_state(self) -> None:
        """ダイアログの設定を保存し、マップツールをリセット"""
        # マップツールが変更されている場合は元に戻す
        if self.previous_map_tool is not None:
            self.canvas.setMapTool(self.previous_map_tool)
        self.settings.save_dialog_state(self)

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        """ウィンドウを閉じる前に設定を保存"""
        self._save_dialog_state()
        event.accept()

    @override
    def reject(self) -> None:
        """ダイアログをreject時に設定を保存"""
        self._save_dialog_state()
        super().reject()

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key_W:
            self.elevation_inputs.step_mid_up()
            event.accept()
        elif key == Qt.Key_S:
            self.elevation_inputs.step_mid_down()
            event.accept()
        elif key == Qt.Key_A:
            self.dataRangeSlider.setValue(
                max(self.dataRangeSlider.minimum(), self.dataRangeSlider.value() - 1)
            )
            event.accept()
        elif key == Qt.Key_D:
            self.dataRangeSlider.setValue(
                min(self.dataRangeSlider.maximum(), self.dataRangeSlider.value() + 1)
            )
            event.accept()
        else:
            super().keyPressEvent(event)
