#!/usr/bin/env python3
"""Generate original, editable, dependency-free SVG diagrams deterministically."""
from pathlib import Path
from html import escape
import json, math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'illustrations'
BG, INK, MUTED, TEAL, ORANGE, BLUE = '#f8f7f2', '#182e3a', '#566773', '#087f83', '#b95130', '#3c60a4'

class Figure:
    def __init__(self, number, title, subtitle, height=680):
        self.h = height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">', f'<title id="title">{escape(title)}</title>',f'<desc id="desc">{escape(subtitle)}</desc>', '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9" fill="none" stroke="#566773" stroke-width="1.4"/></marker></defs>', f'<rect width="1200" height="{height}" rx="20" fill="{BG}"/>', '<g font-family="system-ui, Noto Sans CJK JP, Hiragino Kaku Gothic ProN, Meiryo, sans-serif">']
        self.text(50,52,f'COMPLEXITY / ORDER     {number:02d}',18,TEAL,weight=700)
        self.text(50,103,title,34,weight=700)
        self.text(50,141,subtitle,21,MUTED)
        self.line(50,166,1150,166,color='#d5dedc',width=1)
    def text(self,x,y,text,size=24,color=INK,anchor='start',weight=400):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(text))}</text>')
    def line(self,x1,y1,x2,y2,color=MUTED,width=2,arrow=False,dash=False):
        extra=(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="8 7"' if dash else '')
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{extra}/>')
    def path(self,d,color=MUTED,width=2,arrow=False,dash=False):
        extra=(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="8 7"' if dash else '')
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{extra}/>')
    def box(self,x,y,w,h,title,subtitle='',color=TEAL):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#ffffff" stroke="{color}" stroke-width="2"/>')
        self.text(x+w/2,y+(h/2+8 if not subtitle else h/2-4),title,25,color,anchor='middle',weight=700)
        if subtitle:self.text(x+w/2,y+h/2+30,subtitle,20,MUTED,anchor='middle')
    def circ(self,x,y,r=10,color=TEAL):
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>')
    def panel(self,x,y,w,h):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="none" stroke="#cad5d3" stroke-width="2" stroke-dasharray="7 7"/>')
    def footer(self,text): self.text(50,self.h-28,text,19,MUTED)
    def save(self,name):
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/name).write_text('\n'.join(self.parts+['</g>','</svg>'])+'\n',encoding='utf-8')

def network(f,cx,cy,n,r,all_edges=True,color=TEAL):
    pts=[(cx+r*math.cos(2*math.pi*i/n-math.pi/2),cy+r*math.sin(2*math.pi*i/n-math.pi/2)) for i in range(n)]
    if all_edges:
        for i,p in enumerate(pts):
            for q in pts[i+1:]:f.line(*p,*q,color='#aec1c4',width=1.5)
    for p in pts:f.circ(*p,10,color)
    return pts

def main():
    chapters=json.loads((ROOT/'series.json').read_text())['chapters']
    filenames={c['number']:Path(c['figure']).name for c in chapters}
    f=Figure(0,'複雑さをなくす、から。成立させる、へ。','階層・自己組織化・自律性をめぐる、全12回の連載',660)
    network(f,225,350,12,100)
    f.text(225,500,'相互作用',28,anchor='middle',weight=700)
    f.line(360,350,470,350,arrow=True)
    for x,y in [(550,270),(650,385),(490,410)]:network(f,x,y,4,40)
    f.line(550,310,520,375);f.line(585,290,635,350)
    f.text(580,500,'局所化と階層',28,anchor='middle',weight=700)
    f.line(735,350,835,350,arrow=True)
    f.box(880,245,230,75,'観測・判断')
    f.box(880,395,230,75,'行動・検証',color=ORANGE)
    f.path('M 970 320 L 970 395',arrow=True)
    f.path('M 1040 395 C 1160 395 1160 280 1110 280',arrow=True)
    f.text(995,525,'自律と自己観測',28,anchor='middle',weight=700)
    f.footer('原典の理論・説明用モデル・工学的な応用を区別して読む。')
    f.save('00-cover.svg')

    f=Figure(1,'数が同じでも、関係の増え方は違う','12要素を、全結合と局所接続で比較する')
    network(f,290,360,12,145)
    f.text(290,570,'全結合：66関係',30,anchor='middle',weight=700)
    groups=[]
    for x,y in [(865,270),(725,460),(1005,460)]:
        f.panel(x-67,y-67,134,134)
        groups.append(network(f,x,y,4,43))
    f.line(*groups[0][3],*groups[1][0],color=ORANGE,width=3)
    f.line(*groups[0][1],*groups[2][0],color=ORANGE,width=3)
    f.text(870,570,'内部18 ＋ 境界2 ＝ 20関係',28,anchor='middle',weight=700)
    f.footer('右は接続そのものを制限した模型。分類ラベルを付けるだけでは関係は減らない。')
    f.save(filenames[1])

    f=Figure(2,'境界は、交換を止めるためだけにない','開放系を、要素・関係・境界・環境として捉える')
    f.panel(340,205,520,350)
    f.text(600,245,'システムの境界',24,anchor='middle',weight=700)
    for x,y,name in [(475,325,'要素 A'),(725,325,'要素 B'),(600,465,'要素 C')]:f.box(x-76,y-34,152,68,name)
    f.line(551,325,649,325,arrow=True);f.line(702,360,640,427,arrow=True);f.line(560,427,494,360,arrow=True)
    f.text(600,397,'相互作用',22,anchor='middle')
    f.text(172,325,'環境からの供給',23,anchor='middle');f.line(80,380,340,380,color=ORANGE,arrow=True)
    f.text(1022,325,'環境への流出',23,anchor='middle');f.line(860,380,1120,380,color=ORANGE,arrow=True)
    f.text(600,606,'同じ部品でも、関係と境界が変われば全体の働きが変わる。',25,anchor='middle')
    f.footer('交換・相互作用の概念図。すべての開放系が階層や自己生産を持つわけではない。')
    f.save(filenames[2])

    f=Figure(3,'動きが続くことで、パターンが保たれる','加熱された流体の対流を、散逸構造の概念例として見る')
    f.parts.append('<rect x="180" y="240" width="840" height="270" rx="12" fill="#edf3f2" stroke="#cad5d3" stroke-width="2"/>')
    f.line(180,240,1020,240,color=BLUE,width=12);f.line(180,510,1020,510,color=ORANGE,width=12)
    f.text(600,211,'低温側へ熱が流れる',24,BLUE,anchor='middle')
    f.text(600,563,'高温側から供給が続く',24,ORANGE,anchor='middle')
    for i,x in enumerate([320,600,880]):
        curve=(f'M {x-50} 452 C {x-120} 418 {x-120} 308 {x-35} 294 C {x+85} 274 {x+125} 408 {x+48} 451' if i%2==0 else f'M {x+48} 451 C {x+125} 408 {x+85} 274 {x-35} 294 C {x-120} 308 {x-120} 418 {x-50} 452')
        f.path(curve,color=TEAL,width=5,arrow=True)
    for x in [320,600,880]:f.line(x,610,x,575,color=ORANGE,arrow=True);f.line(x,232,x,219,color=BLUE,arrow=False)
    f.footer('外部駆動と不可逆過程のもとで維持される秩序。対流の存在は階層形成の証明ではない。')
    f.save(filenames[3])

    f=Figure(4,'多数の変数を、少数のモードで近似する','時間スケールの分離が成立する領域での低次元化')
    for i in range(9):
        pts=[]
        for j in range(65):
            x=65+5*j;y=228+i*35+11*math.sin(j*.35+i)*math.exp(-j/85)
            pts.append(f'{x:.1f},{y:.1f}')
        f.parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{[TEAL,BLUE,ORANGE][i%3]}" stroke-width="2"/>')
    f.text(228,578,'多数の状態変数',26,anchor='middle',weight=700)
    f.line(425,360,555,360,arrow=True)
    f.box(590,240,500,100,'遅い秩序変数 u','巨視的な振る舞いを記述')
    f.box(590,415,500,100,'速い安定モード s','近似的に s ≈ h(u)',color=BLUE)
    f.line(840,340,840,410,arrow=True)
    f.text(870,384,'緩和・追随',22,MUTED)
    f.footer('記述の次元低減と、観測・計算の費用の低減は別。近似範囲と残差の検証が必要である。')
    f.save(filenames[4])

    f=Figure(5,'生産する過程が、自分の成立条件をつくる','構成要素・境界・生産過程の循環を、細胞の概念模型として描く')
    f.panel(280,205,640,365)
    f.box(385,245,430,86,'生産・代謝の過程 P')
    f.box(360,435,480,92,'構成要素 C と境界 B')
    f.path('M 460 331 L 460 430',arrow=True);f.text(415,388,'生成',22,anchor='end')
    f.path('M 740 435 L 740 336',arrow=True);f.text(775,388,'実現・維持',22)
    f.text(118,346,'外部資源',24,anchor='middle');f.line(55,383,275,383,color=ORANGE,arrow=True)
    f.text(1050,346,'外部への排出',24,anchor='middle');f.line(925,383,1145,383,color=ORANGE,arrow=True)
    f.footer('循環図だけではオートポイエーシスの証明にならない。実際の生産と境界の条件を問う。')
    f.save(filenames[5])

    f=Figure(6,'成立を助ける関係と、変更を難しくする関係','自己触媒集合とNKモデルの「関係」は、同じものではない')
    f.panel(45,205,535,362);f.panel(620,205,535,362)
    f.text(313,248,'相互触媒の概念模型',25,anchor='middle',weight=700)
    for x,y,t in [(198,335,'A'),(425,335,'B'),(310,473,'C')]:f.box(x-45,y-31,90,62,t)
    f.line(244,335,378,335,arrow=True);f.line(404,367,340,439,arrow=True);f.line(281,439,220,368,arrow=True)
    f.text(313,545,'外部の基礎資源が必要',21,MUTED,anchor='middle')
    f.text(888,248,'評価寄与の相互依存',25,anchor='middle',weight=700)
    for x,y,t in [(732,335,'x₁'),(1036,335,'x₂'),(884,481,'fᵢ')]:f.box(x-50,y-33,100,66,t,color=BLUE)
    f.line(751,370,849,445,arrow=True);f.line(1017,370,919,445,arrow=True)
    f.text(884,551,'組合せで評価が変わる',21,MUTED,anchor='middle')
    f.footer('左は反応の促進、右は適応度への依存。共通の最適結合数が直接導かれるわけではない。')
    f.save(filenames[6])

    f=Figure(7,'規則に従う活動が、規則自身を対象にする','構成・実行・記述の関係を区別した、自己改訂の工学的な模型')
    f.box(330,218,540,90,'規則・Skill θ','何に従って実行するか')
    f.box(95,432,390,90,'実行と成果物','規則に従う活動',color=BLUE)
    f.box(715,432,390,90,'規則についての記述','評価・改訂案',color=ORANGE)
    f.line(435,308,313,427,arrow=True);f.text(280,360,'実行を規定',22,anchor='end')
    f.line(490,477,710,477,arrow=True);f.text(600,463,'対象化',22,anchor='middle')
    f.line(910,432,790,309,arrow=True);f.text(952,367,'改訂提案',22,anchor='middle')
    f.text(600,588,'評価基準と権限の変更は、別の承認境界で扱う。',24,anchor='middle',weight=700)
    f.footer('単なる循環や自己修正だけで、ストレンジループ・意識の成立を意味するわけではない。')
    f.save(filenames[7])

    f=Figure(8,'直すために動く。知るためにも動く。','原因仮説の更新と、情報獲得を含む行動選択')
    f.box(60,232,380,95,'観測・ログ','何が実際に起きたか',color=BLUE)
    f.box(760,232,380,95,'仮説・信念 q(s)','何が原因だと考えるか')
    f.box(760,450,380,95,'行動選択','修正する／追加調査する',color=ORANGE)
    f.box(60,450,380,95,'環境・実行結果','次の観測を生む')
    f.line(445,280,755,280,arrow=True);f.text(600,263,'観測から更新',22,anchor='middle')
    f.line(950,331,950,444,arrow=True);f.text(928,389,'価値と情報利得',22,anchor='end')
    f.line(755,497,445,497,arrow=True);f.text(600,480,'働きかける',22,anchor='middle')
    f.line(250,445,250,332,arrow=True)
    f.footer('確率モデル上の判断と、現実の正しさは別。適用は仮説であり、独立した検証を要する。')
    f.save(filenames[8])

    f=Figure(9,'速さと、選び分ける能力は違う','固定した対応ごとに結果が重複しない制御表を仮定する')
    for i in range(64): f.circ(80+(i%8)*26,245+(i//8)*26,7,BLUE)
    for i in range(16): f.circ(550+(i%4)*32,290+(i//4)*32,10,TEAL)
    for i in range(4): f.circ(964+(i%2)*70,304+(i//2)*70,18,ORANGE)
    f.line(326,340,483,340,arrow=True);f.line(732,340,891,340,arrow=True)
    f.text(185,500,'外乱：64種類',29,anchor='middle',weight=700)
    f.text(600,500,'対応：16種類',29,anchor='middle',weight=700)
    f.text(1000,500,'結果：4種類以上',27,anchor='middle',weight=700)
    f.text(600,582,'結果の種類数 ≥ ⌈ 外乱の種類数 / 対応の種類数 ⌉',27,anchor='middle')
    f.footer('モデルの必要条件。対応の有効性、観測可能性、選択精度、応答時間は別に確かめる。')
    f.save(filenames[9])

    f=Figure(10,'五つの機能であって、五段階の役職ではない','局所の自律性を、調整・統合・将来適応・方針で支える',780)
    f.box(440,205,365,75,'S5  同一性・方針')
    f.box(200,336,365,85,'S3  現在の内部統合')
    f.box(680,336,365,85,'S4  外部・将来への適応',color=ORANGE)
    f.line(510,280,430,332,arrow=True);f.line(730,280,817,332,arrow=True)
    f.line(570,378,675,378,arrow=True)
    f.box(445,469,360,73,'S2  運用間の調整',color=BLUE)
    f.box(80,610,300,83,'S1  価値提供 A','内部にも制御機能')
    f.box(455,610,300,83,'S1  価値提供 B','固有の環境と自律性')
    f.box(875,475,270,70,'S3*  直接監査',color=ORANGE)
    f.line(382,421,382,589);f.line(382,589,230,606,arrow=True);f.line(382,589,605,606,arrow=True)
    f.line(530,542,250,606,arrow=True,dash=True);f.line(625,542,625,606,arrow=True,dash=True)
    f.path('M 1010 545 L 1010 652 L 760 652',color=ORANGE,arrow=True,dash=True)
    f.path('M 1010 475 L 1010 447 L 500 447 L 500 421',color=ORANGE,arrow=True,dash=True)
    f.footer('通信経路を省略した概念図。S1は単なる分業工程ではなく、価値提供と自律性で境界を考える。')
    f.save(filenames[10])

    f=Figure(11,'観測の条件も、検証の対象にする','評価する側のモデル・目的・介入を含めて考える')
    f.panel(65,205,1070,345)
    f.text(600,242,'観測者を含む相互作用系',24,anchor='middle',weight=700)
    f.box(110,287,355,97,'観測者・評価器','規則 θ とモデル')
    f.box(740,287,350,97,'対象システム','状態 x と振る舞い',color=BLUE)
    f.line(470,320,735,320,arrow=True);f.text(600,303,'判断・介入',22,anchor='middle')
    f.line(735,360,470,360,arrow=True);f.text(600,398,'観測・証拠',22,anchor='middle')
    f.box(390,446,420,72,'観測規則の再検討',color=ORANGE)
    f.path('M 285 384 L 285 480 L 385 480',arrow=True);f.path('M 815 480 L 915 480 L 915 389',arrow=True)
    f.text(600,601,'対象・基準・手順・版・根拠・未検証範囲を記録する。',25,anchor='middle')
    f.footer('観測者の存在は、再現可能な比較の放棄を意味しない。どの条件で確かめたかを公開する。')
    f.save(filenames[11])

    f=Figure(12,'複雑さを減らすことが、次の複雑さを可能にする','連載全体を結ぶ設計上の解釈。各接続には条件がある。',760)
    f.box(95,235,350,90,'複雑な相互作用','要素と関係が増える',color=BLUE)
    f.box(750,235,350,90,'局所的な秩序','安定したまとまりが生じる')
    f.box(750,485,350,90,'階層・自律性','内部で扱い、境界でつなぐ')
    f.box(95,485,350,90,'高次の複雑さ','新しい活動が可能になる',color=ORANGE)
    f.line(450,280,745,280,arrow=True);f.text(600,263,'条件付きの形成',21,anchor='middle')
    f.line(925,330,925,480,arrow=True);f.text(950,410,'局所化・統合',21)
    f.line(745,530,450,530,arrow=True);f.text(600,512,'対応能力の拡大',21,anchor='middle')
    f.line(270,480,270,330,arrow=True);f.text(245,410,'新しい相互作用',21,anchor='end')
    f.box(430,357,345,80,'観測・検証・再設計',color=ORANGE)
    f.text(600,664,'どれほどの複雑さを、私たちは成立させられるのか。',30,anchor='middle',weight=700)
    f.footer('自然科学の単一の法則でも、すべての系がたどる発達順序でもない。')
    f.save(filenames[12])
    print(f'Generated {len(chapters)+1} SVG files in {OUT}')

if __name__=='__main__':main()
