from pathlib import Path


def get_version():
    """メタデータファイルからバージョンを取得"""
    metadata_file = Path(__file__).parent / "metadata.txt"
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("version="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "unknown"
