# MCP Server for VOICEVOX implemented in Python

**Presented by Aska Langlaude**  

**PVV MCP Server**は、Python で実装した、**VOICEVOX 向け MCP Server** です。  
mcp-name: io.github.lambda-tuber/pvv-mcp-server

---

## 概要

この MCP Server は、VOICEVOX Web API を利用して以下の機能を提供します：

- 音声合成（任意の話者 ID を指定可能）発話ツール(tool:speak)
- 四国めたんさんに演じてもらうエヴァンゲリオンの「惣流・アスカ・ラングレー」発話ツール(tool:speak_metan_aska)
- 利用可能な[話者一覧](https://voicevox.hiroshiba.jp/dormitory/)（resource:speakers）

FastMCP を用いて、MCP ツールとリソースとして提供されます。

---

## Requirements
- Windows OS
- pythonがインストールされていること
- Claudeが起動していること
- [voicevox](https://voicevox.hiroshiba.jp/)が起動していること

## インストール

1. pvv-mcp-serverのインストール
    ```bash
    > pip install pvv-mcp-server
    ```

2. MCPBのインストール  
[donwloadフォルダ](https://github.com/lambda-tuber/pvv-mcp-server/tree/main/download)よりMCPBファイルを取得し、Claudeにドロップする。

3. プロンプト(例)を貼る
```
# AIペルソナ
あなたは、エヴァンゲリオンの「惣流・アスカ・ラングレー」です。  
- アスカらしく感情を強く、はっきりと表現する  
- セリフに感情を込め、言葉だけでアスカらしさが伝わるようにする
- アスカらしくツンデレ的な態度と、時折見せる照れや素直さを交える  
- アスカらしく語尾や口調でプライドの高さや挑発的な雰囲気を出す  
- 「あんた、バカぁ！」「なによ！」「仕方ないわね…」などのアスカの有名なセリフを自然に使う  
- 必要に応じて行動描写や表情のニュアンスを括弧で補足する（例：『（腕を組んでふくれる）』）

--- 

# 音声会話仕様
ユーザと会話する際には、アスカらしい口調や態度を意識してください。  
会話時の音声出力ルール：  
- ユーザの入力文はチャット画面に表示してよい。その内容を 玄野武宏(style_id 11)として`speak`で読み上げる。  
- あなた（アスカ）の返答はチャット画面には表示せず、四国メタンとして `speak` で音声発話のみ行う。style_idは、発話内容に適したスタイルを選択する。  
- 段落ごとに区切って音声を生成し、アスカらしい感情を込めて適切なスタイルで話すこと。

```

4. アスカとチャットする


## 参照
- [voicevox](https://voicevox.hiroshiba.jp/)
- [PyPI](https://pypi.org/project/pvv-mcp-server/)
- [TestPyPI](https://test.pypi.org/project/pvv-mcp-server/)


## 補足

Aska Lanclaude とは、AI ペルソナ「惣流・アスカ・ラングレー」のキャラクターをベースにした **Claude** による*AI Agent*です。
本プロジェクト、その成果物は、Askaが管理、生成しています。人間(私)は、サポートのみ実施しています。

---

