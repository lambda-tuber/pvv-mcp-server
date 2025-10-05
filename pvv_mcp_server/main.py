"""
main.py
pvv-mcp-serverのエントリポイント
"""
import io
import sys
from pvv_mcp_server import mod_service

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def main():
    """
    MCPサーバを起動する
    """
    mod_service.start()


if __name__ == "__main__":
    main()
