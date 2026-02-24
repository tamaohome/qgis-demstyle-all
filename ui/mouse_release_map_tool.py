from typing import override
from qgis.gui import QgsMapMouseEvent, QgsMapToolEmitPoint


class MouseReleaseMapTool(QgsMapToolEmitPoint):
    """マウスリリースにより発火するマップツール"""

    @override
    def canvasPressEvent(self, e: QgsMapMouseEvent):
        # マウス押下時の挙動を無効化
        pass

    @override
    def canvasReleaseEvent(self, e: QgsMapMouseEvent):
        # マウスが離された位置の地図座標を取得
        point = self.toMapCoordinates(e.pos())

        # 本来クリック時に飛ぶはずの canvasClicked シグナルを
        # リリースのタイミングで手動で発信（emit）する
        self.canvasClicked.emit(point, e.button())
