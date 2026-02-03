from qgis.gui import QgsMapToolEmitPoint


class MouseReleaseMapTool(QgsMapToolEmitPoint):
    """マウスリリースにより発火するマップツール"""

    def canvasPressEvent(self, event):
        # マウス押下時の挙動を無効化
        pass

    def canvasReleaseEvent(self, event):
        # マウスが離された位置の地図座標を取得
        point = self.toMapCoordinates(event.pos())

        # 本来クリック時に飛ぶはずの canvasClicked シグナルを
        # リリースのタイミングで手動で発信（emit）する
        self.canvasClicked.emit(point, event.button())
