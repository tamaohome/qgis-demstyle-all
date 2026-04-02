from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Literal

from ..core.elevation_triplet import calculate_elevation_triplet

if TYPE_CHECKING:
    from ..ui.demstyle_all_dialog import DEMStyleAllDialog


class ElevationManager:
    """標高値関連処理の管理クラス"""

    def __init__(self, dialog: DEMStyleAllDialog) -> None:
        self.dialog = dialog

    def update_elevation_values(self, source: Literal["min", "mid", "max"]) -> None:
        """標高値を更新する（source: 'min' | 'mid' | 'max'）"""
        data_range = self.dialog.get_current_data_range()
        min_value, mid_value, max_value = calculate_elevation_triplet(
            source=source,
            min_value=self.dialog.elevation_inputs.min_value,
            mid_value=self.dialog.elevation_inputs.mid_value,
            max_value=self.dialog.elevation_inputs.max_value,
            data_range=data_range,
        )

        self._set_elevation_values_blocking(min_value, mid_value, max_value)

        self.dialog._update_ok_button_state()
        if self.dialog.current_feature:
            self.dialog.ui_manager.highlight_matching_elevation(self.dialog.current_feature)

    def on_min_elevation_changed(self, _value: int | None = None) -> None:
        self.update_elevation_values("min")

    def on_mid_elevation_changed(self, _value: int | None = None) -> None:
        self.update_elevation_values("mid")

    def on_max_elevation_changed(self, _value: int | None = None) -> None:
        self.update_elevation_values("max")

    def _set_elevation_values_blocking(self, min_value: int, mid_value: int, max_value: int) -> None:
        """シグナルを抑止しながら 3 つの値を同期更新する。"""
        self.dialog.elevation_inputs.set_values_blocking(min_value, mid_value, max_value)

    @staticmethod
    def validate_elevation_value(value: float | int | None) -> int:
        """標高値を検証し、5の倍数に丸める"""
        try:
            if value is None:
                return 0
            validated = round(value / 5) * 5
            return int(validated)
        except (ValueError, TypeError):
            return 0
