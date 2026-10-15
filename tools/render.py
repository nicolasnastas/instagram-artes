"""Renderiza um carrossel 1080x1350 (4:5) no padrão visual do escritório.

Uso: python tools/render.py carrosseis/<pasta>/roteiro.json
Gera slide-01.jpg ... slide-NN.jpg na mesma pasta do roteiro.
"""
import json
import sys
import html
from pathlib import Path
from playwright.sync_api import sync_playwright

PALETTE = {
    "dark_bg": "#1E3B34",
    "dark_text": "#F4EFE6",
    "dark_muted": "#B9CBC4",
    "light_bg": "#F4EFE6",
    "light_text": "#1B2B27",
    "light_muted": "#4E5F5A",
    "coral": "#E8735A",
    "amber": "#E5A33B",
}

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 1080px; height: 1350px; }
body { font-family: 'Inter', sans-serif; }
.slide { width: 1080px; height: 1350px; padding: 84px 88px; display: flex;
         flex-direction: column; position: relative; overflow: hidden; }
.dark { background: var(--dark_bg); color: var(--dark_text); }
.light { background: var(--light_bg); color: var(--light_text); }
.top { display: flex; justify-content: space-between; align-items: center;
       font-size: 28px; font-weight: 600; letter-spacing: 0.2px; }
.pill { font-size: 22px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;
        padding: 10px 22px; border-radius: 999px; background: var(--coral); color: #fff; }
.main { flex: 1; display: flex; flex-direction: column; justify-content: center; }
h1 { font-family: 'Inter Display', 'Inter', sans-serif; font-weight: 700; font-size: 78px;
     line-height: 1.08; letter-spacing: -1.5px; }
.hook h1 { font-size: 92px; }
h1 em { font-style: normal; color: var(--coral); }
.bar { width: 96px; height: 8px; background: var(--amber); border-radius: 4px; margin: 44px 0 40px; }
p { font-size: 38px; line-height: 1.45; font-weight: 400; max-width: 860px; white-space: pre-line; }
.dark p { color: var(--dark_muted); }
.light p { color: var(--light_muted); }
.sign { margin-top: 36px; font-size: 30px; font-weight: 600; }
.dark .sign { color: var(--dark_text); }
.bottom { display: flex; justify-content: space-between; align-items: center; font-size: 24px;
          font-weight: 600; letter-spacing: 1.5px; }
.dark .bottom { color: var(--dark_muted); }
.light .bottom { color: var(--light_muted); }
.dots { display: flex; gap: 12px; }
.dot { width: 12px; height: 12px; border-radius: 50%; background: currentColor; opacity: .35; }
.dot.on { background: var(--coral); opacity: 1; width: 36px; border-radius: 6px; }
.quote h1 { color: var(--amber); }
.deco { position: absolute; right: -160px; bottom: -160px; width: 520px; height: 520px;
        border-radius: 50%; border: 3px solid var(--coral); opacity: .18; }
"""


def esc(s):
    return html.escape(s or "")


def slide_html(s, i, n, perfil):
    tone = s.get("fundo", "light")
    kind = s.get("tipo", "")
    title = esc(s["titulo"])
    for word in s.get("destaque", []):
        title = title.replace(esc(word), f"<em>{esc(word)}</em>", 1)
    pill = f'<span class="pill">{esc(s["etiqueta"])}</span>' if s.get("etiqueta") else "<span></span>"
    body = f"<p>{esc(s['texto'])}</p>" if s.get("texto") else ""
    sign = f'<div class="sign">{esc(s["assinatura"])}</div>' if s.get("assinatura") else ""
    dots = "".join(f'<span class="dot{" on" if k == i else ""}"></span>' for k in range(n))
    nxt = "ARRASTE →" if i < n - 1 else ""
    deco = '<div class="deco"></div>' if tone == "dark" else ""
    vars_ = ";".join(f"--{k}:{v}" for k, v in PALETTE.items())
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{{vars_}}}{CSS}</style></head>
<body><div class="slide {tone} {kind}">{deco}
<div class="top"><span>@{esc(perfil)}</span>{pill}</div>
<div class="main"><h1>{title}</h1><div class="bar"></div>{body}{sign}</div>
<div class="bottom"><span>{i + 1:02d}/{n:02d}</span><span class="dots">{dots}</span><span>{nxt}</span></div>
</div></body></html>"""


def main(path):
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    out = Path(path).parent
    slides = spec["slides"]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides):
            pg.set_content(slide_html(s, i, len(slides), spec["perfil"]), wait_until="load")
            pg.screenshot(path=str(out / f"slide-{i + 1:02d}.jpg"), type="jpeg", quality=92)
        b.close()
    print(f"{len(slides)} slides em {out}")


if __name__ == "__main__":
    main(sys.argv[1])
