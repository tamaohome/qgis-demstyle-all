from __future__ import annotations

from pathlib import Path
from typing import override

from PyQt5.QtCore import Qt
from qgis.core import Qgis
from qgis.core import QgsMapLayer
from qgis.core import QgsVectorLayer
from qgis.PyQt import uic
from qgis.gui import QgisInterface, QgsMapTool

from .base_qgis_dialog import BaseQgisDialog
from .settings import DialogSettings
from .style_qml_creator import StyleQmlCreator
from .ui_manager import UIManager
from .elevation_manager import ElevationManager
from .feature_manager import FeatureManager
from .layer_and_range_manager import LayerAndRangeManager
from .layer_and_range_manager import DATA_RANGE_VALUES
from .mouse_release_map_tool import MouseReleaseMapTool
from .search_string_dialog import SearchStringDialog
from .utils import get_version

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
        self.search_string: str = "DEM"  # 検索文字列

        # マネージャーを初期化
        self.ui_manager = UIManager(self, iface)
        self.elevation_manager = ElevationManager(self)
        self.feature_manager = FeatureManager(self, iface)
        self.layer_range_manager = LayerAndRangeManager(self)

        # 初回起動時のデータレンジ値設定
        self.dataRangeSlider.setValue(2)
        self.dataRangeLineEdit.setText(str(DATA_RANGE_VALUES[2]))

        # スピンボックスの直接入力を無効化
        self.minElevationSpinBox.lineEdit().setReadOnly(True)
        self.midElevationSpinBox.lineEdit().setReadOnly(True)
        self.maxElevationSpinBox.lineEdit().setReadOnly(True)

        self.refresh_target_layer_list()  # レイヤ一覧を更新
        self.ui_manager.init_current_feature_table_widget()  # 地物テーブルを初期化

        # シグナル接続
        self.dataRangeSlider.valueChanged.connect(self.layer_range_manager.handle_slider_change)
        self.setElevationButton.clicked.connect(self.start_capture_mode)
        self.minElevationSpinBox.valueChanged.connect(self.elevation_manager.on_min_elevation_changed)
        self.midElevationSpinBox.valueChanged.connect(self.elevation_manager.on_mid_elevation_changed)
        self.maxElevationSpinBox.valueChanged.connect(self.elevation_manager.on_max_elevation_changed)
        self.map_tool.canvasClicked.connect(self.layer_range_manager.handle_get_elevation)
        self.okButton.clicked.connect(self.on_ok_clicked)
        self.cancelButton.clicked.connect(self.on_cancel_clicked)
        self.searchStringRenameButton.clicked.connect(self.on_search_string_rename_button_clicked)

        if self.current_layer is not None:
            self.current_layer.selectionChanged.connect(self.feature_manager.on_attribute_selection_changed)

        # OKボタンの初期状態を設定
        self._update_ok_button_state()

    def get_current_data_range(self) -> int:
        """現在のデータレンジを取得する"""
        return self.layer_range_manager.get_current_data_range()

    def get_current_search_string(self) -> str:
        """現在の検索文字列を取得する"""
        return self.search_string

    def refresh_target_layer_list(self) -> None:
        """標高設定対象のレイヤ一覧を更新する"""
        self.layer_range_manager.refresh_target_layer_list()

    def get_target_layers(self) -> list[QgsMapLayer]:
        """標高設定対象のレイヤ配列を取得する"""
        return self.layer_range_manager.get_target_layers()

    @property
    def min_elevation(self) -> int:
        return self.minElevationSpinBox.value()

    @property
    def mid_elevation(self) -> int:
        return self.midElevationSpinBox.value()

    @property
    def max_elevation(self) -> int:
        return self.maxElevationSpinBox.value()

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
    def showEvent(self, event):
        super().showEvent(event)

        # ダイアログ設定を復元
        self.settings.restore_dialog_state(self)

        # 検索文字列を復元
        search_string = self.settings.restore_search_string()
        if search_string:
            self.search_string = search_string
        self.update_search_string_label()

        # OKボタンへフォーカスを設定
        self.okButton.setFocus()

        # アクティブレイヤおよび選択中の地物を更新
        self.feature_manager.on_attribute_selection_changed()

        # ダイアログを最前面に表示
        self.raise_()
        self.activateWindow()

    def on_ok_clicked(self):
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
        """スタイルファイルをレイヤに適用"""
        qml_creator = StyleQmlCreator(self.min_elevation, self.max_elevation)

        for layer in layers:
            # レイヤーのデータソースのディレクトリパスを取得
            provider = layer.dataProvider()
            if not provider:
                continue

            # スタイルファイル (*.qml) を生成
            base_dir = Path(provider.dataSourceUri()).parent
            qml_filepath = qml_creator.create_style_qml_file(base_dir)

            # スタイルファイル (*.qml) をレイヤに適用
            layer.loadNamedStyle(str(qml_filepath))
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
            self.update_search_string_label()
            self.refresh_target_layer_list()

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
        # 検索文字列を保存
        self.settings.save_search_string(self.search_string)

        # マップツールが変更されている場合は元に戻す
        if self.previous_map_tool is not None:
            self.canvas.setMapTool(self.previous_map_tool)
        self.settings.save_dialog_state(self)

    @override
    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        self._save_dialog_state()
        event.accept()

    @override
    def reject(self):
        """ダイアログをreject時に設定を保存"""
        self._save_dialog_state()
        super().reject()

    @override
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W:
            self.midElevationSpinBox.stepUp()
            event.accept()
        elif key == Qt.Key_S:
            self.midElevationSpinBox.stepDown()
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
