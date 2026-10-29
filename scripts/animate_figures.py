#!/usr/bin/env python3
"""Render looping GIF versions of selected figures.

Each frame is a deterministic static SVG drawn with the same tools as
draw_figures.py (no SMIL, no scripts). Frames are rasterised with
rsvg-convert and assembled with ffmpeg. Text never moves between frames.
"""
from __future__ import annotations
import argparse
import hashlib
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_figures import Figure, rect, ring, polyline, TEAL, ORANGE, INK, MUTED  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PERIOD = 6.0


def pulse(t: float, start: float, width: float) -> float:
    """Half-sine pulse of the given width starting at `start`, periodic over PERIOD. 0 at the seams."""
    s = (t - start) % PERIOD
    return math.sin(math.pi * s / width) if 0 <= s < width else 0.0


def dot(f: Figure, x: float, y: float, color: str, r: float = 5.5) -> None:
    f.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')


def glow_circle(f: Figure, x: float, y: float, r: float, color: str, opacity: float) -> None:
    if opacity > 0.005:
        f.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity="{opacity:.3f}"/>')


def draw_22(f: Figure, t: float) -> None:
    """図22（コモンズ）の時刻 t における1フレーム。静止図と同じ配置に、トラフィックと反応を足す。"""
    cx, cy = 600, 400
    f.parts.append(f'<circle cx="{cx}" cy="{cy}" r="95" fill="#ffffff" stroke="#087f83" stroke-width="3"/>')
    teams = [(cx + 300 * math.cos(a), cy + 150 * math.sin(a)) for a in [-math.pi / 2 + k * 2 * math.pi / 5 for k in range(5)]]
    paths = []
    for i, (x, y) in enumerate(teams):
        ang = math.atan2(cy - y, cx - x)
        ex, ey = x + 70 * math.cos(ang), y + 50 * math.sin(ang)
        tx, ty = cx - 115 * math.cos(ang), cy - 115 * math.sin(ang)
        f.line(ex, ey, tx, ty, color=MUTED, width=1.5, arrow=True)
        paths.append(((ex, ey), (tx, ty)))
    # arrivals light the platform (0.4 s each); phases 0, 1.2, ... s, travel 1.5 s
    travel, phases = 1.5, [1.2 * i for i in range(5)]
    glow = max(pulse(t, p + travel, 0.4) for p in phases)
    glow_circle(f, cx, cy, 95, TEAL, 0.35 * glow)
    f.text(cx, cy - 6, '共通基盤', 22, TEAL, anchor='middle', weight=700)
    f.text(cx, cy + 20, 'コード・保守者の時間・CI枠・問い合わせの余力', 13, MUTED, anchor='middle')
    for i, (x, y) in enumerate(teams):
        rect(f, x - 55, y - 24, 110, 48, ORANGE)
        f.text(x, y + 6, f'チーム{"ABCDE"[i]}', 17, ORANGE, anchor='middle', weight=700)
    f.text(cx - 60, cy - 120, '利用する', 15, MUTED, anchor='middle')
    # bottom boxes bounce once per period (0.3 s), text stays put
    labels = [(70, '維持の負担を分ける', '保守時間・枠の割当'), (330, '利用を監視する', '利用者自身が確かめる'),
              (640, '紛争を解決する', '低い費用で、その場で'), (900, 'ルールを改訂する', '利用者が決定に参加')]
    for k, (x, title, sub) in enumerate(labels):
        dy = -3 * pulse(t, 0.6 + 1.5 * k, 0.3)
        rect(f, x, 600 + dy, 230, 70, TEAL)
    for x, title, sub in labels:
        f.text(x + 115, 628, title, 16, TEAL, anchor='middle', weight=700)
        f.text(x + 115, 652, sub, 14, MUTED, anchor='middle')
    f.text(600, 586, '中央管理でも放任でもない、複数の意思決定の拠点', 15, INK, anchor='middle')
    # traffic: one request per team per period, drawn last so it rides on top of the arrows
    for i, ((ex, ey), (tx, ty)) in enumerate(paths):
        u = ((t - phases[i]) % PERIOD) / travel
        if u < 1:
            dot(f, ex + (tx - ex) * u, ey + (ty - ey) * u, ORANGE)
    f.footer('動く版。オストロムの設計原理の一部を、共通基盤に当てはめた本連載の類比。')


def glow_rect(f: Figure, x: float, y: float, w: float, h: float, color: str, opacity: float, rx: int = 12) -> None:
    if opacity > 0.005:
        f.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{color}" fill-opacity="{opacity:.3f}"/>')


def pulse_every(t: float, start: float, width: float, every: float) -> float:
    """pulse() repeated with period `every` inside the 6-second loop (every must divide PERIOD)."""
    return max(pulse(t, start + k * every, width) for k in range(int(round(PERIOD / every))))


def draw_18(f: Figure, t: float) -> None:
    """図18（頑健だが脆い）。頻出の障害は2秒周期で厚い防御に当たって光り、想定外は6秒に一度だけ薄い線を抜けて系を暗転させる。"""
    cx, cy = 600, 400
    rect(f, cx - 130, cy - 70, 260, 140, TEAL)
    # the rare perturbation reaches the box at t=4.0 and dims it for 0.6 s
    glow_rect(f, cx - 130, cy - 70, 260, 140, INK, 0.25 * pulse(t, 4.0, 0.6), rx=14)
    f.text(cx, cy - 10, '系', 24, TEAL, anchor='middle', weight=700); f.text(cx, cy + 22, '共通の前提に依存', 16, MUTED, anchor='middle')
    shields = {'left': (cx - 160, cy - 90, 22, 180), 'right': (cx + 138, cy - 90, 22, 180), 'bottom': (cx - 160, cy + 100, 320, 22)}
    for sx, sy, sw, sh in shields.values():
        f.parts.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="6" fill="#087f83"/>')
    f.parts.append(f'<rect x="{cx-160}" y="{cy-128}" width="320" height="5" rx="2" fill="#b95130"/>')
    for x, lab in [(cx - 330, '頻出の障害'), (cx + 330, '頻出の障害')]:
        f.line(x + (60 if x < cx else -60), cy, x + (150 if x < cx else -150), cy, color=INK, width=5, arrow=True); f.text(x, cy - 18, lab, 16, INK, anchor='middle')
    f.line(cx, cy + 205, cx, cy + 135, color=INK, width=5, arrow=True); f.text(cx, cy + 228, '頻出の障害', 16, INK, anchor='middle')
    f.line(cx, cy - 205, cx, cy - 140, color=ORANGE, width=2, arrow=True); f.text(cx, cy - 214, '想定外の外乱（稀だが共通の前提を崩す）', 16, ORANGE, anchor='middle', weight=700)
    f.text(cx - 330, cy + 200, '厚い防御：自動復旧・冗長化・再試行', 15, TEAL); f.text(cx - 330, cy + 222, '薄い防御：前提そのものを疑う手段', 15, ORANGE)
    # frequent perturbations: every 2 s, phases 0, 2/3, 4/3; travel 1.2 s; the shield brightens on impact
    travel = 1.2
    routes = [('left', (cx - 270, cy), (cx - 164, cy), 0.0), ('right', (cx + 270, cy), (cx + 164, cy), 2 / 3), ('bottom', (cx, cy + 205), (cx, cy + 126), 4 / 3)]
    for key, (x0, y0), (x1, y1), phase in routes:
        sx, sy, sw, sh = shields[key]
        glow_rect(f, sx, sy, sw, sh, '#ffffff', 0.6 * pulse_every(t, phase + travel, 0.4, 2.0), rx=6)
        u = ((t - phase) % 2.0) / travel
        if u < 1: dot(f, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, INK)
    # the rare one: departs at 3.0, passes the thin line and reaches the box at 4.0
    u = ((t - 3.0) % PERIOD) / 1.0
    if u < 1: dot(f, cx, (cy - 205) + ((cy - 70) - (cy - 205)) * u, ORANGE)
    f.footer('動く版。頻出の障害は厚い防御で吸収され、想定外の外乱だけが薄い防御を抜ける。HOT の確率モデルの計算ではない。')


def draw_15(f: Figure, t: float) -> None:
    """図15（情報ボトルネック）。項目が順に T へ流れ、残る項目だけが右の箱へ届いて箱が光り、他は T の手前で消える。"""
    items = ['発生時刻', '直前の変更', '失敗した呼び出し', '利用者の数', '時間帯', '機能の名前', '端末の種類', '再試行の回数']
    rect(f, 80, 215, 220, 370, MUTED); f.text(190, 245, '入力 X（ログ）', 20, MUTED, anchor='middle', weight=700)
    ys = [275 + i * 38 for i in range(8)]
    for y, it in zip(ys, items): f.text(190, y + 6, it, 17, INK, anchor='middle')
    travel, step, hop = 1.2, 0.3, 0.4
    dots = []
    for cy, target, keep, color, offset in [(300, '目的 Y₁：原因の特定', [0, 1, 2], TEAL, 0.0), (500, '目的 Y₂：影響の見積り', [3, 4, 5], ORANGE, 3.0)]:
        f.parts.append(f'<path d="M520,{cy-70} L560,{cy-18} L560,{cy+18} L520,{cy+70} Z" fill="#ffffff" stroke="{color}" stroke-width="2.5"/>')
        f.text(540, cy + 6, 'T', 22, color, anchor='middle', weight=700)
        for i in keep: f.line(300, ys[i], 520, cy - 40 + 40 * keep.index(i), color=color, width=2)
        rect(f, 640, cy - 60, 230, 120, color)
        arrivals = [offset + step * i + travel + hop for i in keep]
        glow_rect(f, 640, cy - 60, 230, 120, color, 0.3 * max(pulse(t, a, 0.4) for a in arrivals))
        f.text(755, cy - 28, '残る区別', 18, color, anchor='middle', weight=700)
        for n, i in enumerate(keep): f.text(755, cy + n * 24, items[i], 16, INK, anchor='middle')
        f.line(870, cy, 950, cy, color=color, width=2, arrow=True); f.text(960, cy + 6, target, 18, color, weight=700)
        for i in range(8):
            s = (t - offset - step * i) % PERIOD
            if i in keep:
                end = (520, cy - 40 + 40 * keep.index(i))
                if s < travel:
                    u = s / travel; dots.append((300 + (end[0] - 300) * u, ys[i] + (end[1] - ys[i]) * u, color))
                elif s < travel + hop:
                    u = (s - travel) / hop; dots.append((560 + (640 - 560) * u, cy, color))
            else:
                if s < travel:
                    u = s / travel; x = 300 + (505 - 300) * u; y = ys[i] + (cy - ys[i]) * u
                    dots.append((x, y, MUTED))  # fades at the mouth of the bottleneck
    f.text(540, 405, 'ボトルネック T', 17, MUTED, anchor='middle')
    for x, y, color in dots: dot(f, x, y, color)
    f.footer('動く版。残る項目だけが T を通って右へ届く。項目は説明用の例で、何が残るかは p(x, y) と β によって決まる。')


def draw_conversation(f: Figure, t: float, final: bool) -> None:
    """図13／図24（会話）。説明が A→B、再構成が B→A と往復し、到着した側の概念図が跳ね、最後に両方の枠が光る。"""
    rect(f, 540, 212, 120, 66, MUTED); f.text(600, 252, '仕様書', 22, MUTED, anchor='middle', weight=700)
    f.line(540, 245, 410, 300, color=MUTED, width=1.5, arrow=True); f.line(660, 245, 790, 300, color=MUTED, width=1.5, arrow=True)
    f.text(470, 262, '読む', 16, MUTED, anchor='middle'); f.text(730, 262, '読む', 16, MUTED, anchor='middle')
    both = 0.2 * pulse(t, 5.4, 0.6)
    rect(f, 110, 300, 300, 230, TEAL); glow_rect(f, 110, 300, 300, 230, TEAL, 0.3 * pulse(t, 5.4, 0.4) + both)
    rect(f, 790, 300, 300, 230, ORANGE); glow_rect(f, 790, 300, 300, 230, ORANGE, 0.3 * pulse(t, 2.4, 0.4) + both)
    f.text(260, 332, 'Aの概念図', 20, TEAL, anchor='middle', weight=700); f.text(940, 332, 'Bの概念図', 20, ORANGE, anchor='middle', weight=700)
    da = -3 * pulse(t, 5.4, 0.3); db = -3 * pulse(t, 2.4, 0.3)
    a = [(200, 400 + da), (320, 400 + da), (260, 490 + da)]
    for i in range(3):
        for j in range(i + 1, 3): f.line(*a[i], *a[j], color=TEAL, width=2)
    for x, y in a: f.circ(x, y, 11, TEAL)
    b = [(840, 400 + db), (905, 400 + db), (970, 400 + db), (1035, 400 + db), (940, 490 + db)]
    for i in range(3): f.line(*b[i], *b[i + 1], color=ORANGE, width=2)
    f.line(*b[1], *b[4], color=ORANGE, width=2)
    for x, y in b: f.circ(x, y, 11, ORANGE)
    f.line(420, 385, 780, 385, color=INK, width=2, arrow=True); f.text(600, 374, '説明する（どうやるか／なぜそうなるか）', 18, INK, anchor='middle', weight=700)
    f.line(780, 455, 420, 455, color=INK, width=2, arrow=True); f.text(600, 478, '別の条件で再構成してみせる', 18, INK, anchor='middle', weight=700)
    if not final:
        f.text(600, 560, '同じ語の下に、別の構造があったことが見つかる', 20, ORANGE, anchor='middle', weight=700)
        f.footer('動く版。説明が A から B へ渡り、再構成が B から A へ戻る。パスクの会話の形式化を再現したものではない。')
    else:
        f.text(600, 560, '二つの図は一致しない。違いを確かめ、修正し、共同で動く往復が続く', 20, ORANGE, anchor='middle', weight=700)
        f.footer('動く版。第13回と同じ往復。到達点は一致ではなく、更新し合える関係である。')
    u = (t % PERIOD) / 2.4
    if u < 1: dot(f, 420 + 360 * u, 385, TEAL)
    u = ((t - 3.0) % PERIOD) / 2.4
    if u < 1: dot(f, 780 - 360 * u, 455, ORANGE)


ANIMATIONS = {
    22: dict(draw=draw_22, title='共有のものは、自由だけでは保たれない', subtitle='五つのチームからのリクエストと、利用・維持負担・監視・ルール改訂の経路', height=720, slug='22-commons'),
    18: dict(draw=draw_18, title='何に対して強いのかを、必ず問う', subtitle='頻出する外乱には厚い防御、想定していない方向には薄い防御', height=690, slug='18-robust-yet-fragile'),
    15: dict(draw=draw_15, title='何を残すかは、何を判断したいかで決まる', subtitle='同じ入力から、目的に応じて別々の特徴が残される二つの情報ボトルネック', height=640, slug='15-information-bottleneck'),
    13: dict(draw=lambda f, t: draw_conversation(f, t, False), title='届いたことと、分かったことは違う', subtitle='同じ文書から別の概念図ができ、説明と再構成の往復で違いが見つかる', height=640, slug='13-conversation-theory'),
    24: dict(draw=lambda f, t: draw_conversation(f, t, True), title='同じにはならない。それでも更新し合える。', subtitle='第13回と同じ二者。概念図は一致しないまま、確かめ合う往復が続く', height=640, slug='24-maintaining-by-changing'),
}


def frame_svg(spec: dict, number: int, t: float) -> str:
    f = Figure(number, spec['title'], spec['subtitle'], spec['height'])
    spec['draw'](f, t)
    return '\n'.join(f.parts + ['</g>', '</svg>']) + '\n'


def text_signature(svg: str) -> str:
    return hashlib.sha256('\n'.join(re.findall(r'<text[^>]*>.*?</text>', svg)).encode()).hexdigest()


def lzw_encode(indices: bytes, min_code_size: int = 8) -> bytes:
    """GIF-flavoured LZW (variable code width, LSB-first bit packing)."""
    clear, eoi = 1 << min_code_size, (1 << min_code_size) + 1
    out = bytearray(); acc = 0; nbits = 0
    def emit(code: int, width: int) -> None:
        nonlocal acc, nbits
        acc |= code << nbits; nbits += width
        while nbits >= 8:
            out.append(acc & 0xFF); acc >>= 8; nbits -= 8
    table = {bytes([i]): i for i in range(clear)}; next_code = eoi + 1; width = min_code_size + 1
    emit(clear, width)
    prefix = b''
    for b in indices:
        cur = prefix + bytes([b])
        if cur in table:
            prefix = cur; continue
        emit(table[prefix], width)
        if next_code < 4096:
            table[cur] = next_code; next_code += 1
            if next_code - 1 == (1 << width) and width < 12: width += 1
        else:
            emit(clear, width); table = {bytes([i]): i for i in range(clear)}; next_code = eoi + 1; width = min_code_size + 1
        prefix = bytes([b])
    if prefix: emit(table[prefix], width)
    emit(eoi, width)
    if nbits: out.append(acc & 0xFF)
    blocks = bytearray()
    for i in range(0, len(out), 255):
        chunk = out[i:i + 255]; blocks.append(len(chunk)); blocks += chunk
    blocks.append(0)
    return bytes(blocks)


def write_gif(path: Path, pal8: bytes, palette_rgb: bytes, w: int, h: int, frames: int, delay_cs: int) -> None:
    """Write a looping GIF where every frame after the first encodes only its changed rectangle."""
    size = w * h
    if len(pal8) != size * frames: raise RuntimeError('pal8 のサイズがフレーム数と一致しない。')
    used = set(pal8)
    transparent = next((i for i in range(255, -1, -1) if i not in used), None)
    if transparent is None: raise RuntimeError('透明用のパレット番号が空いていない。色数を減らすこと。')
    out = bytearray(b'GIF89a')
    out += w.to_bytes(2, 'little') + h.to_bytes(2, 'little') + bytes([0xF7, 0, 0])  # global table, 256 entries
    out += palette_rgb[:768].ljust(768, b'\x00')
    out += b'\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00'  # loop forever
    prev = None
    for k in range(frames):
        cur = pal8[k * size:(k + 1) * size]
        if prev is None:
            x0, y0, x1, y1 = 0, 0, w, h; sub = cur; flags = 0x04  # disposal 1 (leave), no transparency
        else:
            rows = [y for y in range(h) if cur[y * w:(y + 1) * w] != prev[y * w:(y + 1) * w]]
            if not rows:
                x0, y0, x1, y1 = 0, 0, 1, 1; sub = bytes([transparent])
            else:
                y0, y1 = rows[0], rows[-1] + 1; x0, x1 = w, 0
                for y in rows:
                    a = cur[y * w:(y + 1) * w]; b = prev[y * w:(y + 1) * w]
                    xs = [x for x in range(w) if a[x] != b[x]]
                    x0 = min(x0, xs[0]); x1 = max(x1, xs[-1] + 1)
                sub = bytearray()
                for y in range(y0, y1):
                    a = cur[y * w + x0:y * w + x1]; b = prev[y * w + x0:y * w + x1]
                    sub += bytes(a[i] if a[i] != b[i] else transparent for i in range(len(a)))
            flags = 0x05  # disposal 1, transparency on
        out += b'\x21\xF9\x04' + bytes([flags]) + delay_cs.to_bytes(2, 'little') + bytes([transparent, 0])
        out += b'\x2C' + x0.to_bytes(2, 'little') + y0.to_bytes(2, 'little') + (x1 - x0).to_bytes(2, 'little') + (y1 - y0).to_bytes(2, 'little') + b'\x00'
        out += bytes([8]) + lzw_encode(bytes(sub))
        prev = cur
    out += b'\x3B'
    path.write_bytes(bytes(out))


def render(number: int, fps: int, width: int, out_dir: Path, keep_frames: Path | None, colors: int = 48, dither: str = 'none') -> Path:
    spec = ANIMATIONS[number]
    frames = int(round(PERIOD * fps))
    svgs = [frame_svg(spec, number, k / fps) for k in range(frames)]
    seam = frame_svg(spec, number, PERIOD)
    if seam != svgs[0]:
        raise RuntimeError('フレーム0と周期末のフレームが一致しない。ループに継ぎ目ができる。')
    if len({text_signature(s) for s in svgs}) != 1:
        raise RuntimeError('フレーム間で文字要素が変化している。文字は固定でなければならない。')
    for tool in ('rsvg-convert', 'ffmpeg'):
        if not shutil.which(tool):
            raise RuntimeError(f'{tool} が必要である。')
    out_dir.mkdir(parents=True, exist_ok=True)
    work = keep_frames or Path(tempfile.mkdtemp(prefix='animate-'))
    work.mkdir(parents=True, exist_ok=True)
    for k, svg in enumerate(svgs):
        svg_path = work / f'frame_{k:02d}.svg'
        svg_path.write_text(svg, encoding='utf-8')
        subprocess.run(['rsvg-convert', '-w', str(width), str(svg_path), '-o', str(work / f'frame_{k:02d}.png')], check=True)
    palette = work / 'palette.png'
    seq = str(work / 'frame_%02d.png')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', seq,
                    '-vf', f'palettegen=max_colors={colors}:stats_mode=diff', str(palette)], check=True)
    # ffmpeg quantises; the GIF itself is written here so that only changed rectangles are encoded.
    raw = work / 'frames.pal8'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', seq, '-i', str(palette),
                    '-lavfi', f'paletteuse=dither={dither}', '-f', 'rawvideo', '-pix_fmt', 'pal8', str(raw)], check=True)
    pal_raw = work / 'palette.rgb'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(palette), '-f', 'rawvideo', '-pix_fmt', 'rgb24', str(pal_raw)], check=True)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(work / 'frame_00.png')], capture_output=True, text=True, check=True).stdout.strip()
    w, h = (int(v) for v in probe.split(','))
    gif = out_dir / f"{spec['slug']}.gif"
    data = raw.read_bytes(); stride = w * h + 1024  # rawvideo pal8 appends a 1024-byte palette to every frame
    pixels = b''.join(data[k * stride:k * stride + w * h] for k in range(frames))
    write_gif(gif, pixels, pal_raw.read_bytes(), w, h, frames, round(100 / fps))
    if keep_frames is None:
        shutil.rmtree(work, ignore_errors=True)
    return gif


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', type=int, required=True, choices=sorted(ANIMATIONS))
    parser.add_argument('--fps', type=int, default=10)
    parser.add_argument('--width', type=int, default=960)
    parser.add_argument('--out', type=Path, default=ROOT / 'assets' / 'animations')
    parser.add_argument('--keep-frames', type=Path, help='フレームの SVG/PNG を残すディレクトリ（確認用）')
    parser.add_argument('--colors', type=int, default=48)
    parser.add_argument('--dither', default='none', choices=['none', 'bayer', 'floyd_steinberg'])
    args = parser.parse_args()
    try:
        gif = render(args.figure, args.fps, args.width, args.out, args.keep_frames, args.colors, args.dither)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f'{gif} ({gif.stat().st_size // 1024} KB, {int(PERIOD * args.fps)} frames, {args.fps} fps)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
