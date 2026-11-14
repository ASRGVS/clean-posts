from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys, os

FD = '/usr/share/fonts/truetype/google-fonts/'
def F(w, s): return ImageFont.truetype(FD + {'b': 'Poppins-Bold.ttf', 'm': 'Poppins-Medium.ttf', 'r': 'Poppins-Regular.ttf'}[w], s)

BLUE = (15, 98, 172); LBLUE = (0, 175, 239); ORANGE = (245, 134, 52)
NAVY = (12, 52, 96); GRAY = (90, 104, 120); GREEN = (31, 170, 89); WHITE = (255, 255, 255)
LOGO = '/home/claude/clean-posts/marca/logo-cor.png'
PHONE = '(33) 98761-0434'


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


def pin(d, x, y, s, col):
    r = s // 2
    d.ellipse([x, y, x + s, y + s], fill=col)
    d.polygon([(x + s * 0.12, y + r * 1.3), (x + s * 0.88, y + r * 1.3), (x + r, y + s * 1.45)], fill=col)
    d.ellipse([x + s * 0.32, y + s * 0.32, x + s * 0.68, y + s * 0.68], fill=WHITE)


def render(photo, out, blocks, story=False, shift=0, fade_extra=0):
    W, H = (1080, 1920) if story else (1080, 1350)
    base = Image.open(photo).convert('RGB').resize((W, H))
    if shift:
        nb = Image.new('RGB', (W, H), WHITE); nb.paste(base, (0, -shift)); base = nb
    img = base.convert('RGBA')
    M = 64; CW = W - 2 * M
    sc = 1.12 if story else 1.0
    meas = ImageDraw.Draw(img)

    # ---- measure blocks
    def h_of(b):
        k = b[0]
        if k == 'eyebrow': return int(44 * sc)
        if k == 'title':
            f = F('b', int(b[2] if len(b) > 2 else 54 * sc)); n = len(wrap(meas, b[1], f, CW)); return int(n * f.size * 1.12)
        if k == 'sub':
            f = F('m', int(32 * sc)); return int(len(wrap(meas, b[1], f, CW)) * f.size * 1.35)
        if k == 'line':
            f = F('r', int(29 * sc)); return int(len(wrap(meas, b[1], f, CW)) * f.size * 1.4)
        if k == 'price': return int(96 * sc)
        if k == 'promo': return int(100 * sc)
        if k == 'grid': return int(150 * sc)
        if k == 'rows': return int(len(b[1]) * 74 * sc)
        if k == 'steps': return int(len(b[1]) * 70 * sc)
        if k == 'options': return int(2 * 88 * sc + 16)
        if k == 'badge': return int(58 * sc)
        if k == 'button': return int(96 * sc) + (int(40 * sc) if b[1] != 'story' else int(44 * sc))
        if k == 'space': return b[1]
        return 0
    GAP = int(22 * sc)
    total = sum(h_of(b) for b in blocks) + GAP * (len(blocks) - 1)
    y0 = H - int(56 * sc) - total

    # ---- fades: top (header) and bottom (content)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for yy in range(0, 230):
        od.line([(0, yy), (W, yy)], fill=(255, 255, 255, int(215 * (1 - yy / 230) ** 1.6)))
    import math
    top = y0 - int(70 * sc)
    grad = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gp = grad.load()
    c1 = (8, 70, 140); c2 = (0, 150, 225)
    for yy in range(max(top - 80, 0), H):
        for xx in range(0, W, 1):
            t = min(1, max(0, (xx / W) * 0.55 + ((yy - top) / (H - top)) * 0.45))
            gp[xx, yy] = (int(c2[0] + (c1[0] - c2[0]) * t), int(c2[1] + (c1[1] - c2[1]) * t), int(c2[2] + (c1[2] - c2[2]) * t), 255)
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    amp = int(34 * sc)
    pts = [(x, top + amp * math.sin(x / W * math.pi * 1.6 + 0.4)) for x in range(0, W + 1, 6)]
    md.polygon(pts + [(W, H), (0, H)], fill=255)
    # thin light-blue accent wave above
    acc = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ad = ImageDraw.Draw(acc)
    pts2 = [(x, top - int(20 * sc) + amp * math.sin(x / W * math.pi * 1.6 + 0.9)) for x in range(0, W + 1, 6)]
    ad.polygon(pts2 + [(W, H), (0, H)], fill=(0, 175, 239, 150))
    od.rectangle([0, 0, 0, 0], fill=(0, 0, 0, 0))
    img = Image.alpha_composite(img, ov); ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    img = Image.alpha_composite(img, acc)
    panel = Image.new('RGBA', (W, H), (0, 0, 0, 0)); panel.paste(grad, (0, 0), mask)
    # decorative circles
    deco = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(deco)
    dd.ellipse([W - 330, H - 330, W + 170, H + 170], fill=(255, 255, 255, 18))
    dd.ellipse([W - 210, top + 30, W + 90, top + 330], fill=(245, 134, 52, 38))
    dm = Image.composite(deco, Image.new('RGBA', (W, H), (0, 0, 0, 0)), mask)
    img = Image.alpha_composite(img, panel); img = Image.alpha_composite(img, dm)
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img)

    # ---- header
    ps = int(34 * sc); pin(d, M, int(58 * sc), ps, BLUE)
    d.text((M + ps + 14, int(58 * sc) + ps // 2 + 4), 'Governador Valadares', font=F('m', int(30 * sc)), fill=NAVY, anchor='lm')
    logo = Image.open(LOGO).convert('RGBA'); lw = int(250 * sc)
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(logo, (W - M - lw, int(34 * sc)))
    d = ImageDraw.Draw(img)

    def pill(x, y, text, font, bg, fg, padx=26, h=None):
        tw = d.textlength(text, font=font); h = h or int(font.size * 1.9)
        d.rounded_rectangle([x, y, x + tw + 2 * padx, y + h], radius=h // 2, fill=bg)
        d.text((x + padx + tw / 2, y + h / 2), text, font=font, fill=fg, anchor='mm')
        return tw + 2 * padx

    def strike(x, y, text, font, col, anchor='la'):
        d.text((x, y), text, font=font, fill=col, anchor=anchor)
        bb = d.textbbox((x, y), text, font=font, anchor=anchor)
        my = (bb[1] + bb[3]) / 2 + 2
        d.line([(bb[0] - 2, my), (bb[2] + 2, my)], fill=col, width=max(3, font.size // 10))

    y = y0
    for b in blocks:
        k = b[0]; h = h_of(b)
        if k == 'eyebrow':
            f = F('b', int(24 * sc)); x = M
            for i, t in enumerate(b[1].split('|')):
                x += pill(x, y, t.strip(), f, ORANGE if i == 0 else WHITE, WHITE if i == 0 else BLUE, padx=22, h=int(44 * sc)) + 12
        elif k == 'title':
            f = F('b', int(b[2] if len(b) > 2 else 54 * sc))
            for i, l in enumerate(wrap(d, b[1], f, CW)):
                d.text((M, y + i * f.size * 1.12), l, font=f, fill=WHITE)
        elif k == 'sub':
            f = F('m', int(32 * sc))
            for i, l in enumerate(wrap(d, b[1], f, CW)):
                d.text((M, y + i * f.size * 1.35), l, font=f, fill=(205, 236, 255))
        elif k == 'line':
            f = F('r', int(29 * sc))
            for i, l in enumerate(wrap(d, b[1], f, CW)):
                d.text((M, y + i * f.size * 1.4), l, font=f, fill=(225, 240, 252))
        elif k == 'price':
            f = F('b', int(84 * sc)); d.text((M, y - 6), b[1], font=f, fill=WHITE)
            if len(b) > 2:
                x = M + d.textlength(b[1], font=f) + 10
                d.text((x, y + int(40 * sc)), b[2], font=F('m', int(36 * sc)), fill=WHITE)
        elif k == 'promo':
            fs_ = F('m', int(36 * sc)); fb = F('b', int(84 * sc))
            strike(M, y + int(52 * sc), b[1], fs_, (205, 236, 255), 'ls')
            x = M + d.textlength(b[1], font=fs_) + 22
            d.text((x, y + int(52 * sc)), 'por', font=fs_, fill=(205, 236, 255), anchor='ls')
            x += d.textlength('por', font=fs_) + 16
            d.text((x, y + int(80 * sc)), b[2], font=fb, fill=ORANGE, anchor='ls')
        elif k == 'grid':
            items = b[1]; n = len(items); g = 14; cw = (CW - g * (n - 1)) / n; ch = h
            for i, (nm, de, por) in enumerate(items):
                x = M + i * (cw + g)
                d.rounded_rectangle([x, y, x + cw, y + ch], radius=22, fill=WHITE)
                cx = x + cw / 2
                d.text((cx, y + ch * 0.22), nm, font=F('m', int(25 * sc)), fill=NAVY, anchor='mm')
                strike(cx, y + ch * 0.47, de, F('r', int(23 * sc)), GRAY, 'mm')
                d.text((cx, y + ch * 0.76), por, font=F('b', int(42 * sc)), fill=ORANGE, anchor='mm')
        elif k == 'rows':
            for i, (l, r, hl) in enumerate(b[1]):
                yy = y + i * 74 * sc; rh = 62 * sc
                d.rounded_rectangle([M, yy, M + CW, yy + rh], radius=20, fill=(255, 241, 230) if hl else WHITE)
                d.text((M + 26, yy + rh / 2), l, font=F('m', int(30 * sc)), fill=NAVY, anchor='lm')
                d.text((M + CW - 26, yy + rh / 2), r, font=F('b', int(32 * sc)), fill=ORANGE if hl else BLUE, anchor='rm')
        elif k == 'steps':
            for i, t in enumerate(b[1]):
                yy = y + i * 70 * sc; r = 27 * sc
                d.ellipse([M, yy, M + 2 * r, yy + 2 * r], fill=ORANGE)
                d.text((M + r, yy + r), str(i + 1), font=F('b', int(28 * sc)), fill=WHITE, anchor='mm')
                d.text((M + 2 * r + 20, yy + r), t, font=F('m', int(31 * sc)), fill=WHITE, anchor='lm')
        elif k == 'options':
            g = 16; cw = (CW - g) / 2; ch = 88 * sc
            for i, t in enumerate(b[1]):
                x = M + (i % 2) * (cw + g); yy = y + (i // 2) * (ch + g)
                d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=24, fill=WHITE)
                L, txt = t.split(')', 1)
                d.ellipse([x + 18, yy + ch / 2 - 26, x + 70, yy + ch / 2 + 26], fill=ORANGE)
                d.text((x + 44, yy + ch / 2), L, font=F('b', int(28 * sc)), fill=WHITE, anchor='mm')
                d.text((x + 88, yy + ch / 2), txt.strip(), font=F('m', int(30 * sc)), fill=NAVY, anchor='lm')
        elif k == 'badge':
            pill(M, y, b[1], F('b', int(28 * sc)), b[2] if len(b) > 2 else ORANGE, WHITE, h=int(58 * sc))
        elif k == 'button':
            bh = int(96 * sc)
            txt = 'CHAME NO WHATSAPP E AGENDE A COLETA' if b[1] != 'story' else 'TOQUE E CHAME NO WHATSAPP'
            d.rounded_rectangle([M, y, M + CW, y + bh], radius=bh // 2, fill=GREEN)
            f = F('b', int(32 * sc)); tx = M + CW / 2
            if b[1] == 'story':
                # up arrow
                ax = M + 70; ay = y + bh / 2
                d.polygon([(ax, ay - 24), (ax - 20, ay + 2), (ax + 20, ay + 2)], fill=WHITE)
                d.rectangle([ax - 7, ay, ax + 7, ay + 22], fill=WHITE)
                tx += 30
            d.text((tx, y + bh / 2), txt, font=f, fill=WHITE, anchor='mm')
            d.text((M + CW / 2, y + bh + int(30 * sc)), 'WhatsApp ' + PHONE + '  ·  Coleta e entrega grátis', font=F('m', int(26 * sc)), fill=WHITE, anchor='mm')
        y += h + GAP

    img.convert('RGB').save(out, quality=92)
