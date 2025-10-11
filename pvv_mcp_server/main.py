"""
pvv-mcp-server のエントリポイント

MCPサーバを起動し、コマンドライン引数を処理する
"""
import argparse
import sys
import logging
import yaml
from importlib.metadata import version, PackageNotFoundError
from pvv_mcp_server import mod_service

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
)

def get_version():
    """
    パッケージのバージョン情報を取得する
    
    Returns:
        str: バージョン文字列
    """
    try:
        return version("pvv-mcp-server")
    except PackageNotFoundError:
        return "development"


def main():
    """
    MCPサーバを起動する
    コマンドライン引数でバージョン表示・YAML読込にも対応
    """
    parser = argparse.ArgumentParser(
        description="VOICEVOX MCP Server - 音声合成機能を提供するMCPサーバ"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pvv-mcp-server {get_version()}",
        help="バージョン情報を表示して終了"
    )
    parser.add_argument(
        "-y", "--yaml",
        type=str,
        help="設定用の YAML ファイルパスを指定"
    )

    args = parser.parse_args()

    config = {}
    if args.yaml:
        try:
            with open(args.yaml, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            logging.info(f"YAML設定を読み込みました: {args.yaml}")
        except Exception as e:
            logging.error(f"YAMLファイルの読み込みに失敗しました: {e}")
            sys.exit(1)

    # MCPサーバを起動
    mod_service.start(config)


if __name__ == "__main__":
    main()
