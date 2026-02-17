import subprocess
from pathlib import Path

# --- 設定（定数） ---
QGIS_ROOT = Path("C:/Program Files/QGIS 3.44.4")
PYRCC_EXE = QGIS_ROOT / "apps/Python312/Scripts/pyrcc5.exe"
ENV_BAT = QGIS_ROOT / "bin/o4w_env.bat"

QRC_FILE = Path("resources.qrc")
PY_FILE = Path("resources.py")


def build():
    """`resources.qrc` をコンパイルして `resources.py` を生成"""
    if not PYRCC_EXE.exists():
        print(f"エラー: pyrcc5.exe が見つかりません。パスを確認してください: {PYRCC_EXE}")
        return

    if not ENV_BAT.exists():
        print(f"エラー: 環境設定バッチが見つかりません。パスを確認してください: {ENV_BAT}")
        return

    # コマンドの組み立て
    command = f'"{ENV_BAT}" && "{PYRCC_EXE}" -o "{PY_FILE}" "{QRC_FILE}"'

    print(f"ビルド開始: {QRC_FILE} -> {PY_FILE}")

    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("成功: リソースファイルが更新されました。")
    except subprocess.CalledProcessError as e:
        print("失敗: ビルド中にエラーが発生しました。")
        print(f"標準出力: {e.stdout}")
        print(f"エラー出力: {e.stderr}")


if __name__ == "__main__":
    build()
