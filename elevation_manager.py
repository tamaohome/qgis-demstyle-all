class ElevationManager:
    """標高値関連処理の管理クラス"""

    def __init__(self, dialog):
        self.dialog = dialog

    def update_elevation_values(self, source: str) -> None:
        """標高値を更新する（source: 'min' | 'mid' | 'max'）"""
        data_range = self.dialog.get_current_data_range()

        # 値を計算
        if source == "min":
            min_value = self.dialog.minElevationSpinBox.value()
            mid_value = min_value + data_range
            max_value = mid_value + data_range
        elif source == "mid":
            mid_value = self.dialog.midElevationSpinBox.value()
            min_value = mid_value - data_range
            max_value = mid_value + data_range
        else:  # source == "max"
            max_value = self.dialog.maxElevationSpinBox.value()
            mid_value = max_value - data_range
            min_value = mid_value - data_range

        # 全てのシグナルをブロック
        self.dialog.minElevationSpinBox.blockSignals(True)
        self.dialog.midElevationSpinBox.blockSignals(True)
        self.dialog.maxElevationSpinBox.blockSignals(True)

        # 値を設定
        self.dialog.minElevationSpinBox.setValue(min_value)
        self.dialog.midElevationSpinBox.setValue(mid_value)
        self.dialog.maxElevationSpinBox.setValue(max_value)

        # シグナルのブロックを解除
        self.dialog.minElevationSpinBox.blockSignals(False)
        self.dialog.midElevationSpinBox.blockSignals(False)
        self.dialog.maxElevationSpinBox.blockSignals(False)

        self.dialog._update_ok_button_state()
        if self.dialog._current_feature:
            self.dialog.ui_manager.highlight_matching_elevation(self.dialog._current_feature)

    def on_min_elevation_changed(self) -> None:
        self.update_elevation_values("min")

    def on_mid_elevation_changed(self) -> None:
        self.update_elevation_values("mid")

    def on_max_elevation_changed(self) -> None:
        self.update_elevation_values("max")

    @staticmethod
    def validate_elevation_value(value: float) -> int:
        """標高値を検証し、5の倍数に丸める"""
        try:
            validated = round(value / 5) * 5
            return int(validated)
        except (ValueError, TypeError):
            return 0
