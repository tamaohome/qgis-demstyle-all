from __future__ import annotations

from typing import Literal

from ..core.elevation_triplet import calculate_elevation_triplet


class ElevationManager:
    """標高値関連処理の管理クラス"""

    def __init__(self, dialog):
        self.dialog = dialog

    def update_elevation_values(self, source: Literal["min", "mid", "max"]) -> None:
        """標高値を更新する（source: 'min' | 'mid' | 'max'）"""
        data_range = self.dialog.get_current_data_range()
        min_value, mid_value, max_value = calculate_elevation_triplet(
            source=source,
            min_value=self.dialog.minElevationSpinBox.value(),
            mid_value=self.dialog.midElevationSpinBox.value(),
            max_value=self.dialog.maxElevationSpinBox.value(),
            data_range=data_range,
        )

        self._set_elevation_values_blocking(min_value, mid_value, max_value)

        self.dialog._update_ok_button_state()
        if self.dialog.current_feature:
            self.dialog.ui_manager.highlight_matching_elevation(self.dialog.current_feature)

    def on_min_elevation_changed(self) -> None:
        self.update_elevation_values("min")

    def on_mid_elevation_changed(self) -> None:
        self.update_elevation_values("mid")

    def on_max_elevation_changed(self) -> None:
        self.update_elevation_values("max")

    def _set_elevation_values_blocking(self, min_value: int, mid_value: int, max_value: int) -> None:
        """シグナルを抑止しながら 3 つの値を同期更新する。"""
        self.dialog.minElevationSpinBox.blockSignals(True)
        self.dialog.midElevationSpinBox.blockSignals(True)
        self.dialog.maxElevationSpinBox.blockSignals(True)
        try:
            self.dialog.minElevationSpinBox.setValue(min_value)
            self.dialog.midElevationSpinBox.setValue(mid_value)
            self.dialog.maxElevationSpinBox.setValue(max_value)
        finally:
            self.dialog.minElevationSpinBox.blockSignals(False)
            self.dialog.midElevationSpinBox.blockSignals(False)
            self.dialog.maxElevationSpinBox.blockSignals(False)

    @staticmethod
    def validate_elevation_value(value: float) -> int:
        """標高値を検証し、5の倍数に丸める"""
        try:
            validated = round(value / 5) * 5
            return int(validated)
        except (ValueError, TypeError):
            return 0
