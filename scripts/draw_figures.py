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
        label=f'{number:02d}' if isinstance(number,int) else str(number)
        self.text(50,52,f'COMPLEXITY / ORDER     {label}',18,TEAL,weight=700)
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

def polyline(pts):
    return 'M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)


def figure_3_2(name):
    """図3-2: 超臨界ピッチフォーク分岐の正規形 u' = μu − u³ の定常解と安定性。"""
    f=Figure('03-2','同じ揺らぎでも、戻されるか増幅されるかが変わる','超臨界ピッチフォーク分岐の正規形 u̇ = μu − u³ の定常解と安定性',640)
    X=lambda mu:600+400*mu
    Y=lambda u:395-137.5*u
    f.line(180,395,1020,395,color=INK,width=1.5,arrow=True)
    f.line(600,575,600,220,color=INK,width=1.5,arrow=True)
    f.text(1150,388,'μ（駆動の強さ）',20,MUTED,anchor='end')
    f.text(614,214,'u（パターンの振幅）',20,MUTED)
    f.text(592,422,'μ = 0（分岐点）',18,MUTED,anchor='end')
    f.line(X(-1),Y(0),X(0),Y(0),color=TEAL,width=4)
    f.line(X(0),Y(0),X(1),Y(0),color=ORANGE,width=3,dash=True)
    mus=[i/40 for i in range(41)]
    f.path(polyline([(X(m),Y(math.sqrt(m))) for m in mus]),color=TEAL,width=4)
    f.path(polyline([(X(m),Y(-math.sqrt(m))) for m in mus]),color=TEAL,width=4)
    f.text(X(-0.9),Y(0)+30,'u = 0（安定）',19,TEAL,anchor='middle')
    f.text(X(0.3),Y(0)+30,'u = 0（不安定）',19,ORANGE,anchor='middle')
    f.text(X(1)+10,Y(1)+7,'u = +√μ',19,TEAL)
    f.text(X(1)+10,Y(-1)+7,'u = −√μ',19,TEAL)
    for u0,u1 in [(0.55,0.08),(-0.55,-0.08)]:f.line(X(-0.6),Y(u0),X(-0.6),Y(u1),color=BLUE,width=2.5,arrow=True)
    f.text(X(-0.6),Y(0.8)-6,'ずれは戻される',20,BLUE,anchor='middle',weight=700)
    for u0,u1 in [(0.12,0.68),(-0.12,-0.68),(1.15,0.86),(-1.15,-0.86)]:f.line(X(0.6),Y(u0),X(0.6),Y(u1),color=BLUE,width=2.5,arrow=True)
    f.text(X(0.6),Y(-1.2)+28,'u = 0 からのずれは増幅され、±√μ で止まる',20,BLUE,anchor='middle',weight=700)
    f.line(190,206,250,206,color=TEAL,width=4);f.text(262,212,'実線 = 安定な定常解',19,MUTED)
    f.line(190,234,250,234,color=ORANGE,width=3,dash=True);f.text(262,240,'破線 = 不安定な定常解',19,MUTED)
    f.footer('正規形の説明図。対流の実験データではない。μ は駆動の強さを表す一般的な記号。')
    f.save(name)


def ring(f,x,y,r,color=TEAL,width=2):
    f.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#ffffff" stroke="{color}" stroke-width="{width}"/>')


def rect(f,x,y,w,h,color=TEAL,dash=False,width=2):
    extra=' stroke-dasharray="7 6"' if dash else ''
    f.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#ffffff" stroke="{color}" stroke-width="{width}"{extra}/>')


def card(f,x,y,w,h,title,subtitle,color=TEAL):
    rect(f,x,y,w,h,color)
    f.text(x+w/2,y+27,title,min(20,round(215/max(len(title),1))),color,anchor='middle',weight=700)
    f.text(x+w/2,y+52,subtitle,16,MUTED,anchor='middle')


def figure_6_2(name):
    """図6-2: K=0 の単峰な適応度地形と、K が大きいときの多峰な地形（概念図）。"""
    f=Figure('06-2','依存が増えるほど、局所の改善が途中で止まる','K=0 の単峰な地形と、K が大きいときの多峰な地形の概念図',620)
    smooth=lambda x:math.exp(-((x-0.5)/0.3)**2)
    rugged=lambda x:0.55+0.25*math.sin(7*x)+0.12*math.sin(17*x+1)+0.08*math.sin(29*x+2)
    def climb(F,x,step=1/400):
        while True:
            nxt=max([v for v in (x-step,x,x+step) if 0<=v<=1],key=F)
            if nxt==x:return x
            x=nxt
    for px,F,start,head in [(70,smooth,0.15,'K = 0：各要素の良い選択を別々に選べる'),(620,rugged,0.13,'K が大きい：一つを直すと別の寄与が動く')]:
        f.panel(px,200,510,330);f.text(px+20,232,head,21,INK,weight=700)
        X=lambda x:px+50+420*x
        Y=lambda v:500-220*v
        f.line(px+50,500,px+490,500,color=INK,width=1.5,arrow=True);f.line(px+50,500,px+50,255,color=INK,width=1.5,arrow=True)
        f.text(px+488,522,'構成（隣り合う構成が隣）',17,MUTED,anchor='end');f.text(px+58,252,'適応度 F',17,MUTED)
        xs=[i/120 for i in range(121)]
        f.path(polyline([(X(x),Y(F(x))) for x in xs]),color=TEAL,width=3)
        stop=climb(F,start);steps=[start+(stop-start)*k/4 for k in range(5)]
        for a,b in zip(steps,steps[1:]):f.line(X(a),Y(F(a)),X(b),Y(F(b)),color=ORANGE,width=2.5,arrow=True)
        f.circ(X(start),Y(F(start)),7,ORANGE);f.text(X(start),Y(F(start))+30,'出発',16,ORANGE,anchor='middle')
        f.circ(X(stop),Y(F(stop)),8,ORANGE)
        if F is smooth:
            f.text(X(stop),Y(F(stop))-18,'頂上に着く',18,ORANGE,anchor='middle',weight=700)
        else:
            gx=max(xs,key=F)
            assert abs(gx-stop)>0.05,'局所探索が全体の最適に着いてしまう'
            f.text(X(stop),Y(F(stop))-18,'局所最適で止まる',18,ORANGE,anchor='middle',weight=700)
            f.circ(X(gx),Y(F(gx)),8,TEAL);f.text(X(gx)+14,Y(F(gx))-10,'全体の最適',18,TEAL,weight=700)
            f.line(X(stop),Y(F(stop)),X(gx),Y(F(gx)),color=MUTED,width=1.5,dash=True)
    f.footer('概念図。特定のNKモデルの実行結果ではない。横軸は隣り合う構成を隣に並べた一次元の略図。')
    f.save(name)


def figure_4_2(name):
    """図4-2: 例 εs' = −s + u² の遅い多様体 s ≈ u² と、u が急変したときの遅れ。"""
    f=Figure('04-2','速い変数は、遅い変数が決める曲線へ落ちる','例 εṡ = −s + u² の先頭近似 s ≈ u² と、u が急変したときの遅れ',640)
    f.panel(70,200,640,330);f.text(90,232,'曲線は s = h₀(u) = u²',21,INK,weight=700)
    X=lambda u:390+280*u
    Y=lambda s:500-240*s
    f.line(100,500,690,500,color=INK,width=1.5,arrow=True);f.line(390,500,390,228,color=INK,width=1.5,arrow=True)
    f.text(690,522,'u',18,MUTED,anchor='end');f.text(378,236,'s',18,MUTED,anchor='end')
    us=[-1+i/30 for i in range(61)]
    f.path(polyline([(X(u),Y(u*u)) for u in us]),color=TEAL,width=4)
    for u,s0 in [(-0.7,0.95),(-0.3,0.70),(0.5,0.02),(0.8,1.05)]:f.line(X(u),Y(s0),X(u),Y(u*u),color=BLUE,width=2.5,arrow=True)
    f.text(100,262,'速い緩和（ε が小さい）',19,BLUE,weight=700)
    slow=[-0.6+1.2*i/40 for i in range(41)]
    f.path(polyline([(X(u),Y(u*u)) for u in slow]),color=ORANGE,width=3,arrow=True)
    f.text(390,528,'遅い変化：u の変化に合わせて曲線上を動く',18,ORANGE,anchor='middle',weight=700)
    f.panel(750,200,380,330);f.text(770,232,'u が急変した直後、s は追いつかない',21,INK,weight=700)
    T=lambda t:800+75*t
    V=lambda v:490-200*v
    f.line(800,490,1112,490,color=INK,width=1.5,arrow=True);f.line(800,490,800,262,color=INK,width=1.5,arrow=True)
    f.text(1112,512,'t',18,MUTED,anchor='end')
    f.path(polyline([(T(0),V(0.2)),(T(1),V(0.2)),(T(1),V(0.8)),(T(4),V(0.8))]),color=ORANGE,width=3)
    f.text(1106,V(0.8)+6,'u',18,ORANGE,weight=700)
    ts=[1+3*i/60 for i in range(61)]
    f.path(polyline([(T(0),V(0.04)),(T(1),V(0.04))]+[(T(t),V(0.64-0.60*math.exp(-(t-1)/0.5))) for t in ts]),color=BLUE,width=3)
    f.text(1106,V(0.64)+22,'s',18,BLUE,weight=700)
    f.line(T(1),V(0.04),T(1),V(0.8),color=MUTED,width=1.5,dash=True);f.text(T(1),262,'急変',17,MUTED,anchor='middle')
    f.footer('説明用の例。初期の速い過渡、安定な解の存在、時間スケール分離を省いた厳密な等式ではない。')
    f.save(name)


def figure_2_2(name):
    """図2-2: 等結果性。異なる初期状態や経路が同じ定常状態へ到達し得る（概念図）。"""
    f=Figure('02-2','出発点が違っても、同じ定常状態へ着く','開放系の等結果性。異なる初期状態や経路が、同じ最終状態に到達し得る',600)
    tx,ty=830,380
    f.panel(560,250,320,260);f.text(866,484,'違いを吸収する仕組み',18,MUTED,anchor='end');f.text(866,504,'（流入と流出の釣り合いなど）',16,MUTED,anchor='end')
    starts=[('A',170,250,480,200),('B',170,470,480,560),('C',340,500,600,530),('D',300,215,560,230)]
    for label,sx,sy,cx,cy in starts:
        # end the curve on a circle of radius 40 around the target
        ang=math.atan2(cy-ty,cx-tx);ex,ey=tx+40*math.cos(ang),ty+40*math.sin(ang)
        f.path(f'M{sx},{sy} Q{cx},{cy} {ex:.1f},{ey:.1f}',color=MUTED,width=2.5,arrow=True)
        f.circ(sx,sy,10,ORANGE)
    f.text(170,232,'初期状態 A',18,ORANGE,anchor='middle');f.text(170,500,'初期状態 B',18,ORANGE,anchor='middle')
    f.text(340,530,'初期状態 C',18,ORANGE,anchor='middle');f.text(300,197,'初期状態 D',18,ORANGE,anchor='middle')
    ring(f,tx,ty,34,TEAL,2);f.circ(tx,ty,22,TEAL);f.text(tx,442,'同じ定常状態',22,TEAL,anchor='middle',weight=700)
    f.box(900,440,240,80,'条件','一定の条件を満たす開放系')
    f.footer('概念図。どの仕組みが初期条件の違いを吸収するかは、系ごとに調べる。')
    f.save(name)


def figure_1_2(name):
    """図1-2: サイモンの二人の時計職人の比喩。部分組立があると中断で失う範囲が小さい。"""
    f=Figure('01-2','中断されても、部分組立は残る','サイモンの二人の時計職人の比喩。安定した部分組立があると、途中の成果を失いにくい',640)
    f.panel(70,200,510,350);f.text(90,232,'一度に組み上げる',21,INK,weight=700)
    f.panel(620,200,510,350);f.text(640,232,'部分組立をつくる',21,INK,weight=700)
    # left: one chain of 12 parts, 8 assembled, interrupted, back to nothing
    xs=[110+40*i for i in range(12)]
    for i in range(7):f.line(xs[i],330,xs[i+1],330,color=TEAL,width=3)
    for i,x in enumerate(xs):
        (f.circ(x,330,9,TEAL) if i<8 else ring(f,x,330,9,TEAL))
    f.line(410,280,410,350,color=ORANGE,width=2,dash=True);f.text(410,270,'中断',19,ORANGE,anchor='middle',weight=700)
    f.path('M410,362 Q410,430 150,445',color=ORANGE,width=2,arrow=True);f.text(330,398,'最初へ戻る',17,ORANGE,anchor='middle')
    for x in xs:ring(f,x,470,9,TEAL)
    f.text(325,540,'失うもの：ここまでの全部',20,ORANGE,anchor='middle',weight=700)
    # right: four subassemblies of three parts
    def group(bx,y,filled,color,dash=False):
        rect(f,bx,y-30,100,60,color,dash)
        for k in range(3):
            x=bx+20+30*k
            (f.circ(x,y,9,TEAL) if k<filled else ring(f,x,y,9,TEAL))
    for j,(filled,color,dash) in enumerate([(3,TEAL,False),(3,TEAL,False),(2,ORANGE,True),(0,MUTED,True)]):group(660+120*j,330,filled,color,dash)
    f.line(950,280,950,350,color=ORANGE,width=2,dash=True);f.text(950,270,'中断',19,ORANGE,anchor='middle',weight=700)
    f.line(950,368,950,432,color=ORANGE,width=2,arrow=True);f.text(970,405,'作りかけの一組だけ戻る',17,ORANGE)
    for j,(filled,color,dash) in enumerate([(3,TEAL,False),(3,TEAL,False),(0,ORANGE,True),(0,MUTED,True)]):group(660+120*j,470,filled,color,dash)
    f.text(875,540,'失うもの：作りかけの一組だけ',20,ORANGE,anchor='middle',weight=700)
    f.footer('比喩の構図のみ。部品数や中断の確率はサイモン（1962）の設定であり、ここでは描いていない。')
    f.save(name)


def figure_12_2(name):
    """図12-2: 十一の理論を、担当する問いで配置した見取り図。順序の矢印はない。"""
    f=Figure('12-2','十一の理論は、階段ではなく問いの地図である','各理論が担当する問いで配置した連載の見取り図。順序の矢印はない',760)
    areas=[(60,200,540,250,'成り立ちを問う'),(620,200,520,250,'自分をつくり、自分を書くことを問う'),(60,480,540,200,'環境に応じることを問う'),(620,480,520,200,'測る側を問う')]
    for x,y,w,h,title in areas:f.panel(x,y,w,h);f.text(x+20,y+32,title,22,INK,weight=700)
    cards={
        1:(80,250,'第1回　サイモン','部分ごとに扱えるか'),2:(345,250,'第2回　ベルタランフィ','全体は部品の一覧か'),
        3:(80,335,'第3回　プリゴジン','流れの中で保たれるか'),4:(345,335,'第4回　ハーケン','少数の変数で記述できるか'),
        5:(640,250,'第5回　オートポイエーシス','自らを生産するか'),6:(895,250,'第6回　カウフマン','支え合うか、変えにくくなるか'),
        7:(640,335,'第7回　ホフスタッター','自分を記述するか'),
        8:(80,522,'第8回　フリストン','先に何を知るか'),9:(345,522,'第9回　アシュビー','対応の多様性は足りるか'),
        10:(80,600,'第10回　ビーア','どこで判断するか'),11:(640,522,'第11回　フォン・フェルスター','誰が測っているか')}
    W,H=235,64
    center=lambda n:(cards[n][0]+W/2,cards[n][1]+H/2)
    for n,(x,y,title,q) in cards.items():card(f,x,y,W,H,title,q)
    f.text(640,636,'図を描く側も、図の中にいる。',18,MUTED)
    f.text(640,662,'本文は第1回と第6回、第9回と第10回、第10回と第11回を行き来する。',15,MUTED)
    f.footer('配置は本連載の解釈。発達段階や一直線の順序を表さない。')
    f.save(name)


def figure_cover_2(name):
    """第2クールの表紙: 成立した秩序を学習・変化・継承させる三つの部。"""
    f=Figure('13–24','成立させる、から。更新する、へ。','秩序は、どう変わり続けるのか ― 第13〜24回の連載',660)
    # Ⅰ 意味と学習: two observers reconstruct the same document differently and exchange
    f.box(80,250,110,70,'A');f.box(300,250,110,70,'B',color=ORANGE)
    rect(f,200,355,90,56,MUTED);f.text(245,390,'文書',20,MUTED,anchor='middle')
    f.line(190,285,300,285,arrow=True);f.line(300,300,190,300,arrow=True)
    f.line(135,320,215,355,color=MUTED);f.line(355,320,275,355,color=MUTED)
    f.text(245,500,'意味と学習',28,anchor='middle',weight=700)
    f.line(440,350,520,350,arrow=True)
    # Ⅱ 硬直と崩壊: a thick, rigid block with a thin side
    f.parts.append('<rect x="560" y="250" width="200" height="130" rx="14" fill="#ffffff" stroke="#087f83" stroke-width="8"/>')
    f.parts.append('<rect x="560" y="250" width="200" height="130" rx="14" fill="none" stroke="#b95130" stroke-width="2" stroke-dasharray="7 6"/>')
    f.line(760,315,830,315,color=ORANGE,width=2.5,arrow=True);f.text(835,321,'想定外',18,ORANGE)
    f.text(660,500,'硬直と崩壊',28,anchor='middle',weight=700)
    f.line(900,350,980,350,arrow=True)
    # Ⅲ 再編成と継承: nested units carried forward
    for i,(x,y) in enumerate([(1010,245),(1010,330)]):rect(f,x,y,120,60,TEAL if i==0 else MUTED,dash=i==1)
    f.circ(1040,275,8);f.circ(1070,275,8);f.circ(1100,275,8)
    ring(f,1040,360,8);f.circ(1070,360,8);ring(f,1100,360,8)
    f.line(1070,305,1070,330,arrow=True)
    f.text(1070,500,'再編成と継承',28,anchor='middle',weight=700)
    f.footer('第1クールの結論を裏返す。秩序は可能性を開くと同時に閉じる。何を残し、何を変えるかを決め直す。')
    f.save(name)


def figure_conversation(name,final=False):
    """図13（final=False）／図24（final=True）: 同じ文書から別の概念図ができ、説明と再構成の往復で違いが見つかる。"""
    if not final:
        f=Figure(13,'届いたことと、分かったことは違う','同じ文書から別の概念図ができ、説明と再構成の往復で違いが見つかる',640)
    else:
        f=Figure(24,'同じにはならない。それでも更新し合える。','第13回と同じ二者。概念図は一致しないまま、確かめ合う往復が続く',640)
    rect(f,540,212,120,66,MUTED);f.text(600,252,'仕様書',22,MUTED,anchor='middle',weight=700)
    f.line(540,245,410,300,color=MUTED,width=1.5,arrow=True);f.line(660,245,790,300,color=MUTED,width=1.5,arrow=True)
    f.text(470,262,'読む',16,MUTED,anchor='middle');f.text(730,262,'読む',16,MUTED,anchor='middle')
    rect(f,110,300,300,230,TEAL);f.text(260,332,'Aの概念図',20,TEAL,anchor='middle',weight=700)
    rect(f,790,300,300,230,ORANGE);f.text(940,332,'Bの概念図',20,ORANGE,anchor='middle',weight=700)
    a=[(200,400),(320,400),(260,490)]
    for i in range(3):
        for j in range(i+1,3):f.line(*a[i],*a[j],color=TEAL,width=2)
    for x,y in a:f.circ(x,y,11,TEAL)
    b=[(840,400),(905,400),(970,400),(1035,400),(940,490)]
    for i in range(3):f.line(*b[i],*b[i+1],color=ORANGE,width=2)
    f.line(*b[1],*b[4],color=ORANGE,width=2)
    for x,y in b:f.circ(x,y,11,ORANGE)
    f.line(420,385,780,385,color=INK,width=2,arrow=True);f.text(600,374,'説明する（どうやるか／なぜそうなるか）',18,INK,anchor='middle',weight=700)
    f.line(780,455,420,455,color=INK,width=2,arrow=True);f.text(600,478,'別の条件で再構成してみせる',18,INK,anchor='middle',weight=700)
    if not final:
        f.text(600,560,'同じ語の下に、別の構造があったことが見つかる',20,ORANGE,anchor='middle',weight=700)
        f.footer('概念図。パスクの会話の形式化を再現したものではない。復唱は語の到達を、再構成は理解を確かめる。')
    else:
        f.text(600,560,'二つの図は一致しない。違いを確かめ、修正し、共同で動く往復が続く',20,ORANGE,anchor='middle',weight=700)
        f.footer('第13回の図と同じ構図。到達点は一致ではなく、更新し合える関係である。')
    f.save(name)


def figure_14(name):
    """図14: 同じ迷路で経路を直す（学習Ⅰ）と、迷路の区切り方を変える（学習Ⅱ）の対比。"""
    f=Figure(14,'答えを直すことと、選び方を変えることは違う','同じ迷路で経路を直す図と、迷路の区切り方そのものを変える図',620)
    for px,head in [(70,'経路を直す：与えられた区切りの中で答えを変える'),(620,'区切り方を変える：選択肢の組み立て方を変える')]:
        f.panel(px,200,510,330);f.text(px+20,232,head,20,INK,weight=700)
        ox,oy=px+60,270;cell=90
        for i in range(5):f.line(ox+i*cell,oy,ox+i*cell,oy+2*cell,color='#cad5d3',width=1.5);
        for j in range(3):f.line(ox,oy+j*cell,ox+4*cell,oy+j*cell,color='#cad5d3',width=1.5)
        f.text(ox+8,oy+2*cell+26,'入口',16,MUTED);f.text(ox+4*cell-8,oy-8,'出口',16,MUTED,anchor='end')
        if px==70:
            walls=[(2,0,2,1),(3,1,3,2)]
            for a,b,c,d in walls:f.line(ox+a*cell,oy+b*cell,ox+c*cell,oy+d*cell,color=INK,width=4)
            f.path(polyline([(ox+45,oy+135),(ox+45,oy+45),(ox+150,oy+45)]),color=MUTED,width=2.5,dash=True)
            f.text(ox+100,oy+30,'行き止まり',15,MUTED,anchor='middle')
            f.path(polyline([(ox+45,oy+135),(ox+225,oy+135),(ox+225,oy+45),(ox+315,oy+45)]),color=ORANGE,width=3,arrow=True)
            f.text(ox+135,oy+160,'直した経路',15,ORANGE,anchor='middle')
        else:
            walls=[(3,1,3,2)]
            for a,b,c,d in walls:f.line(ox+a*cell,oy+b*cell,ox+c*cell,oy+d*cell,color=INK,width=4)
            f.line(ox+2*cell,oy,ox+2*cell,oy+cell,color=ORANGE,width=4,dash=True);f.text(ox+2*cell+8,oy+cell+22,'区切りを引き直す',15,ORANGE)
            f.path(polyline([(ox+45,oy+135),(ox+45,oy+45),(ox+315,oy+45)]),color=ORANGE,width=3,arrow=True)
    f.text(325,560,'学習Ⅰ',22,TEAL,anchor='middle',weight=700);f.text(875,560,'学習Ⅱ',22,TEAL,anchor='middle',weight=700)
    f.footer('概念図。ベイトソンの論理階型の装置を再現したものではなく、本連載の類比である。')
    f.save(name)


def figure_15(name):
    """図15: 同じ入力から、目的に応じて別の特徴が残る二つの情報ボトルネック。"""
    f=Figure(15,'何を残すかは、何を判断したいかで決まる','同じ入力から、目的に応じて別々の特徴が残される二つの情報ボトルネック',640)
    items=['発生時刻','直前の変更','失敗した呼び出し','利用者の数','時間帯','機能の名前','端末の種類','再試行の回数']
    rect(f,80,215,220,370,MUTED);f.text(190,245,'入力 X（ログ）',20,MUTED,anchor='middle',weight=700)
    ys=[275+i*38 for i in range(8)]
    for y,it in zip(ys,items):f.text(190,y+6,it,17,INK,anchor='middle')
    for cy,target,keep,color in [(300,'目的 Y₁：原因の特定',[0,1,2],TEAL),(500,'目的 Y₂：影響の見積り',[3,4,5],ORANGE)]:
        f.parts.append(f'<path d="M520,{cy-70} L560,{cy-18} L560,{cy+18} L520,{cy+70} Z" fill="#ffffff" stroke="{color}" stroke-width="2.5"/>')
        f.text(540,cy+6,'T',22,color,anchor='middle',weight=700)
        for i in keep:f.line(300,ys[i],520,cy-40+40*keep.index(i),color=color,width=2)
        rect(f,640,cy-60,230,120,color);f.text(755,cy-28,'残る区別',18,color,anchor='middle',weight=700)
        for n,i in enumerate(keep):f.text(755,cy+n*24,items[i],16,INK,anchor='middle')
        f.line(870,cy,950,cy,color=color,width=2,arrow=True);f.text(960,cy+6,target,18,color,weight=700)
    f.text(540,405,'ボトルネック T',17,MUTED,anchor='middle')
    f.footer('概念図。項目は説明用の例であり、何が残るかは p(x, y) と β によって決まる。')
    f.save(name)


def figure_16(name):
    """図16: 同一システムを個別要素・集団・全体の三段階で表し、粒度ごとに見える因果が違う図。"""
    f=Figure(16,'原因が見える粒度は、一つではない','同一システムを個別要素・集団・全体の三段階で表す。粗すぎても細かすぎても見えない',640)
    heads=[('個別要素','遷移が多く、雑音と重なりが大きい'),('集団','受け渡しの単位で、次の状態がよく決まる'),('全体','区別が一つに潰れ、原因を語れない')]
    for k,(h,sub) in enumerate(heads):
        px=70+k*370;f.panel(px,200,340,330);f.text(px+20,232,h,21,INK,weight=700);f.text(px+20,258,sub,15,MUTED)
    # micro: 9 dots with many thin arrows
    import itertools
    pts=[(130+60*i,320+55*j) for j in range(3) for i in range(3)]
    for (a,b) in [(0,1),(1,2),(0,4),(3,4),(4,5),(1,4),(2,5),(4,8),(3,7),(6,7),(7,8),(5,8),(2,4),(6,4)]:
        f.line(*pts[a],*pts[b],color='#aec1c4',width=1.3,arrow=True)
    for x,y in pts:f.circ(x,y,8,TEAL)
    f.text(240,505,'一人ずつの作業履歴',16,MUTED,anchor='middle')
    # meso: 3 groups with clear arrows
    for i,x in enumerate([500,610,720]):
        rect(f,x-40,345,80,70,TEAL);f.circ(x-18,370,6);f.circ(x+18,370,6);f.circ(x,395,6)
    f.line(540,380,570,380,color=ORANGE,width=3,arrow=True);f.line(650,380,680,380,color=ORANGE,width=3,arrow=True)
    f.text(555,372,'待ち',14,ORANGE,anchor='middle');f.text(665,372,'待ち',14,ORANGE,anchor='middle')
    f.text(610,505,'チーム間の受け渡し',16,MUTED,anchor='middle')
    # macro: one box
    rect(f,900,330,220,100,MUTED);f.text(1010,385,'組織',22,MUTED,anchor='middle',weight=700)
    f.text(1010,505,'一つの状態しかない',16,MUTED,anchor='middle')
    f.footer('概念図。有効情報の計算例ではない。どの粗視化を選ぶかは分析者の決定である。')
    f.save(name)


def figure_17(name):
    """図17: 最初は対等だった二つの道が、利用者・知識・接続先の蓄積によって非対称になる図。"""
    f=Figure(17,'先に選ばれた方が、次も選ばれやすくなる','対等だった二つの道が、利用者と教材と接続先の蓄積で非対称になる',640)
    f.line(120,560,1100,560,color=INK,width=1.5,arrow=True);f.text(1100,586,'時間（採用者の到着）',17,MUTED,anchor='end')
    f.line(120,560,120,230,color=INK,width=1.5,arrow=True);f.text(132,236,'累積の採用と周辺の蓄積',17,MUTED)
    import math as _m
    ax=[(120+i*19.6,560-(0.5*i+0.11*i*i)) for i in range(51)]
    bx=[(120+i*19.6,560-(0.5*i+ (0 if i<12 else 0.02*(i-12)**2*0.5))) for i in range(51)]
    f.path(polyline([(x,max(y,235)) for x,y in ax]),color=TEAL,width=5)
    f.path(polyline(bx),color=ORANGE,width=5)
    f.text(600,300,'A：採用者・教材・接続先が積み上がる',18,TEAL,weight=700)
    f.text(480,522,'B：利用が増えず、周辺が育たない',18,ORANGE,weight=700)
    f.line(355,560,355,250,color=MUTED,width=1.5,dash=True);f.text(355,586,'初期の偶然（到着順）',16,MUTED,anchor='middle')
    f.line(640,560,640,250,color=MUTED,width=1.5,dash=True);f.text(640,586,'固定：Bを好む人もAを選ぶ',16,MUTED,anchor='middle')
    for i,(lab,y) in enumerate([('利用者',300),('教材・知識',330),('周辺システム',360)]):
        rect(f,950,y-12,150,24,TEAL);f.text(1025,y+6,lab,14,TEAL,anchor='middle')
    f.text(1025,280,'Aに積み上がるもの',15,MUTED,anchor='middle')
    f.footer('概念図。アーサーの収穫逓増モデルの数値結果ではなく、採用の蓄積が次の採用を有利にする構図。')
    f.save(name)


def figure_18(name):
    """図18: 頻出する外乱には厚い防御がある一方、想定外の方向には防御が薄い構造。"""
    f=Figure(18,'何に対して強いのかを、必ず問う','頻出する外乱には厚い防御、想定していない方向には薄い防御',690)
    cx,cy=600,400
    rect(f,cx-130,cy-70,260,140,TEAL);f.text(cx,cy-10,'系',24,TEAL,anchor='middle',weight=700);f.text(cx,cy+22,'共通の前提に依存',16,MUTED,anchor='middle')
    # thick shields on left, right, bottom (frequent perturbations)
    f.parts.append(f'<rect x="{cx-160}" y="{cy-90}" width="22" height="180" rx="6" fill="#087f83"/>')
    f.parts.append(f'<rect x="{cx+138}" y="{cy-90}" width="22" height="180" rx="6" fill="#087f83"/>')
    f.parts.append(f'<rect x="{cx-160}" y="{cy+100}" width="320" height="22" rx="6" fill="#087f83"/>')
    # thin shield on top (unanticipated)
    f.parts.append(f'<rect x="{cx-160}" y="{cy-128}" width="320" height="5" rx="2" fill="#b95130"/>')
    for x,lab in [(cx-330,'頻出の障害'),(cx+330,'頻出の障害')]:
        f.line(x+(60 if x<cx else -60),cy,x+(150 if x<cx else -150),cy,color=INK,width=5,arrow=True);f.text(x,cy-18,lab,16,INK,anchor='middle')
    f.line(cx,cy+205,cx,cy+135,color=INK,width=5,arrow=True);f.text(cx,cy+228,'頻出の障害',16,INK,anchor='middle')
    f.line(cx,cy-205,cx,cy-140,color=ORANGE,width=2,arrow=True);f.text(cx,cy-214,'想定外の外乱（稀だが共通の前提を崩す）',16,ORANGE,anchor='middle',weight=700)
    f.text(cx-330,cy+200,'厚い防御：自動復旧・冗長化・再試行',15,TEAL);f.text(cx-330,cy+222,'薄い防御：前提そのものを疑う手段',15,ORANGE)
    f.footer('概念図。HOT の確率モデルの計算ではなく、資源を配分した結果として生じる「頑健だが脆い」構図。')
    f.save(name)


def figure_19(name):
    """図19: 平衡点への戻りやすさ（器の深さ）と、別の状態領域へ移りにくさ（器の広さ）を分けて示す概念図。"""
    f=Figure(19,'戻りやすさと、移りにくさは別の量である','平衡へ戻る速さ（安定性）と、別の領域へ移る前に吸収できる外乱の大きさ（レジリエンス）',640)
    import math as _m
    def basin(px,width,depth):
        pts=[(px+x,280+depth*_m.exp(-((x-width/2)/(width*0.3))**2)) for x in range(0,width+1,4)]
        f.path(polyline(pts),color=INK,width=3)
        return px+width/2,280+depth
    lx,ly=basin(90,300,200);f.circ(lx,ly-12,12,TEAL)
    rx,ry=basin(560,540,110);f.circ(rx,ry-12,12,ORANGE)
    f.line(lx-90,ly-12,lx-26,ly-12,color=MUTED,width=2,arrow=True);f.text(lx-58,ly-26,'外乱',14,MUTED,anchor='middle')
    f.line(rx-190,ry-12,rx-26,ry-12,color=MUTED,width=2,arrow=True);f.text(rx-108,ry-26,'外乱',14,MUTED,anchor='middle')
    f.path(f'M{lx+12},{ly-20} Q{lx+150},{ly-60} {lx+180},{262}',color=ORANGE,width=2,dash=True,arrow=True)
    f.text(lx+190,252,'小さな外乱でも別の領域へ出る',15,ORANGE)
    f.text(lx,560,'戻りが速いが、器は狭い',19,TEAL,anchor='middle',weight=700);f.text(lx,586,'安定性は高く、レジリエンスは低い',15,MUTED,anchor='middle')
    f.text(rx,560,'戻りは遅いが、器は広い',19,ORANGE,anchor='middle',weight=700);f.text(rx,586,'安定性は低く、レジリエンスは高い',15,MUTED,anchor='middle')
    f.footer('概念図。ホリングの定義の説明であり、特定の系の測定ではない。器の形は系ごとに違う。')
    f.save(name)


def figure_20(name):
    """図20: 速い・中間・遅い三つの周期と、階層間を結ぶ変化・継承の経路。"""
    f=Figure(20,'速い変化と遅い構造は、互いに支え合う','速い・中間・遅い三つの周期と、下からの反乱と上からの記憶という階層間の経路',700)
    import math as _m
    levels=[(600,300,70,'速い・小さい','チームの運営'),(600,420,110,'中間','組織の制度'),(600,560,150,'遅い・大きい','技術・信頼・記録の蓄積')]
    for cx,cy,r,lab,sub in levels:
        pts=[(cx+r*_m.cos(a)*1.6,cy+r*0.42*_m.sin(a)) for a in [i*2*_m.pi/60 for i in range(61)]]
        f.path(polyline(pts),color=TEAL if r<150 else ORANGE,width=3)
        f.text(cx+r*1.6+16,cy+6,f'{lab}：{sub}',16,INK)
    for (x,y,txt) in [(600,300,'成長'),(600+70*1.6,300,'保全'),(600,300+70*0.42,'解放'),(600-70*1.6,300,'再編成')]:pass
    f.text(600,246,'各周期は、成長 → 保全 → 解放 → 再編成をたどる',15,MUTED,anchor='middle')
    f.line(430,330,430,395,color=ORANGE,width=2.5,arrow=True);f.text(418,370,'反乱：速い層の崩壊が遅い層へ波及',15,ORANGE,anchor='end')
    f.line(770,520,770,455,color=TEAL,width=2.5,arrow=True);f.text(782,490,'記憶：遅い層の蓄積が速い層の再編成を支える',15,TEAL)
    f.footer('概念図。適応サイクルは分析の枠組みであり、すべての系が同じ順序で回る法則ではない。')
    f.save(name)


def figure_21(name):
    """図21: 現在の山を高く登る経路と、別の山を探す経路に、同じ資源を配分する図。"""
    f=Figure(21,'今の山を登る資源と、別の山を探す資源','既知の方法を磨く活用と、新しい可能性を探す探索に、同じ資源を配分する',640)
    import math as _m
    X=lambda x:120+x*980
    Y=lambda v:540-v*280
    known=lambda x:0.62*_m.exp(-((x-0.28)/0.16)**2)
    other=lambda x:0.95*_m.exp(-((x-0.78)/0.12)**2)
    xs=[i/200 for i in range(201)]
    f.line(100,540,1120,540,color=INK,width=1.5,arrow=True);f.text(1120,566,'方法の空間',17,MUTED,anchor='end')
    f.line(120,540,120,230,color=INK,width=1.5,arrow=True);f.text(108,236,'成果',17,MUTED,anchor='end')
    f.path(polyline([(X(x),Y(known(x))) for x in xs]),color=TEAL,width=3)
    f.path(polyline([(X(x),Y(other(x))) for x in xs]),color=ORANGE,width=3,dash=True)
    f.circ(X(0.22),Y(known(0.22)),9,TEAL)
    for a,b in [(0.22,0.245),(0.245,0.265),(0.265,0.28)]:f.line(X(a),Y(known(a)),X(b),Y(known(b)),color=TEAL,width=2.5,arrow=True)
    f.text(X(0.28),Y(known(0.28))-18,'活用：今の山を少しずつ高く登る',17,TEAL,anchor='middle',weight=700)
    f.path(f'M{X(0.24):.0f},{Y(known(0.22))-30:.0f} Q{X(0.5):.0f},{Y(0.15):.0f} {X(0.70):.0f},{Y(other(0.70))+40:.0f}',color=ORANGE,width=2.5,dash=True,arrow=True)
    f.text(X(0.5),Y(0.08)-6,'探索：成果が出るか分からない別の山へ',17,ORANGE,anchor='middle',weight=700)
    f.text(X(0.78),Y(other(0.78))-16,'見つかれば高いが、見つかるとは限らない',15,MUTED,anchor='middle')
    rect(f,160,232,420,70,MUTED);f.text(370,260,'同じ資源 R を、活用 (1−ε) と探索 ε に分ける',16,INK,anchor='middle');f.text(370,286,'短期の指標はほぼ活用の成果だけを映す',15,MUTED,anchor='middle')
    f.footer('概念図。マーチの相互学習モデルの結果ではなく、配分のトレードオフを示す構図。')
    f.save(name)


def figure_22(name):
    """図22: 共有資源を囲む複数の利用主体と、利用・維持負担・監視・ルール改訂の経路。"""
    f=Figure(22,'共有のものは、自由だけでは保たれない','共有資源を囲む複数の利用主体と、利用・維持負担・監視・ルール改訂の経路',720)
    import math as _m
    cx,cy=600,400
    f.parts.append(f'<circle cx="{cx}" cy="{cy}" r="95" fill="#ffffff" stroke="#087f83" stroke-width="3"/>')
    f.text(cx,cy-6,'共通基盤',22,TEAL,anchor='middle',weight=700);f.text(cx,cy+20,'コード・保守者の時間・CI枠・問い合わせの余力',13,MUTED,anchor='middle')
    teams=[(cx+300*_m.cos(a),cy+150*_m.sin(a)) for a in [-_m.pi/2,-_m.pi/2+2*_m.pi/5,-_m.pi/2+4*_m.pi/5,-_m.pi/2+6*_m.pi/5,-_m.pi/2+8*_m.pi/5]]
    for i,(x,y) in enumerate(teams):
        rect(f,x-55,y-24,110,48,ORANGE);f.text(x,y+6,f'チーム{"ABCDE"[i]}',17,ORANGE,anchor='middle',weight=700)
        ang=_m.atan2(cy-y,cx-x);ex,ey=x+70*_m.cos(ang),y+50*_m.sin(ang);tx,ty=cx-115*_m.cos(ang),cy-115*_m.sin(ang)
        f.line(ex,ey,tx,ty,color=MUTED,width=1.5,arrow=True)
    f.text(cx-60,cy-120,'利用する',15,MUTED,anchor='middle')
    rect(f,70,600,230,70,TEAL);f.text(185,628,'維持の負担を分ける',16,TEAL,anchor='middle',weight=700);f.text(185,652,'保守時間・枠の割当',14,MUTED,anchor='middle')
    rect(f,330,600,230,70,TEAL);f.text(445,628,'利用を監視する',16,TEAL,anchor='middle',weight=700);f.text(445,652,'利用者自身が確かめる',14,MUTED,anchor='middle')
    rect(f,640,600,230,70,TEAL);f.text(755,628,'紛争を解決する',16,TEAL,anchor='middle',weight=700);f.text(755,652,'低い費用で、その場で',14,MUTED,anchor='middle')
    rect(f,900,600,230,70,TEAL);f.text(1015,628,'ルールを改訂する',16,TEAL,anchor='middle',weight=700);f.text(1015,652,'利用者が決定に参加',14,MUTED,anchor='middle')
    f.text(600,586,'中央管理でも放任でもない、複数の意思決定の拠点',15,INK,anchor='middle')
    f.footer('概念図。オストロムの設計原理の一部を、共通基盤に当てはめた本連載の類比。')
    f.save(name)


def figure_23(name):
    """図23: 独立した要素の協働から、全体として特徴を継承する単位への変化。"""
    f=Figure(23,'一緒に動くことと、一つとして続くことは違う','独立に複製する要素の協働から、全体として再生産され特徴を次へ伝える単位へ',640)
    f.panel(70,200,480,350);f.text(90,232,'集まる：各要素が独立に複製する',20,INK,weight=700)
    f.panel(650,200,480,350);f.text(670,232,'一つになる：全体として複製し、特徴を引き継ぐ',20,INK,weight=700)
    pts=[(170,320),(260,300),(350,330),(220,400),(320,410)]
    for a,b in [(0,1),(1,2),(0,3),(1,3),(2,4),(3,4),(1,4)]:f.line(*pts[a],*pts[b],color='#aec1c4',width=1.5)
    for x,y in pts:f.circ(x,y,11,TEAL)
    for x,y in pts:
        f.line(x,y+16,x,y+44,color=MUTED,width=1.2,arrow=True);ring(f,x,y+58,7,TEAL)
    f.text(310,500,'次の世代：各要素がばらばらに',15,MUTED,anchor='middle')
    rect(f,700,280,180,120,ORANGE)
    for x,y in [(740,320),(800,310),(840,350),(760,370)]:f.circ(x,y,9,ORANGE)
    f.line(790,410,790,450,color=ORANGE,width=2.5,arrow=True);f.text(812,436,'全体として複製',15,ORANGE)
    rect(f,700,460,180,70,ORANGE,dash=True)
    for x,y in [(740,490),(800,482),(840,510),(760,520)]:ring(f,x,y,8,ORANGE)
    rect(f,920,280,190,120,MUTED);f.text(1015,318,'情報の保存と伝達',15,INK,anchor='middle',weight=700);f.text(1015,344,'全体の特徴が次へ渡る',13,MUTED,anchor='middle');f.text(1015,366,'内部の対立が抑えられる',13,MUTED,anchor='middle')
    f.line(880,340,920,340,color=MUTED,width=1.5,arrow=True)
    f.text(890,538,'結合だけでなく、全体を維持し引き継ぐ仕組みが関わる',14,MUTED,anchor='middle')
    f.footer('概念図。生物の進化の大転換を図式化したもので、組織やAgentの増設と同一視しない。')
    f.save(name)


CHAPTER_FIGURES={13:lambda name:figure_conversation(name,final=False),14:figure_14,15:figure_15,16:figure_16,17:figure_17,18:figure_18,19:figure_19,20:figure_20,21:figure_21,22:figure_22,23:figure_23,24:lambda name:figure_conversation(name,final=True)}
COVERS={2:figure_cover_2}
EXTRA_FIGURES={'3-2':figure_3_2,'6-2':figure_6_2,'4-2':figure_4_2,'2-2':figure_2_2,'1-2':figure_1_2,'12-2':figure_12_2}


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
    for k in json.loads((ROOT/'series.json').read_text())['cours']:
        if k['number']>=2:COVERS[k['number']](Path(k['cover']).name)

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
    for c in chapters:
        if c['number'] in CHAPTER_FIGURES:CHAPTER_FIGURES[c['number']](Path(c['figure']).name)
    extra=0
    for c in chapters:
        for fig in c.get('figures',[]):
            EXTRA_FIGURES[fig['label']](Path(fig['path']).name);extra+=1
    covers=len(json.loads((ROOT/'series.json').read_text())['cours'])
    print(f'Generated {len(chapters)+covers+extra} SVG files in {OUT}')

if __name__=='__main__':main()
