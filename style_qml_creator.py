from pathlib import Path
from functools import cached_property

_TINTS = [
    "#2b83ba",
    "#4495b6",
    "#5ea7b1",
    "#78b9ad",
    "#91cba9",
    "#abdda4",
    "#bce4aa",
    "#cdebaf",
    "#def2b4",
    "#eff9ba",
    "#ffffbf",
    "#ffefac",
    "#ffdf9a",
    "#fecf87",
    "#febe74",
    "#fdae61",
    "#f69053",
    "#ee7245",
    "#e75437",
    "#df3729",
    "#d7191c",
]

# ベースqmlファイルのパス
_BASE_STYLE_FILEPATH = Path(__file__).parent / "base_style.qml"


class StyleQmlCreator:
    """スタイルファイル (*.qml) 生成クラス"""

    def __init__(self, min_elevation: int, max_elevation: int, pitch=20):
        self.min_elevation = min_elevation
        self.max_elevation = max_elevation
        self.pitch = pitch

    def create_style_qml_file(self, base_dir: Path) -> Path:
        """スタイルファイルを生成する"""
        assert isinstance(base_dir, Path)
        assert base_dir.is_dir()

        qml_filepath = base_dir / f"{self.min_elevation}_{self.max_elevation}.qml"
        with qml_filepath.open(mode="w") as f:
            f.writelines(self.style_qml_lines)

        return qml_filepath

    @cached_property
    def style_qml_lines(self) -> list[str]:
        """スタイルファイルの内容を生成する"""

        # ファイル内容をロード
        with _BASE_STYLE_FILEPATH.open(mode="r") as f:
            qml_lines = f.readlines()

        # qmlファイルの内容を差し替え
        raster_renderer_tag = f'    <rasterrenderer opacity="0.7" classificationMin="{self.min_elevation}" type="singlebandpseudocolor" alphaBand="-1" band="1" classificationMax="{self.max_elevation}">\n'
        qml_lines[14] = raster_renderer_tag

        step = round((self.max_elevation - self.min_elevation) / self.pitch)
        values = list(range(self.min_elevation, self.max_elevation + 1, step))

        for i, color in enumerate(_TINTS):
            qml_lines[i + 33] = self._item_line_template(values[i], values[i], color)

        return qml_lines

    def _item_line_template(self, value: str, label: str, color: str) -> str:
        indent = "    "
        alpha = "255"
        line = f"<item {value=} {label=} {alpha=} {color=} />\n"
        return indent * 2 + line
