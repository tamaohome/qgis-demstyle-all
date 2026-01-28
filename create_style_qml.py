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

_BASE_STYLE_FILENAME = "style.qml"


def create_style_qml(base_dir: Path, min_val: int, max_val: int, pitch=20):
    """スタイルファイルを生成する"""
    assert base_dir.is_dir()
    base_style_filepath = open(base_dir / _BASE_STYLE_FILENAME, "r")
    with base_style_filepath.read("w") as f:
        data = f.readlines()

    data[14] = (
        '    <rasterrenderer opacity="0.7" classificationMin="'
        + str(min_val)
        + '" type="singlebandpseudocolor" alphaBand="-1" band="1" classificationMax="'
        + str(max_val)
        + '">\n'
    )

    values = []
    for n in range(pitch + 1):
        values = values + [str(min_val + (max_val - min_val) / pitch * n)]

    for i, color in enumerate(_COLORS):
        data[i + 33] = _item_line_template(values[i], values[i], color)
    # data[33] = '          <item value="' + values[0] + '" label="' + values[0] + '" alpha="255" color="#2b83ba"/>\n'
    # data[34] = '          <item value="' + values[1] + '" label="' + values[1] + '" alpha="255" color="#4495b6"/>\n'
    # data[35] = '          <item value="' + values[2] + '" label="' + values[2] + '" alpha="255" color="#5ea7b1"/>\n'
    # data[36] = '          <item value="' + values[3] + '" label="' + values[3] + '" alpha="255" color="#78b9ad"/>\n'
    # data[37] = '          <item value="' + values[4] + '" label="' + values[4] + '" alpha="255" color="#91cba9"/>\n'
    # data[38] = '          <item value="' + values[5] + '" label="' + values[5] + '" alpha="255" color="#abdda4"/>\n'
    # data[39] = '          <item value="' + values[6] + '" label="' + values[6] + '" alpha="255" color="#bce4aa"/>\n'
    # data[40] = '          <item value="' + values[7] + '" label="' + values[7] + '" alpha="255" color="#cdebaf"/>\n'
    # data[41] = '          <item value="' + values[8] + '" label="' + values[8] + '" alpha="255" color="#def2b4"/>\n'
    # data[42] = '          <item value="' + values[9] + '" label="' + values[9] + '" alpha="255" color="#eff9ba"/>\n'
    # data[43] = '          <item value="' + values[10] + '" label="' + values[10] + '" alpha="255" color="#ffffbf"/>\n'
    # data[44] = '          <item value="' + values[11] + '" label="' + values[11] + '" alpha="255" color="#ffefac"/>\n'
    # data[45] = '          <item value="' + values[12] + '" label="' + values[12] + '" alpha="255" color="#ffdf9a"/>\n'
    # data[46] = '          <item value="' + values[13] + '" label="' + values[13] + '" alpha="255" color="#fecf87"/>\n'
    # data[47] = '          <item value="' + values[14] + '" label="' + values[14] + '" alpha="255" color="#febe74"/>\n'
    # data[48] = '          <item value="' + values[15] + '" label="' + values[15] + '" alpha="255" color="#fdae61"/>\n'
    # data[49] = '          <item value="' + values[16] + '" label="' + values[16] + '" alpha="255" color="#f69053"/>\n'
    # data[50] = '          <item value="' + values[17] + '" label="' + values[17] + '" alpha="255" color="#ee7245"/>\n'
    # data[51] = '          <item value="' + values[18] + '" label="' + values[18] + '" alpha="255" color="#e75437"/>\n'
    # data[52] = '          <item value="' + values[19] + '" label="' + values[19] + '" alpha="255" color="#df3729"/>\n'
    # data[53] = '          <item value="' + values[20] + '" label="' + values[20] + '" alpha="255" color="#d7191c"/>\n'

    qml_filepath = base_dir / f"_{max_val}.qml"
    with qml_filepath.open(mode="w"):
        f.writelines(data)


def _item_line_template(value: str, label: str, color: str) -> str:
    indent = "    "
    alpha = "255"
    line = f"<item {value=} {label=} {alpha=} {color=} />\n"
    return indent * 2 + line
