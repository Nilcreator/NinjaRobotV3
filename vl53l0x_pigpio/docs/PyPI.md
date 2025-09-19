# PyPIへの公開とインストールの方法

このドキュメントでは、`vl53l0x_pigpio` パッケージの公開手順とインストール手順を説明します。

---

## 公開者向け: PyPIへの公開手順

### 1. ビルド

配布用のパッケージをビルドします。

```bash
uv build
```

### 2. 認証情報の設定（推奨）

毎回アップロードのたびに認証情報を入力する手間を省くため、`.pypirc` ファイルに認証情報を保存する方法を推奨します。

**重要**: `pyproject.toml` のようなバージョン管理されるファイルには、APIトークンなどの機密情報を絶対に書き込まないでください。

#### `.pypirc` ファイルの作成

ホームディレクトリ (`~`) に `.pypirc` ファイルを作成し、以下の内容を記述します。`<...>`の部分はご自身のAPIトークンに置き換えてください。

**ファイル:** `~/.pypirc`
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-token>
```
作成後、以下のコマンドで自分だけが読み書きできるように権限を変更しておくと、より安全です。
```bash
chmod 600 ~/.pypirc
```

### 3. PyPI/TestPyPIへの公開

#### 3.1. アカウントとAPIトークンの準備

- **TestPI**: [TestPI](https://test.pypi.org/) でアカウントを作成し、[API token](https://test.pypi.org/manage/account/token/) を生成します。
- **PyPI**: [PyPI](https://pypi.org/) でアカウントを作成し、[API token](https://pypi.org/manage/account/token/) を生成します。

**プロジェクト初回公開時の注意:**
PyPI/TestPyPIにまだプロジェクトが存在しない場合、プロジェクトにスコープを限定したAPIトークンは作成できません。その場合、初回のみ以下の手順が必要です。

1.  スコープを **`Entire account (all projects)`** に設定した一時的なトークンを作成して、初回アップロードを行います。
2.  アップロード成功後、プロジェクトに限定した正式なトークンを再作成します。
3.  セキュリティのため、最初に使用した一時的なトークンは削除します。

#### 3.2. アップロード

以下のコマンドでパッケージをアップロードします。

**TestPIへ (テスト用):**
```bash
uv run hatch publish -r test
```

**PyPIへ (本番公開):**
```bash
uv run hatch publish
```

`.pypirc` ファイルを設定していない場合は、コマンド実行後にユーザー名 (`__token__`) とパスワード (APIトークン) の入力が求められます。

---

## 利用者向け: インストールと更新の方法

### PyPIからの通常インストール・更新

PyPIで公開されている安定版をインストールするには、以下のコマンドを実行します。

```bash
pip install vl53l0x_pigpio
```
または `uv` を使う場合:
```bash
uv pip install vl53l0x_pigpio
```

すでにインストール済みで、最新版に更新する場合は `-U` (`--upgrade`) フラグを追加します。

```bash
pip install -U vl53l0x_pigpio
```
(`uv pip install` は常に最新版をインストールしようとするため、コマンドは同じです。)

### TestPIからのテストインストール・更新

開発中のバージョンなどをテストするには、以下のコマンドでTestPIから直接インストールします。

**`uv pip` を使う場合 (推奨):**
```bash
uv pip install \
  --index-url https://test.pypi.org/simple/ \
  vl53l0x_pigpio
```

**`pip` を使う場合:**
```bash
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  vl53l0x_pigpio
```

すでにTestPIからインストール済みで、最新のテストバージョンに更新する場合も、同様に `--index-url` を指定し、`-U` フラグを追加します。

```bash
pip install -U \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  vl53l0x_pigpio
```
(`uv` を使う場合は、インストールと同じコマンドで更新も行えます。)
