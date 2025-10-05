"""
main.py
pvv-mcp-serverのエントリポイント
"""
import io
import sys
import os

from pvv_mcp_server import mod_service

sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def main():
    """
    MCPサーバを起動する
    """
    mod_service.start()


if __name__ == "__main__":
    main()
