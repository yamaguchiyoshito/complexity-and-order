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


ANIMATIONS = {
    22: dict(draw=draw_22, title='共有のものは、自由だけでは保たれない', subtitle='五つのチームからのリクエストと、利用・維持負担・監視・ルール改訂の経路', height=720, slug='22-commons'),
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
