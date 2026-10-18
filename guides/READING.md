# 読み方と表示環境

[連載目次へ](../README.md)

## GitHubのMarkdownで読む

リポジトリのREADMEから各回を開き、Preview表示を使う。RawやCode表示は原稿テキストを見るためのものであり、図や数式は組版されない。各回の冒頭と末尾に、前回・目次・次回のリンクがある。

数式はGitHubが対応する `$x$` と `$$` のブロックを使う。公式仕様は[Writing mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)を参照する。GitHubの表示を第三者製Markdownビューアと同一だとは仮定しない。

## HTMLで読む

配布物では `_site/index.html` をブラウザで開く。サーバー起動は不要である。目次、相対リンクの図、数式をローカルで表示する。クールごとの全回を一つのファイルで読む場合は `_site/complete.html`（第1クール）を開く。

HTMLはPandocの `--mathml` で生成する。現行の主要ブラウザではMathMLを数式として表示できるが、古いブラウザや独自のHTMLプレビューには対応しない場合がある。本配布物の具体的な確認結果は、[実装検証レポート](VALIDATION.md)を参照する。

数式が崩れる場合は、まず通常のブラウザで開く。企業のメール内プレビューやHTMLを除去するビューアは使わない。GitHubのMarkdown表示でも読むことができる。

## 再生成する

Python 3.11以降とPandoc 3.xを利用する。Python標準ライブラリだけを使うため、pipによる追加導入は不要である。Pandocの導入方法は[公式インストール案内](https://pandoc.org/installing.html)を参照する。

```sh
python --version
pandoc --version
python scripts/validate.py
python scripts/build.py
```

WindowsでPythonコマンドが `py` の場合は `py -3 scripts/build.py` とする。HTMLを作る前にMarkdownの検査を行い、警告を残したまま公開しない。

## 図・注・数式の読み分け

挿絵は原典の転載ではなく、本連載の説明のために作成した概念図である。矢印は必ずしも因果法則を表さない。キャプションに示す前提を併せて読む。

式には、理論で使われる式、本文で仮定を置いて導出した模型、工学的な応用のための式がある。どの変数を何のために数えるかを確認する。関係数、状態数、推論の次元、時間計算量、情報量を同じ「複雑度」として足し合わせない。
