# Tasks

## 1. CLI実行のための設定

- [x] `src/vl53l0x_pigpio/__main__.py` を作成する。
- [x] `__main__.py` に `vl53l0x_pigpio.cli` の `main` 関数を呼び出すコードを記述する。
- [x] `pyproject.toml` の `[project]` セクションに `scripts` を追加し、`vl53l0x-pigpio = "vl53l0x_pigpio.__main__:main"` のように設定する。
- [x] `uv run vl53l0x-pigpio --help` を実行して、CLIが起動することを確認する。

## 2. LintingとFormatting

- [ ] `pyproject.toml` の `[tool.ruff]` セクションに `line-length = 78` を設定する。
- [ ] `uv run ruff check . --fix` を実行して、自動修正可能なlintエラーを修正する。
- [ ] `uv run ruff check .` を実行して、残りのlintエラーを手動で修正する。
- [ ] `uv run ruff format .` を実行して、コード全体のフォーマットを統一する。

## 3. テストによる動作確認

- [ ] `uv run python -m pytest -v` を実行し、既存のテストがすべてパスすることを確認する。
- [ ] （必要に応じて）基本的な動作を検証するためのテストを追加する。

## 4. リファクタリング

- [ ] `src/vl53l0x_pigpio/driver.py` を中心に、マジックナンバーを `constants.py` に移動する。
- [ ] 複雑なロジックをより小さな関数に分割し、可読性を向上させる。
- [ ] 変数名、関数名をより分かりやすく、一貫性のあるものに見直す。
- [ ] すべてのソースコードのコメントが日本語で、かつ内容が適切であることを確認・修正する。

## 5. 完了報告

- [ ] `ToDo.md` の完了した項目にチェックを入れる。
- [ ] 本 `Tasks.md` のすべての項目にチェックが入っていることを確認する。
- [ ] `Tasks.md` を `tasks/Tasks-done-yymmdd-HHMM.md` の形式でリネームする。
- [ ] ユーザーにすべての作業が完了したことを報告し、指示を待つ。
