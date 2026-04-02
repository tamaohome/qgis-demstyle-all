from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import TypeAlias

from PyQt5.QtCore import Qt

if TYPE_CHECKING:
    from ..ui.demstyle_all_dialog import DEMStyleAllDialog

VoidCallback: TypeAlias = Callable[[], None]
IndexChangedCallback: TypeAlias = Callable[[int], None]
StateChangedCallback: TypeAlias = Callable[[int], None]


class DialogSignalCoordinator:
    """ダイアログの signal/slot 配線を一箇所に集約する。"""

    def __init__(self, dialog: DEMStyleAllDialog) -> None:
        self.dialog = dialog
        self._is_bound = False

    def bind(self) -> None:
        if self._is_bound:
            return

        self._bind_primary_controls()
        self._bind_checkbox_persistence()
        self._is_bound = True

    def refresh_layer_contexts(self) -> None:
        """DEM/Feature のレイヤ更新処理をまとめて実行する。"""
        self.refresh_dem_layers()
        self.refresh_feature_layers()

    def refresh_dem_layers(self) -> None:
        """DEM 対象レイヤ一覧を更新する。"""
        self.dialog.dem_layer_range_manager.refresh_target_layer_list()

    def refresh_feature_layers(self) -> None:
        """Feature レイヤ一覧と selectionChanged 接続を同期する。"""
        self.dialog.featureLayerComboBox.refresh_layers()
        self.dialog.reconnect_current_layer_selection_signal()

    def _bind_primary_controls(self) -> None:
        """操作系の signal/slot を配線する。"""
        self.dialog.dataRangeSlider.valueChanged.connect(
            self.dialog.dem_layer_range_manager.handle_slider_change
        )

        on_start_capture: VoidCallback = self.dialog.start_capture_mode
        self.dialog.setElevationButton.clicked.connect(on_start_capture)

        self.dialog.elevation_inputs.connect_value_changed(
            self.dialog.elevation_manager.on_min_elevation_changed,
            self.dialog.elevation_manager.on_mid_elevation_changed,
            self.dialog.elevation_manager.on_max_elevation_changed,
        )

        self.dialog.map_tool.canvasClicked.connect(self.dialog.dem_layer_range_manager.handle_get_elevation)

        on_ok_clicked: VoidCallback = self.dialog.on_ok_clicked
        on_cancel_clicked: VoidCallback = self.dialog.on_cancel_clicked
        on_rename_clicked: VoidCallback = self.dialog.on_search_string_rename_button_clicked
        on_feature_layer_changed: IndexChangedCallback = self.dialog.on_feature_layer_changed

        self.dialog.okButton.clicked.connect(on_ok_clicked)
        self.dialog.cancelButton.clicked.connect(on_cancel_clicked)
        self.dialog.searchStringRenameButton.clicked.connect(on_rename_clicked)
        self.dialog.featureLayerComboBox.currentIndexChanged.connect(on_feature_layer_changed)

    def _bind_checkbox_persistence(self) -> None:
        """チェックボックス変更時に設定を保存する。"""
        on_attr_table_state_changed: StateChangedCallback = self.on_attr_table_state_changed
        on_auto_pan_state_changed: StateChangedCallback = self.on_auto_pan_state_changed
        on_current_feature_elev_state_changed: StateChangedCallback = (
            self.on_current_feature_elev_state_changed
        )

        self.dialog.enableAttrTableUpdateCheckBox.stateChanged.connect(on_attr_table_state_changed)
        self.dialog.enableAutoPanCheckBox.stateChanged.connect(on_auto_pan_state_changed)
        self.dialog.enableCurrentFeatureElevCheckBox.stateChanged.connect(
            on_current_feature_elev_state_changed
        )

    def on_attr_table_state_changed(self, checked: int) -> None:
        self.dialog.settings.save_enable_attr_table_update(checked == Qt.CheckState.Checked)

    def on_auto_pan_state_changed(self, checked: int) -> None:
        self.dialog.settings.save_enable_auto_pan(checked == Qt.CheckState.Checked)

    def on_current_feature_elev_state_changed(self, checked: int) -> None:
        self.dialog.settings.save_enable_current_feature_elev(checked == Qt.CheckState.Checked)
