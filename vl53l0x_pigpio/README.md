# VL53L0X pigpio

## ◆概要

`pigpio`ライブラリを使用してVL53L0X距離センサーを制御するためのPythonドライバーです。
Raspberry Pi Zero 2Wのような低スペックの環境でも動作するように設計されています。

## ◆特徴

- `pigpio` を利用し、すべてPythonで実装
- ライブラリとして、またCLIツールとして利用可能
- オフセットキャリブレーション機能

## ◆インストール

リポジトリをクローンして`uv`を使用してください。

```bash
git clone https://github.com/your-username/vl53l0x-pigpio.git
cd vl53l0x-pigpio
uv venv
uv pip install -e .
```

## ◆ライブラリとしての使い方

基本的な使い方は以下の通りです。

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

# pigpioに接続
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpioに接続できません")

try:
    # withステートメントでセンサーを初期化
    # 自動的に設定ファイル(~/vl53l0x.json)が読み込まれます
    with VL53L0X(pi) as tof:
        # 距離を測定
        distance = tof.get_range()
        if distance > 0:
            print(f"距離: {distance} mm")
        else:
            print("無効なデータ。")

finally:
    # pigpioのリソースを解放
    pi.stop()
```

## ◆CLIツールの使い方

このパッケージには、コマンドラインからセンサーを操作するための`vl53l0x_pigpio`コマンドが含まれています。
コマンドの実行には `uv run` を使用します。

### === ヘルプ

```bash
uv run vl53l0x_pigpio --help
```

### === 距離の測定 (`get`)

指定した回数だけ距離を測定します。

```bash
uv run vl53l0x_pigpio get [OPTIONS]
```

**オプション:**
- `-c, --count INTEGER`: 測定回数 (デフォルト: 10)
- `-i, --interval FLOAT`: 測定間隔（秒） (デフォルト: 1.0)

**例:**
```bash
# 5回測定する
uv run vl53l0x_pigpio get --count 5
```

### === パフォーマンス測定 (`performance`)

センサーの測定パフォーマンス（1秒あたりの測定回数）を評価します。

```bash
uv run vl53l0x_pigpio performance [OPTIONS]
```

**オプション:**
- `--count INTEGER`: 測定回数 (デフォルト: 100)

**例:**
```bash
# 500回測定してパフォーマンスを評価
uv run vl53l0x_pigpio performance --count 500
```

### === キャリブレーション (`calibrate`)

センサーのオフセット値をキャリブレーションし、設定ファイルに保存します。

```bash
uv run vl53l0x_pigpio calibrate [OPTIONS]
```

**手順:**
1. センサーの前に、指定した距離（デフォルト: 100mm）に白いターゲットを置きます。
2. 上記コマンドを実行すると、Enterキーの入力を求められます。
3. 準備ができたらEnterキーを押すと、測定が開始されます。
4. 計算されたオフセット値が設定ファイルに保存されます。

**オプション:**
- `-D, --distance INTEGER`: ターゲットまでの距離 [mm] (デフォルト: 100)
- `-c, --count INTEGER`: 測定回数 (デフォルト: 10)
- `-o, --output-file TEXT`: オフセットを保存するファイルパス (デフォルト: `~/vl53l0x.json`)

**例:**
```bash
# 15cm (150mm) の距離でキャリブレーション
uv run vl53l0x_pigpio calibrate --distance 150
```

## ◆参考情報

- [Pololu社:Arduino用 C++ ソースコード](https://github.com/pololu/vl53l0x-arduino)
- https://github.com/cassou/VL53L0X_rasp
- https://github.com/johnbryanmoore/VL53L0X_rasp_python


## ◆AIの活用

以下のAIと **協力しながら** 作成しました。
とはいえ、作らせっぱなしにするのではなく、
随時人間が確認し、相当な手を加えています。

- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [ChatGPT](https://chatgpt.com/)
- [claude](https://claude.ai/)


## ◆ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。
