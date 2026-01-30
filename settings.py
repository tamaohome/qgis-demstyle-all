from __future__ import annotations

from pathlib import Path

from qgis.PyQt.QtCore import QSettings, QSize
from qgis.PyQt import QtWidgets

INI_FILENAME = "demstyle_all/demstyle_all.ini"
DEFAULT_WINDOW_SIZE = QSize(320, 400)


class DialogSettings(QSettings):
    """ダイアログ設定クラス"""

    def __init__(self, filename=INI_FILENAME):
        app_dir = Path(__file__).parents[1].resolve()
        settings_path = str(app_dir / filename)

        # 親クラス QSettings の初期化（INI形式を指定）
        super().__init__(settings_path, QSettings.Format.IniFormat)

    def save_dialog_state(self, dialog: QtWidgets.QDialog) -> None:
        """ダイアログの配置を保存する"""
        self.setValue("dialog/geometry", dialog.saveGeometry())
        self.sync()  # INIファイルに保存

    def restore_dialog_state(self, dialog: QtWidgets.QDialog) -> None:
        """ダイアログの配置を復元する"""
        geometry = self.value("dialog/geometry")
        if geometry:
            dialog.restoreGeometry(geometry)
        else:
            # デフォルトサイズを使用
            dialog.resize(DEFAULT_WINDOW_SIZE)
