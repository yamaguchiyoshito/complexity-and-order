# GitHub登録と任意のPages公開

[連載目次へ](../README.md)

## 現在の状態

本配布物はGitHub管理用のファイル一式である。この作業環境でGitHubへの新規作成・pushは実施していない。以下は手元の認証済みGitHub CLIを用いて実行する手順である。

Git、GitHub CLI、Python 3.11以降、Pandoc 3.xを準備する。GitHub CLIは[公式マニュアル](https://cli.github.com/manual/gh_repo_create)に従って導入・認証する。トークンを原稿・設定・コマンド引数へ貼り付けない。

```sh
gh auth login
gh auth status
git config --get user.name
git config --get user.email
```

Gitの名前とメールが未設定なら、自分の著者情報を設定する。配布物では他人の名前やメールを初期コミットへ埋め込まない。

## 新規リポジトリを作成する

ZIPを展開し、`complexity-and-order` ディレクトリへ移動する。最初に計画だけを確認できる。

```sh
python scripts/publish.py --owner yamaguchiyoshito --name complexity-and-order
```

非公開の新規リポジトリを作り、初期コミットをpushする場合は、明示的に `--execute` を付ける。

```sh
python scripts/publish.py --owner yamaguchiyoshito --name complexity-and-order --visibility private --execute
```

既定は `private` である。既存リポジトリ、既存の `.git`、別リポジトリの内側では停止する。force push、既存ファイルの上書き、公開範囲の変更は行わない。生成物 `_site/` とPythonキャッシュは登録しない。

公開する判断を行った場合のみ `--visibility public` を指定する。作成先のユーザー／組織に対する権限はGitHub側で必要となる。

## 途中で失敗した場合

認証・ネットワーク・権限・組織ルールにより、リポジトリ作成またはpushが失敗することがある。スクリプトはリモートを自動削除して取り消さない。ローカルの状態と、GitHub上に空のリポジトリができているかを確認する。

初期コミットが存在し、対象リポジトリが空であると確認した場合に限り、表示されたURLを使って通常の `git remote add` と `git push -u origin main` で再開する。既存コンテンツのあるリポジトリへ強制pushしない。

## 既存リポジトリへ追加する場合

新規作成スクリプトを使わない。対象をcloneし、新しい作業ブランチへこの配布物をコピーする。既存のREADMEや `.github` 設定を上書きせず、差分を確認してPRにする。対象リポジトリが指定されていないため、この配布物では自動移植しない。

## GitHub Pagesを使う場合

**Pagesは任意である。MarkdownをGitHubで読むだけなら不要である。**

公開の影響を確認し、リポジトリのSettings → Pages → Build and deploymentでSourceをGitHub Actionsにする。利用可能性やアクセス制御は契約・設定に依存するため、[公式手順](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)を確認する。

Actionsで `Publish reader (manual)` を選び、公開内容を確認したうえでRun workflowを実行する。このワークフローは手動実行のみで、通常のpushやPRから公開しない。

配置されるのは `_site/` の読者用出力である。Markdown原本、公開スクリプト、検証用コードをそのままサイトへ配置しない。URLは実際に成功したPagesジョブから取得する。推測した公開URLを案内しない。

## CI設定の保守

検証ワークフローは `contents: read` のみとし、公開ジョブにのみ `pages: write` と `id-token: write` を与える。Pagesは公開確認の入力が真の場合だけ動く。

GitHub Actionsの主要バージョンは作成時の公式リポジトリを参照した。参照先は [checkout](https://github.com/actions/checkout)、[setup-python](https://github.com/actions/setup-python)、[upload-artifact](https://github.com/actions/upload-artifact) である。Pandocはローカル検証に使った3.1.11.1へ固定した。厳格な供給網管理が必要な運用では、組織の基準に従ってActionのコミットSHA固定と配布バイナリのハッシュ照合を追加する。

ワークフロー定義を同梱していることと、GitHub上でその実行が成功済みであることは区別する。この版のリモート実行は未実施である。
