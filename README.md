# 複雑さと秩序

## 階層・自己組織化・自律性をめぐる全12回

![全12回の主題を、相互作用、局所化と階層、自律と自己観測として示した表紙](assets/illustrations/00-cover.svg)

**必要な複雑さを持ち、そのすべてを、すべての参加者へ負わせない。**

複雑度のオーダーから出発し、秩序形成、自己維持、環境への適応、観測する主体までをたどる連載である。各回は独立した読み物であり、末尾の問いが次回につながる。第12回は連載全体を振り返るエッセイとなる。

[第1回から読む](chapters/01-complexity-hierarchy.md) ／ [最終回を読む](chapters/12-complexity-and-order.md) ／ [読み方](guides/READING.md)

## 全12回の目次

| 回 | 文章 | 主題 |
| --- | --- | --- |
| 01 | [複雑さを減らすと、何が増えるのか](chapters/01-complexity-hierarchy.md) | 複雑度のオーダーとサイモンの階層論 |
| 02 | [部品を並べても、全体にはならない](chapters/02-general-system-theory.md) | ベルタランフィの一般システム理論 |
| 03 | [流れているから、かたちが保たれる](chapters/03-dissipative-structures.md) | プリゴジンの散逸構造論 |
| 04 | [一万の動きを、一つの動きとして読む](chapters/04-synergetics.md) | ハーケンのシナジェティクスと隷属原理 |
| 05 | [壊れないのではなく、つくり直している](chapters/05-autopoiesis.md) | オートポイエーシスと自己生産 |
| 06 | [つながるほど生まれやすく、変わりにくくなる](chapters/06-kauffman.md) | 自己触媒集合とNKモデル |
| 07 | [規則に従うものが、規則を書く](chapters/07-strange-loops.md) | ホフスタッターのストレンジループ |
| 08 | [直す前に、何を知るべきか](chapters/08-active-inference.md) | 自由エネルギー原理と能動的推論 |
| 09 | [速くするだけでは、制御できない](chapters/09-requisite-variety.md) | アシュビーの必要多様性の法則 |
| 10 | [中央がすべてを知らなくても、全体は動く](chapters/10-viable-system-model.md) | ビーアの生存可能システムモデル |
| 11 | [測る側も、測られている系の中にいる](chapters/11-second-order-cybernetics.md) | フォン・フェルスターの第二次サイバネティクス |
| 12 | [複雑さは、なぜ秩序を生むのか](chapters/12-complexity-and-order.md) | 階層、自己組織化、そして自律するシステム |

第1回で複雑度とサイモンの階層論を扱う。以降は一回につき一つの主題を中心に接続し、最後に十一の理論的視点を総括する。理論の数を、そのまま科学上の発達段階とみなす構成ではない。

<!-- SITE-INDEX-END: 以下はリポジトリ利用者向け。HTML閲覧版のトップページには含めない。 -->

## GitHubで読む

このREADMEと各回の `.md` をGitHubの **Preview** で開く。本文中の図は相対リンク先のSVG、数式は `$...$` と `$$...$$` の数式として表示する。[GitHub公式の数式仕様](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)を用いるため、Markdown閲覧のためにPagesや専用アプリを起動する必要はない。

外部の画像・フォント・数式画像APIを参照しない。挿絵13点は編集可能な独立SVGである。数学的な式はテキストから組版される。SVGの中に数式画像を隠して代替する構成ではない。

## ブラウザで読む

配布ZIPの `_site/index.html` を開くと、目次付きの閲覧ページを読める。`_site/complete.html` は全12回とSVGを一つにまとめたHTMLであり、単独で持ち運べる。数式はネイティブMathMLなので外部CDNやJavaScriptを必要としない。

再生成にはPython 3.11以降とPandoc 3.xを使う。この版はPython 3.13.5・Pandoc 3.1.11.1で検証済みである。CIはPython 3.11を指定するが、GitHub上の実行は未実施である。依存パッケージの追加インストールは不要である。

```sh
python scripts/validate.py
python scripts/build.py
python -m unittest discover -s tests -v
```

GitHub管理対象はMarkdownとSVGなどの原本である。`_site/` は生成物として `.gitignore` で除外する。GitHub Pagesへの配置は手動実行のワークフローで行える。

## 編集・保守・公開

[編集ガイド](guides/EDITING.md)には原本の責務、SVG・数式・出典の編集規則をまとめた。[文体の規則](guides/STYLE.md)には本文の文のリズムと留保の置き方をまとめた。[GitHub登録・Pages公開手順](guides/PUBLISHING.md)には非公開リポジトリ作成用コマンドと公開時の注意を示す。[編集方針と検証範囲](guides/EDITORIAL.md)では、会話からの再編集、理論と応用の区別、出典確認の限界を記載する。

## 原典へ戻る

[参考文献と確認範囲](references/bibliography.md)から、各理論の出典を参照できる。本文の文献注は、その理論の参照先であり、原文の引用ではない。独自の説明用数式、図、開発組織への応用は、本文で区別している。

自然科学の法則、数学的な模型、認知の概念、組織設計の枠組みを一つの普遍法則として扱わない。本連載で示す接続は、次に検証すべき問いをつくるための解釈である。
