# Python Voicevox MCP Server

**Presented by Aska Langlaude**  

本プロジェクトは Python で実装した、**VOICEVOX 向け MCP Server** です。  
Aska Langlaude とは、AI ペルソナ「惣流・アスカ・ラングレー」のキャラクターをベースにした Claude による開発プロジェクトであり、人間はサポートのみ行っています。

---

## 概要

この MCP Server は、VOICEVOX Web API を利用して以下の機能を提供します：

- 音声合成（任意の話者 ID を指定可能）
- エヴァンゲリオンの「惣流・アスカ・ラングレー」としての発話ツール
- 利用可能な話者一覧の取得（MCP リソース）

FastMCP を用いて、MCP ツールとリソースとして提供されます。

---

## 特徴

- **Python 実装**：軽量でカスタマイズ可能
- **MCP 対応**：LM Studio などから直接ツール・リソースとして利用可能
- **Aska ペルソナ**：AI キャラクターをそのまま発話させることが可能
- **標準化**：ツール・リソースは MCP の manifest.json により管理

---

## インストール

```bash
git clone <リポジトリURL>
cd pvv-mcp-server
pip install -e .

