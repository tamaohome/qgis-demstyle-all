from pathlib import Path

_COLORS = [
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


def create_style_qml(base_dir: Path, min_value: int, max_value: int, pitch=20) -> Path:
    """スタイルファイルを生成する"""
    assert isinstance(base_dir, Path)
    assert base_dir.is_dir()

    # ベースqmlファイルのパスを取得
    base_style_filepath = Path(__file__).parent / "base_style.qml"

    # ファイル内容をロード
    with base_style_filepath.open(mode="r") as f:
        data = f.readlines()

    # qmlファイルの内容を差し替え
    raster_renderer_tag = f'    <rasterrenderer opacity="0.7" classificationMin="{min_value}" type="singlebandpseudocolor" alphaBand="-1" band="1" classificationMax="{max_value}">\n'
    data[14] = raster_renderer_tag

    values = []
    for n in range(pitch + 1):
        values = values + [str(min_value + (max_value - min_value) / pitch * n)]

    for i, color in enumerate(_COLORS):
        data[i + 33] = _item_line_template(values[i], values[i], color)

    qml_filepath = base_dir / f"_{max_value}.qml"
    with qml_filepath.open(mode="w") as f:
        f.writelines(data)

    return qml_filepath


def _item_line_template(value: str, label: str, color: str) -> str:
    indent = "    "
    alpha = "255"
    line = f"<item {value=} {label=} {alpha=} {color=} />\n"
    return indent * 2 + line
