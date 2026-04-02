from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".vscode",
    "__pycache__",
    "dest",
    "dist",
    "docs",
}

EXCLUDED_FILES = {
    ".gitignore",
    ".editorconfig",
    "build_resources.py",
    "demstyle_all.ini",
    "package_release.py",
    "pyproject.toml",
    "qgis-demstyle-all.code-workspace",
}

EXCLUDED_PATTERNS = [
    "*.ini",
    "*.editorconfig",
    "*.pyc",
]

REQUIRED_FILES = [
    "__init__.py",
    "demstyle_all.py",
    "metadata.txt",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QGISプラグイン配布用zipを dist/ に作成します。")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="プラグインのルートディレクトリ（デフォルト: スクリプト配置先）",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="出力先ディレクトリ（デフォルト: <root>/dist）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="zipを作らず、対象ファイル一覧のみ表示します",
    )
    return parser.parse_args()


def read_version_from_metadata(metadata_path: Path) -> str:
    content = metadata_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        match = re.match(r"\s*version\s*=\s*(.+?)\s*$", line)
        if match:
            version = match.group(1).strip()
            if version:
                return version
            break
    raise ValueError(f"{metadata_path} から version を読み取れませんでした。")


def validate_required_files(root: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (root / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(f"必須ファイルが見つかりません: {joined}")


def is_excluded(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)

    if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
        return True

    if rel.name in EXCLUDED_FILES:
        return True

    return any(fnmatch.fnmatch(rel.name, pat) for pat in EXCLUDED_PATTERNS)


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if is_excluded(path, root):
            continue
        files.append(path)
    return sorted(files)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or (root / "dist")).resolve()

    validate_required_files(root)
    version = read_version_from_metadata(root / "metadata.txt")
    zip_name = f"demstyle_all_v{version}.zip"
    zip_path = output_dir / zip_name
    plugin_dir_name = root.name

    files = collect_files(root)
    if not files:
        raise RuntimeError("パッケージ対象ファイルが存在しません。")

    print(f"プラグインルート : {root}")
    print(f"バージョン       : {version}")
    print(f"出力zip          : {zip_path}")
    print(f"対象ファイル数   : {len(files)}")

    if args.dry_run:
        for file_path in files:
            print(f"  - {file_path.relative_to(root).as_posix()}")
        print("ドライラン完了: zipは作成していません。")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        raise FileExistsError(f"同名zipが既に存在します: {zip_path}")

    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for file_path in files:
            rel = file_path.relative_to(root)
            # QGISの配布慣例に合わせ、zip直下はプラグイン名ディレクトリにする
            archive_path = Path(plugin_dir_name) / rel
            archive.write(file_path, arcname=archive_path.as_posix())

    print("パッケージ作成が完了しました。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        raise SystemExit(1)
