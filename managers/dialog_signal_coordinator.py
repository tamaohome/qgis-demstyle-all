from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt

if TYPE_CHECKING:
    from ..ui.demstyle_all_dialog import DEMStyleAllDialog


class DialogSignalCoordinator:
    """ダイアログの signal/slot 配線を一箇所に集約する。"""

    def __init__(self, dialog: DEMStyleAllDialog) -> None:
        self.dialog = dialog

    def bind(self) -> None:
        # 主操作の配線
        self.dialog.dataRangeSlider.valueChanged.connect(
            self.dialog.dem_layer_range_manager.handle_slider_change
        )
        self.dialog.setElevationButton.clicked.connect(self.dialog.start_capture_mode)
        self.dialog.elevation_inputs.connect_value_changed(
            self.dialog.elevation_manager.on_min_elevation_changed,
            self.dialog.elevation_manager.on_mid_elevation_changed,
            self.dialog.elevation_manager.on_max_elevation_changed,
        )
        self.dialog.map_tool.canvasClicked.connect(self.dialog.dem_layer_range_manager.handle_get_elevation)
        self.dialog.okButton.clicked.connect(self.dialog.on_ok_clicked)
        self.dialog.cancelButton.clicked.connect(self.dialog.on_cancel_clicked)
        self.dialog.searchStringRenameButton.clicked.connect(
            self.dialog.on_search_string_rename_button_clicked
        )
        self.dialog.featureLayerComboBox.currentIndexChanged.connect(self.dialog.on_feature_layer_changed)

        # チェックボックス状態を設定へ保存
        self.dialog.enableAttrTableUpdateCheckBox.stateChanged.connect(
            lambda checked: self.dialog.settings.save_enable_attr_table_update(
                checked == Qt.CheckState.Checked
            )
        )
        self.dialog.enableAutoPanCheckBox.stateChanged.connect(
            lambda checked: self.dialog.settings.save_enable_auto_pan(checked == Qt.CheckState.Checked)
        )
        self.dialog.enableCurrentFeatureElevCheckBox.stateChanged.connect(
            lambda checked: self.dialog.settings.save_enable_current_feature_elev(
                checked == Qt.CheckState.Checked
            )
        )
