# Tasks.md

## タスク: `get_measurement_timing_budget`と`set_measurement_timing_budget`の実装

### 参考情報
- [Pololu社:Arduino用 C++ ソースコード](https://github.com/pololu/vl53l0x-arduino)
- 現在のdriver.pyの該当メソッドは500ms固定のプレースホルダー実装

### 実行計画
現在のプレースホルダー実装を、Pololu社のC++実装を参考に適切な実装に置き換える。

### 詳細タスク

- [x] 1. 参考URLからPololu社のVL53L0X Arduino C++ライブラリのソースコードを調査
  - `get_measurement_timing_budget()`の実装を確認
  - `set_measurement_timing_budget()`の実装を確認
  - 使用されているレジスタアドレスと計算式を把握
  - 判明事項：デフォルト33ms、最小20ms、HIGH_SPEEDモードでは20ms設定

- [ ] 2. driver.pyの`get_measurement_timing_budget`メソッドの実装
  - プレースホルダーの固定値500000を削除
  - 各シーケンスステップのタイミングを読み取る処理を実装
  - レジスタから実際の値を計算して返す処理を実装

- [ ] 3. driver.pyの`set_measurement_timing_budget`メソッドの実装
  - プレースホルダーの空実装を削除
  - 指定されたタイミングバジェットに応じてレジスタを設定する処理を実装
  - エラーハンドリング（無効な値の場合など）を追加

- [ ] 4. 必要に応じてconstants.pyに新しい定数を追加
  - タイミング計算で使用される定数値を追加
  - レジスタアドレスで不足しているものがあれば追加

- [ ] 5. リンティングの実行
  - `uv run ruff check .`
  - `uv run mypy .`
  - エラーがあれば修正

- [ ] 6. テストプログラムの作成・更新
  - `tests`ディレクトリにタイミングバジェット機能のテストを作成
  - 基本的な動作確認を行うテストケースを実装

- [ ] 7. テストの実行と動作確認
  - `uv run python -m pytest -v tests/`でテストを実行
  - CLIツールでの動作確認も実施

- [ ] 8. コードの最終確認とドキュメント更新
  - 実装内容の確認
  - 必要に応じてdocstringの更新

### 注意事項
- 現在のdriver.pyには既にタイミングバジェット関連の処理が一部実装されているため、既存コードとの整合性を保つ
- エンディアン変換（ビッグエンディアン⇔リトルエンディアン）に注意
- タイムアウト処理を適切に実装する
