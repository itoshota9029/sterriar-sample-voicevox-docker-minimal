# VoiceVox Docker Minimal Setup

[![CI](https://github.com/itoshota9029/sterriar-sample-voicevox-docker-minimal/actions/workflows/ci.yml/badge.svg)](https://github.com/itoshota9029/sterriar-sample-voicevox-docker-minimal/actions/workflows/ci.yml)

Docker Compose で VoiceVox ENGINE を 1 コマンドで立ち上げ、Python から TTS（Text-to-Speech）を呼ぶ最小サンプルです。

## 特徴

- Docker Compose で VoiceVox ENGINE を簡単に起動
- Python から REST API 経由で音声合成を実行
- 最小限のコードで TTS を体験できる

## 必要な環境

- Python 3.11 以上
- Docker & Docker Compose

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/itoshota9029/sterriar-sample-voicevox-docker-minimal.git
cd sterriar-sample-voicevox-docker-minimal
```

### 2. VoiceVox ENGINE を起動

```bash
docker-compose up -d
```

起動後、`http://localhost:50021` で VoiceVox ENGINE にアクセスできます。

### 3. Python パッケージをインストール

```bash
pip install -e .
```

## 使い方

```python
from src.voicevox_client import VoiceVoxClient

# クライアントを作成
client = VoiceVoxClient(base_url="http://localhost:50021")

# 話者一覧を取得
speakers = client.get_speakers()
print(f"Available speakers: {len(speakers)}")

# テキストから音声を生成
audio_data = client.synthesize(text="こんにちは、VoiceVoxです", speaker_id=1)

# 音声ファイルを保存
with open("output.wav", "wb") as f:
    f.write(audio_data)
```

## 開発

### 開発用パッケージをインストール

```bash
pip install -e ".[dev]"
```

### Linter & Formatter

```bash
ruff check src tests
ruff format src tests
```

### テストを実行

```bash
pytest
```

## ライセンス

MIT
