from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import QSettings, QSize
from PyQt5.QtWidgets import QDialog

INI_FILENAME = "demstyle_all.ini"
DEFAULT_WINDOW_SIZE = QSize(240, 580)


class DialogSettings(QSettings):
    """ダイアログ設定クラス"""

    def __init__(self, filename=INI_FILENAME):
        app_dir = Path(__file__).parents[1].resolve()
        settings_path = str(app_dir / filename)

        # 親クラス QSettings の初期化（INI形式を指定）
        super().__init__(settings_path, QSettings.Format.IniFormat)

    def save_dialog_state(self, dialog: QDialog) -> None:
        """ダイアログの配置を保存する"""
        self.setValue("dialog/geometry", dialog.saveGeometry())
        self.sync()  # INIファイルに保存

    def restore_dialog_state(self, dialog: QDialog) -> None:
        """ダイアログの配置を復元する"""
        geometry = self.value("dialog/geometry")
        if geometry:
            dialog.restoreGeometry(geometry)
        else:
            # デフォルトサイズを使用
            dialog.resize(DEFAULT_WINDOW_SIZE)

    def save_search_string(self, search_string: str) -> None:
        """検索文字列を保存する"""
        self.setValue("search/string", search_string)
        self.sync()  # INIファイルに保存

    def restore_search_string(self) -> str:
        """検索文字列を復元する"""
        return self.value("search/string", "DEM")  # デフォルトは "DEM"

    def restore_checkbox_states(self) -> tuple[bool, bool, bool]:
        """チェックボックスの状態を復元する"""
        enable_attr_table_update = self.value("checkboxes/enableAttrTableUpdate", True, type=bool)
        enable_auto_pan = self.value("checkboxes/enableAutoPan", True, type=bool)
        enable_current_feature_elev = self.value("checkboxes/enableCurrentFeatureElev", True, type=bool)
        return enable_attr_table_update, enable_auto_pan, enable_current_feature_elev

    def save_enable_attr_table_update(self, checked: bool) -> None:
        """チェックボックスの状態を保存する (属性テーブル更新)"""
        self.setValue("checkboxes/enableAttrTableUpdate", checked)
        self.sync()

    def save_enable_auto_pan(self, checked: bool) -> None:
        """チェックボックスの状態を保存する (地物中心にパン)"""
        self.setValue("checkboxes/enableAutoPan", checked)
        self.sync()

    def save_enable_current_feature_elev(self, checked: bool) -> None:
        """チェックボックスの状態を保存する (属性テーブルの標高を読み込む)"""
        self.setValue("checkboxes/enableCurrentFeatureElev", checked)
        self.sync()
