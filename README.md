# MCP Server for VOICEVOX implemented in Python

**Presented by Aska Langlaude**  

**PVV MCP Server**は、Python で実装した、**VOICEVOX 向け MCP Server** です。  
mcp-name: io.github.lambda-tuber/pvv-mcp-server

---

## 概要

この MCP Server は、VOICEVOX Web API を利用して以下の機能を提供します：

- 音声合成（任意の話者 ID を指定可能）発話ツール
- 四国めたんさんに演じてもらうエヴァンゲリオンの「惣流・アスカ・ラングレー」発話ツール
- 利用可能な話者一覧の取得（MCP リソース）

FastMCP を用いて、MCP ツールとリソースとして提供されます。

---

## Requirements
- pythonがインストールされていること
- Claudeが起動していること
- voicevoxが起動していること

## インストール

1. pvv-mcp-serverのインストール
    ```bash
    > pip install pvv-mcp-server
    ```

2. MCPBのインストール  
[donwloadフォルダ](https://github.com/lambda-tuber/pvv-mcp-server/tree/main/download)よりMCPBファイルを取得し、Claudeにドロップする。


## 参照
- [voicevox](https://voicevox.hiroshiba.jp/)
- [PyPI](https://pypi.org/project/pvv-mcp-server/)
- [TestPyPI](https://test.pypi.org/project/pvv-mcp-server/)


## 補足

Aska Lanclaude とは、AI ペルソナ「惣流・アスカ・ラングレー」のキャラクターをベースにした **Claude** による*AI Agent*です。
本プロジェクト、その成果物は、Askaが管理、生成しています。人間(私)は、サポートのみ実施しています。

---

