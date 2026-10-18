# 編集・保守ガイド

[連載目次へ](../README.md)

## 原本と生成物の責務

| パス | 責務 | 編集方法 |
| --- | --- | --- |
| `chapters/*.md` | 各回の本文、数式、脚注、前後リンク | 直接編集する |
| `series.json` | 全12回の順序、題名、概要、本文・図・出典の対応 | 本文変更と同じPRで整合させる |
| `assets/illustrations/*.svg` | 本文から参照する独立した挿絵 | 再生成またはSVG編集 |
| `scripts/draw_figures.py` | 全13図を再現する図形コード | 原則としてこちらを編集して図を生成する |
| `references/sources.json` | 文献の書誌と今回の確認範囲 | 一次情報と確認状況を分けて更新する |
| `references/bibliography.md` | 読者向けの文献一覧 | sources.jsonと同じPRで更新する |
| `site-src/styles.css` | HTML閲覧用の見た目 | 本文内容を持たせない |
| `scripts/build.py` | MarkdownをMathML付きHTMLへ変換 | 原本を改変しない |
| `scripts/validate.py` | 本文・参照・SVG・数式の構造検査 | 検査規則を保守する |
| `scripts/check_html.py` | HTMLの相対リンク・アンカー・MathML・外部依存を検査 | 生成後に実行する |
| `tests/` | 検査・変換の回帰試験 | 成功例と失敗例を両方持つ |
| `scripts/publish.py` | 新規GitHubリポジトリ作成の補助 | 既存リポジトリには使わない |
| `_site/` | ブラウザ用生成物 | 直接編集せず再生成する |

## 変更の最小手順

```sh
# Markdown、図の生成コード、出典を編集した後
python scripts/draw_figures.py
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/check_html.py
```

SVGを直接修正すると次の図再生成で上書きされる。長期保守する変更は `draw_figures.py` に反映する。全12回の枠組みは固定し、追加連載は別シリーズとして扱う。

## 数式の記法

本文内の数式は `$...$`、独立した数式は次の形式とする。数式全体をコードフェンスで囲まない。

```text
$$
E(n)=rac{n(n-1)}{2}.
$$
```

TeXでは半角のバックスラッシュを使う。`aligned` などはPandocでMathMLへ変換できる範囲で使う。GitHub独自またはブラウザ独自のマクロを増やさない。数式の前後に、仮定、変数の意味、得られる結論と得られない結論を書く。

検査は数式として解析されたか、MathMLに変換できるかを確認する。数学的な正しさを機械的に証明するものではない。変更した式は数値例でも照合する。

## SVGの記法

Markdownから `![図の内容](../assets/illustrations/01-complexity-hierarchy.svg)` のように相対参照する。SVGコードを本文へ貼り付けない。

SVGには `viewBox`、`role="img"`、`title`、`desc` を持たせる。本文にも代替テキストと、前提を説明するキャプションを置く。`script`、`foreignObject`、外部画像、外部フォント、イベントハンドラは入れない。矢印や色だけに意味を依存させず、ラベルでも区別する。

日本語の表示は閲覧環境のフォントを利用する。フォントファイルは同梱しない。白系の背景をSVG自体に置き、GitHubのダークテーマでも文字と線のコントラストが保たれるようにする。

## 出典の管理

文献は本文の脚注 `[^simon]` と末尾の脚注定義でつなぐ。同じIDを `sources.json` と `series.json` でも使う。原典の語句を引用する場合は、引用符、引用範囲、ページを明示し、長文転載はしない。

機械検査はURLの構文とローカル参照を検査する。外部URLの生存や、文献が主張を本当に支えるかは編集レビューで確認する。外部サービスの一時的な制限をCIの必須成功条件にしない。

## 公開前の目視確認

GitHubのPreview、HTMLのデスクトップ幅とスマートフォン幅で確認する。長い式や表の局所スクロールは許容するが、ページ全体の横はみ出し、欠けた日本語、切れた図の文字、数式が生TeXになる状態は修正する。

## 任意のブラウザ回帰試験

`browser_smoke.py` は任意の追加検査であり、通常のビルド・CIの依存ではない。Playwrightを別途導入した環境で実行する。

```sh
python -m pip install playwright
python -m playwright install chromium
python scripts/browser_smoke.py
```

既存のChromiumを指定する場合は `--browser /path/to/chromium` を付ける。スクリーンショットと判定結果を `verification-artifacts/` に出力する。

この検査は生成HTMLをブラウザへ直接投入し、検査時だけ相対参照のSVGを埋め込む。`file://` やHTTP経由の読み込み経路、GitHubの実際のPreview、Pagesの認証・公開状態の検査ではない。
