# Kit de artes da Liga BRT: uma ficha JSON -> PNGs prontos + revisao.png
# Uso: python3 arte.py ficha.json
# Tipos: resultado | chamada (pré-corrida / É HOJE, feed + story) | curiosidade (carrossel) | etapa (banner + espera + entrevistas)
# Campos de cada tipo: veja exemplos/*.json e LEIA-ME.md. Não reescreva este arquivo para um post: mude só a ficha.
import json, math, os, shutil, subprocess, sys, html as H
from PIL import Image, ImageDraw

KIT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(KIT, 'assets')
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Permanent+Marker&family=Barlow+Condensed:wght@500;600;700;800&display=swap">'
CSS = """body{margin:0;display:flex;flex-direction:column;gap:40px;align-items:flex-start}
.s{position:relative;overflow:hidden;background:#8A3FFC;color:#fff;font-family:'Barlow Condensed',sans-serif;flex:none}
.l{position:absolute;inset:0}.a{position:absolute}
.grain{position:absolute;inset:0;background-image:url(grain.png);background-size:256px 256px;opacity:.85;pointer-events:none}
.anton{font-family:Anton,Impact,sans-serif;font-weight:400;letter-spacing:.01em}.hand{font-family:'Permanent Marker',cursive;white-space:nowrap}
.pill{border-radius:999px;display:inline-flex;align-items:center;gap:16px;font-weight:800;letter-spacing:.08em}
.brand{display:flex;align-items:center;gap:16px}.brand img{height:80px}.brand span{font-weight:800;font-size:32px;letter-spacing:.14em}
.sh{text-shadow:0 6px 30px rgba(0,0,0,.35)}
.play{width:76px;height:76px;border-radius:50%;background:#8A3FFC;display:flex;align-items:center;justify-content:center;flex:none}
"""
PLAY = '<svg width="36" height="36" viewBox="0 0 24 24" fill="#fff"><path d="M8 5v14l11-7z"/></svg>'
FIT = """<script>
function fit(){document.querySelectorAll('[data-fit]').forEach(el=>{const [w,h]=el.dataset.fit.split(',').map(Number);let fs=parseFloat(getComputedStyle(el).fontSize);
const over=()=>{const r=el.getBoundingClientRect();const inl=getComputedStyle(el).display.startsWith('inline');return el.scrollWidth>el.clientWidth+1||r.height>h||(inl&&r.width>w)};
while(over()&&fs>40){fs-=4;el.style.fontSize=fs+'px'}})}
document.fonts.ready.then(()=>{fit();document.title='ok'})</script>"""


def cacos(espelho=False):
    c = [('#7A2FEB', 'polygon(0 0,50% 0,0 34%)'), ('#A065FF', 'polygon(72% 0,100% 0,100% 26%)'), ('#6A1FD6', 'polygon(100% 66%,100% 100%,40% 100%)')]
    t = 'transform:scaleX(-1);' if espelho else ''
    return ''.join(f'<div class="l" style="background:{cor};clip-path:{p};{t}"></div>' for cor, p in c)


def tracado(cid, W=900, H=860, fino=False):
    """SVG do traçado no padrão fixo: branco grosso, sombra, bolinha preta na largada."""
    if not cid:
        return ''
    fc = json.load(open(os.path.join(A, 'f1-circuits.geojson')))
    f = next(x for x in fc['features'] if x['properties']['id'] == cid)
    g = f['geometry']; pts = g['coordinates'] if g['type'] == 'LineString' else g['coordinates'][0]
    k = math.cos(math.radians(sum(p[1] for p in pts) / len(pts)))
    xy = [(p[0] * k, -p[1]) for p in pts]
    xs, ys = [p[0] for p in xy], [p[1] for p in xy]
    sc = min(W / (max(xs) - min(xs)), H / (max(ys) - min(ys)))
    ox, oy = (W - (max(xs) - min(xs)) * sc) / 2, (H - (max(ys) - min(ys)) * sc) / 2
    P = [((x - min(xs)) * sc + ox, (y - min(ys)) * sc + oy) for x, y in xy]
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in P) + ' Z'
    sx, sy = P[0]
    return (f'<svg width="100%" height="100%" viewBox="-30 -30 {W+60} {H+60}" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="{d}" fill="none" stroke="#0B0A10" stroke-opacity=".25" stroke-width="44" stroke-linejoin="round" stroke-linecap="round" transform="translate(10,14)"/>'
            f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="30" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="26" fill="#0B0A10" stroke="#FFFFFF" stroke-width="8"/></svg>')


def foto_url(p):
    return 'file://' + os.path.abspath(p)


def pagina(corpo):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">{FONTS}<style>{CSS}</style></head><body>{corpo}{FIT}</body></html>'


def render(out, nome, html, sels, transp=False):
    open(os.path.join(out, nome + '.html'), 'w').write(html)
    r = subprocess.run(['node', os.path.join(KIT, 'render.js'), os.path.join(out, nome + '.html'), os.path.join(out, nome), ','.join(sels), '1' if transp else '0'],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-2000:])
    os.remove(os.path.join(out, nome + '.html'))
    return r.stdout.split()


# ---------------- RESULTADO (modelo fixo aprovado em 10/11) ----------------
def resultado(f, out):
    (n1, p1), (n2, p2), (n3, p3) = f['podio']
    grade = ''.join(f'<div class="r"><span class="p">{i}</span><b>{H.escape(n)}</b><span class="pt">{p}</span></div>' for i, (n, p) in enumerate(f['grade'], 4))
    if f.get('destaque'):
        v, t = f['destaque']
        grade += f'<div class="r" style="background:#fff;color:#0B0A10"><span class="p" style="background:#8A3FFC;color:#fff;font-size:22px">{v}</span><b style="font-size:24px">{t}</b></div>'
    css = """<style>.col{position:absolute;bottom:0;border-radius:34px 34px 0 0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.nm{position:absolute;text-align:center;font-weight:800;font-size:34px;letter-spacing:.02em}
.r{display:flex;align-items:center;background:#0B0A10;border-radius:999px;height:66px;padding:0 26px 0 8px;gap:16px}
.r .p{width:52px;height:52px;border-radius:50%;background:#fff;color:#0B0A10;display:flex;align-items:center;justify-content:center;font-family:Anton;font-size:28px;flex:none}
.rod b{color:#0B0A10}.r b{flex:1;font-weight:800;font-size:30px;letter-spacing:.02em;white-space:nowrap;overflow:hidden}.r span.pt{font-family:Anton;font-size:30px}</style>"""
    s = f"""{css}<div class="s" id="s1" style="width:1080px;height:1350px">
<div class="l" style="background:#7A2FEB;clip-path:polygon(0 0,46% 0,0 40%)"></div><div class="l" style="background:#A065FF;clip-path:polygon(74% 0,100% 0,100% 24%)"></div><div class="l" style="background:#6A1FD6;clip-path:polygon(100% 70%,100% 100%,44% 100%)"></div><div class="grain"></div>
<div class="a brand" style="left:0;right:0;top:44px;justify-content:center"><img src="logo.png" style="height:70px"><span style="font-size:30px;letter-spacing:.16em">LIGA BRT</span></div>
<div class="a anton" style="left:0;right:0;top:118px;text-align:center;font-size:232px;line-height:1;color:#0B0A10">{f.get('titulo','RESULTADO')}</div>
<div class="a hand" style="right:70px;top:300px;font-size:74px;transform:rotate(-4deg)">{f['manuscrito']}</div>
<div class="a" style="left:0;right:0;top:404px;text-align:center;font-weight:800;font-size:28px;letter-spacing:.14em">{f['linha']}</div>
<div class="a" style="left:110px;right:110px;top:470px;height:300px">
 <div class="nm" style="left:0;width:270px;top:62px">{n2}</div><div class="col" style="left:0;width:270px;height:190px;background:#fff;color:#0B0A10"><span class="anton" style="font-size:120px;line-height:1">2</span><span style="font-weight:800;font-size:28px">{p2} PTS</span></div>
 <div class="nm" style="left:290px;width:280px;top:0">{n1}</div><div class="col" style="left:290px;width:280px;height:250px;background:#0B0A10"><span class="anton" style="font-size:150px;line-height:1">1</span><span style="font-weight:800;font-size:28px;color:#C4A1FF">{p1} PTS</span></div>
 <div class="nm" style="left:590px;width:270px;top:92px">{n3}</div><div class="col" style="left:590px;width:270px;height:160px;background:#C4A1FF;color:#0B0A10"><span class="anton" style="font-size:110px;line-height:1">3</span><span style="font-weight:800;font-size:28px">{p3} PTS</span></div></div>
<div class="a" style="left:110px;right:110px;top:770px;height:6px;background:#0B0A10;border-radius:3px"></div>
<div class="a" style="left:70px;right:70px;top:806px;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(4,66px);gap:14px 20px">{grade}</div>
<div class="a rod" style="left:60px;right:60px;top:1150px;text-align:center;font-weight:700;font-size:30px;line-height:1.3">{f['rodape']}</div>
<div class="a" style="left:0;right:0;bottom:56px;text-align:center;font-weight:800;font-size:24px;letter-spacing:.2em">RESULTADO COMPLETO EM LIGABRT.COM.BR</div></div>"""
    return render(out, f['nome'], pagina(s), ['#s1'])


# ---------------- CHAMADA: pré-corrida / É HOJE (feed 1080x1350 + story 1080x1920) ----------------
def chamada(f, out):
    lay = f.get('layout', 'a')  # a = texto à esquerda (modelo aprovado) | b = espelhado, texto à direita
    L, R, al = ('left', 'right', 'left') if lay == 'a' else ('right', 'left', 'right')
    svg = tracado(f['circuito'])
    pos = f.get('foto_pos', '30% 40%')
    def tela(id_, h, top0, trac, man, pista, pills, rod):
        foto = (f'<div class="l" style="height:{h};background:url({foto_url(f["foto"])}) {pos}/cover;filter:grayscale(1) contrast(1.15);mix-blend-mode:luminosity;opacity:.55;'
                f'-webkit-mask-image:linear-gradient(180deg,#000 45%,transparent 100%);bottom:auto"></div>') if f.get('foto') else ''
        tx, ty, tw, th = trac
        return f"""<div class="s" id="{id_}" style="width:1080px;height:{1350 if id_=='s1' else 1920}px">{cacos(lay=='b')}{foto}<div class="grain"></div>
<div class="a brand" style="{L}:64px;top:{top0}px;flex-direction:{'row' if lay=='a' else 'row-reverse'}"><img src="logo.png"><span>LIGA BRT</span></div>
<div class="a" style="{R}:56px;top:{top0+18}px"><span class="pill" style="background:#0B0A10;font-size:30px;padding:8px 26px">{f['pilula']}</span></div>
<div class="a" style="{L if lay=='b' else 'left'}:{tx}px;top:{ty}px;width:{tw}px;height:{th}px">{svg}</div>
<div class="a hand" style="{L}:60px;top:{man - (40 if lay=='b' else 0)}px;font-size:94px;transform:rotate(-5deg);transform-origin:{al};color:#fff">{f['manuscrito']}</div>
<div class="a anton" data-fit="980,{330 if id_=='s1' else 360}" style="{L}:56px;{R}:40px;top:{pista}px;font-size:{140 if id_=='s1' else 150}px;line-height:1.08;color:#0B0A10;text-align:{al}">{f['pista']}</div>
<div class="a" style="{L}:56px;{R}:56px;top:{pills}px;display:flex;flex-direction:column;gap:20px;align-items:{'flex-start' if lay=='a' else 'flex-end'}">
<div style="display:flex;gap:16px;width:100%"><span class="pill" style="background:#fff;color:#0B0A10;padding:10px 30px"><span class="anton" style="font-size:54px">{f['data']}</span></span>
<span class="pill" style="background:#0B0A10;padding:10px 30px;flex:1;justify-content:center"><span class="anton" style="font-size:54px">{f.get('hora','LARGADA 20H')}</span></span></div>
<span class="pill" style="background:#fff;color:#0B0A10;padding:12px 30px 12px 12px"><span class="play">{PLAY}</span><span class="anton" style="font-size:58px">{f.get('chamada_live','AO VIVO NO YOUTUBE')}</span></span></div>
<div class="a" style="{L}:56px;{R}:56px;{rod};font-weight:700;font-size:28px;letter-spacing:.12em;text-align:{al}">{f.get('rodape_feed' if id_=='s1' else 'rodape_story','')}</div></div>"""
    feed = tela('s1', '760px', 56, (240, 130, 600, 480), 610, 710, 1030, 'bottom:36px')
    story = tela('s2', '1100px', 230, (180, 330, 720, 560), 930, 1040, 1440, 'top:1390px')
    r = render(out, f['nome'], pagina(feed + story), ['#s1', '#s2'])
    os.replace(r[0], os.path.join(out, f['nome'] + '.png')); os.replace(r[1], os.path.join(out, f['nome'] + '-story.png'))
    return [os.path.join(out, f['nome'] + '.png'), os.path.join(out, f['nome'] + '-story.png')]


# ---------------- CURIOSIDADE: carrossel foto real em tela cheia (rebranding 04/11) ----------------
def curiosidade(f, out):
    sl = f['slides']; n = len(sl) - 1; html = ''
    for i, s in enumerate(sl):
        blocos = ''
        if s.get('pilula'):
            blocos += f'<span class="pill" style="background:#fff;color:#0B0A10;font-size:32px;padding:10px 28px;align-self:flex-start">{s["pilula"]}</span>'
        if s.get('manuscrito_antes'):
            blocos += f'<div class="hand sh" style="font-size:80px;transform:rotate(-5deg);transform-origin:left;margin-left:14px">{s["manuscrito_antes"]}</div>'
        if s.get('titulo'):
            blocos += f'<div class="anton sh" data-fit="980,{s.get("titulo_alt",420)}" style="font-size:{s.get("titulo_tam",200)}px;line-height:.98">{s["titulo"]}</div>'
        if s.get('manuscrito'):
            blocos += f'<div class="hand sh" style="font-size:84px;transform:rotate(-5deg);transform-origin:left;margin:6px 0 0 14px">{s["manuscrito"]}</div>'
        for j, (txt, val) in enumerate(s.get('linhas', [])):
            bg, fg, vb, vf = ('#fff', '#0B0A10', '#8A3FFC', '#fff') if j % 2 == 0 else ('#0B0A10', '#fff', '#fff', '#0B0A10')
            vv = f'<span class="anton" style="background:{vb};color:{vf};border-radius:999px;padding:6px 30px;font-size:58px">{val}</span>' if val else ''
            blocos += f'<div style="display:flex;align-items:center;background:{bg};color:{fg};border-radius:999px;padding:10px 10px 10px 40px;min-height:116px;box-sizing:border-box"><span class="anton" data-fit="700,100" style="font-size:60px;flex:1">{txt}</span>{vv}</div>'
        if s.get('texto'):
            blocos += f'<div style="font-weight:700;font-size:38px;line-height:1.25;letter-spacing:.02em">{s["texto"]}</div>'
        if s.get('live'):
            blocos += f'<span class="pill" style="background:#fff;color:#0B0A10;padding:10px 32px 10px 10px;font-size:40px;align-self:flex-start"><span class="play">{PLAY}</span>{s["live"]}</span>'
        if s.get('siga'):
            blocos += '<span class="pill" style="background:#0B0A10;padding:16px 32px;font-size:40px;align-self:flex-start">SIGA @LIGA_BRT</span>'
        cta = f'<div class="a" style="right:64px;bottom:60px"><span class="pill" style="background:#0B0A10;font-size:32px;padding:12px 34px">{s["cta"]}</span></div>' if s.get('cta') else ''
        cont = f'<div class="a" style="right:60px;top:84px;font-weight:700;font-size:26px;letter-spacing:.14em">{i:02d} / {n:02d}</div>' if i and f.get('contador', True) else ''
        html += f"""<div class="s" id="s{i+1}" style="width:1080px;height:1350px">
<div class="l" style="background:url({foto_url(s['foto'])}) {s.get('pos','50% 50%')}/cover;filter:saturate(1.15) contrast(1.08){';transform:scaleX(-1)' if s.get('espelhar') else ''}"></div>
<div class="l" style="background:linear-gradient(180deg,rgba(11,10,16,.55) 0%,rgba(11,10,16,0) 22%,rgba(11,10,16,0) 42%,rgba(90,25,200,.75) 68%,#5A19C8 100%)"></div>
<div class="grain" style="opacity:.5"></div><div class="a brand" style="left:64px;top:60px"><img src="logo.png"><span style="font-size:30px">LIGA BRT</span></div>{cont}
<div class="a" style="left:56px;right:56px;bottom:{s.get('base',150 if s.get('cta') else 80)}px;display:flex;flex-direction:column;gap:20px">{blocos}</div>{cta}</div>"""
    r = render(out, f['nome'], pagina(html), [f'#s{i+1}' for i in range(len(sl))])
    return r


# ---------------- ETAPA: banner da live + tela de espera + tela de entrevistas (1920x1080) ----------------
def etapa(f, out):
    t9 = json.load(open(os.path.join(A, 't9.json'))); N = f['etapa']
    e = next(x for x in t9['etapas'] if x['n'] == N)
    pista, local, cid = f.get('pista', e['pista']), f.get('manuscrito', e['local'].title()), f.get('circuito', e['circuito'])
    camp = f.get('campeonato', t9['campeonato']); dia = f.get('data', f'DOM {e["data"]} · 20H')
    svg = tracado(cid); res = []
    pref = f'{f["data_arquivo"]}'
    ev = f.get('evento', f'T9-Etapa-{N}'); slug = f.get('pista_arquivo', pista.title().replace(' ', '-'))
    # 1) banner (modelo aprovado: foto P&B translúcida à direita, degradê roxo da esquerda)
    fb = f.get('foto_banner')
    foto = (f'<div class="a" style="top:-40px;right:-60px;width:1500px;height:1240px;background:url({foto_url(fb)}) {f.get("pos_banner","38% 40%")}/cover;filter:grayscale(1) contrast(1.15);mix-blend-mode:luminosity;opacity:.55;-webkit-mask-image:linear-gradient(180deg,#000 55%,transparent 92%)"></div>'
            '<div class="l" style="background:linear-gradient(90deg,#8A3FFC 0%,rgba(138,63,252,.85) 30%,rgba(138,63,252,0) 70%)"></div>') if fb else ''
    b = f"""<div class="s" id="b" style="width:1920px;height:1080px">
<div class="l" style="background:#7A2FEB;clip-path:polygon(0 0,34% 0,0 52%)"></div><div class="l" style="background:#A065FF;clip-path:polygon(76% 0,100% 0,100% 36%)"></div><div class="l" style="background:#6A1FD6;clip-path:polygon(100% 62%,100% 100%,50% 100%)"></div>{foto}<div class="grain"></div>
<div class="a brand" style="left:96px;top:84px;gap:22px"><img src="logo.png" style="height:120px"><span style="font-size:46px">LIGA BRT</span></div>
<div class="a" style="left:96px;top:270px;width:1000px;display:flex;flex-direction:column;align-items:flex-start;gap:14px">
<span class="pill" style="background:#0B0A10;font-size:44px;padding:10px 34px">{camp}</span>
<div class="anton" data-fit="1000,400" style="width:960px;font-size:190px;line-height:1.1;color:#0B0A10;margin-left:-12px">{pista}</div>
<div class="hand" style="transform:rotate(-5deg);transform-origin:left;font-size:84px;line-height:1;margin-top:4px">{local}</div></div>
<div class="a" style="left:96px;bottom:84px;display:flex;gap:20px"><span class="pill" style="background:#fff;color:#0B0A10;padding:14px 36px"><span class="anton" style="font-size:64px">ETAPA {N}</span></span>
<span class="pill" style="background:#0B0A10;padding:14px 36px"><span class="anton" style="font-size:64px">{dia}</span></span></div>
<div class="a" style="right:60px;top:70px;width:900px;height:860px">{svg}</div>
<div class="a" style="right:96px;bottom:84px"><span class="pill" style="background:#fff;color:#0B0A10;padding:14px 36px 14px 16px"><span class="play" style="width:72px;height:72px">{PLAY}</span><span class="anton" style="font-size:64px">AO VIVO</span></span></div></div>"""
    nb = f'{pref}_Capa-Live_{ev}_{slug}'
    res += render(out, nb, pagina(b), ['#b'])
    # 2) tela de espera (aprovada 06/11) + versão _OVERLAY com o vídeo vazado (1000x563 em x830 y120)
    fe = f.get('foto_espera', f.get('foto_banner'))
    esp = f"""<div class="s" id="e" style="width:1920px;height:1080px">
<div class="l" style="background:url({foto_url(fe)}) {f.get('pos_espera','35% 40%')}/cover;transform:scaleX(-1);filter:saturate(1.15) contrast(1.08)"></div>
<div class="l" style="background:linear-gradient(90deg,rgba(90,25,200,.9) 0%,rgba(90,25,200,.72) 35%,rgba(90,25,200,.4) 60%,rgba(40,10,90,.35) 100%)"></div>
<div class="l" style="background:linear-gradient(0deg,rgba(11,10,16,.7) 0%,rgba(11,10,16,0) 30%)"></div><div class="grain" style="opacity:.45"></div>
<div class="a brand" style="left:90px;top:70px;gap:20px"><img src="logo.png" style="height:96px"><span style="font-size:38px">LIGA BRT</span></div>
<div class="a" style="left:90px;top:230px"><span class="pill" style="background:#0B0A10;font-size:36px;padding:8px 30px">{camp}</span></div>
<div class="a anton" style="left:82px;top:290px;font-size:250px;line-height:1">ETAPA {N}</div>
<div class="a" style="left:94px;top:560px"><span class="pill" style="background:#fff;color:#0B0A10;padding:6px 30px"><span class="anton" data-fit="640,90" style="font-size:62px">{pista}</span></span></div>
<div class="a hand" style="left:100px;top:670px;font-size:76px;transform:rotate(-5deg);transform-origin:left">{local}!</div>
<div class="a" style="left:470px;top:650px;width:380px;height:360px">{svg}</div>
<div class="a" style="right:90px;top:120px;width:1000px;height:563px;border-radius:28px;background:#0B0A10;box-shadow:0 0 0 10px #fff,0 30px 80px rgba(0,0,0,.45)"></div>
<div class="a" style="right:90px;top:740px;width:1000px;display:flex;flex-direction:column;align-items:flex-end;gap:18px">
<div class="anton" style="font-size:96px;line-height:1;text-align:right">A CORRIDA COMEÇA<br>EM INSTANTES</div>
<div style="display:flex;gap:16px"><span class="pill" style="background:#fff;color:#0B0A10;padding:8px 30px 8px 10px"><span class="play" style="width:60px;height:60px">{PLAY}</span><span class="anton" style="font-size:44px">AO VIVO</span></span>
<span class="pill" style="background:#0B0A10;padding:8px 30px"><span class="anton" style="font-size:44px">{dia}</span></span></div></div></div>"""
    ne = f'{pref}_Tela-Espera_{ev}_{slug}'
    r = render(out, ne, pagina(esp), ['#e']); res += r; res.append(vazar(r[0], (830, 120, 1000, 563), 28))
    # 3) tela de entrevistas / pós-corrida com o calendário (vídeo 840x473 em x90 y560)
    rows = ''
    for x in t9['etapas']:
        i = x['n']
        if i < N: bg, fg, nb_, nf, db, df, op = 'rgba(255,255,255,.18)', '#fff', 'rgba(255,255,255,.25)', '#fff', 'rgba(11,10,16,.35)', '#fff', '.75'
        elif i == N: bg, fg, nb_, nf, db, df, op = '#0B0A10', '#fff', '#8A3FFC', '#fff', '#fff', '#0B0A10', '1'
        else: bg, fg, nb_, nf, db, df, op = '#fff', '#0B0A10', '#0B0A10', '#fff', '#8A3FFC', '#fff', '1'
        tag = '<span style="font-family:Barlow Condensed;font-weight:800;font-size:18px;letter-spacing:.14em;background:#8A3FFC;color:#fff;border-radius:999px;padding:3px 12px;margin-left:12px">HOJE</span>' if i == N else ''
        rows += (f'<div class="r" style="background:{bg};color:{fg};opacity:{op}"><span class="n anton" style="background:{nb_};color:{nf}">{"✓" if i < N else i}</span>'
                 f'<span class="t"><b class="anton">{x["pista"]}{tag}</b><i>{x["local"]}</i></span><span class="d anton" style="background:{db};color:{df}">{x["data"]}</span></div>')
    fi = f.get('foto_entrevistas', fe)
    ent = f"""<style>.r{{display:flex;align-items:center;gap:16px;border-radius:999px;height:84px;padding:0 10px;box-sizing:border-box}}
.n{{width:64px;height:64px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:32px;flex:none}}
.t{{flex:1;display:flex;flex-direction:column;line-height:1}}.t b{{font-size:38px;display:flex;align-items:center;font-weight:400}}.t i{{font-style:normal;font-weight:800;font-size:17px;letter-spacing:.14em;opacity:.7;margin-top:4px}}
.d{{border-radius:999px;padding:6px 22px;font-size:34px}}</style>
<div class="s" id="t" style="width:1920px;height:1080px;background:#5A19C8">
<div class="l" style="background:url({foto_url(fi)}) {f.get('pos_entrevistas','30% 50%')}/cover;filter:saturate(1.15) contrast(1.08)"></div>
<div class="l" style="background:linear-gradient(90deg,rgba(90,25,200,.55) 0%,rgba(90,25,200,.7) 45%,#5A19C8 58%,#5A19C8 100%)"></div><div class="grain" style="opacity:.45"></div>
<div class="a brand" style="left:90px;top:64px;gap:20px"><img src="logo.png" style="height:90px"><span style="font-size:36px">LIGA BRT</span></div>
<div class="a" style="left:90px;top:196px"><span class="pill" style="background:#0B0A10;font-size:34px;padding:8px 28px">{camp} · ETAPA {N}</span></div>
<div class="a anton" style="left:84px;top:272px;font-size:160px;line-height:1">PÓS-CORRIDA</div>
<div class="a hand" style="left:96px;top:452px;font-size:60px;transform:rotate(-4deg);transform-origin:left">papo com os pilotos</div>
<div class="a" style="left:90px;top:560px;width:840px;height:473px;border-radius:26px;background:#0B0A10;box-shadow:0 0 0 10px #fff,0 30px 80px rgba(0,0,0,.45)"></div>
<div class="a" style="left:1060px;right:80px;top:44px;display:flex;align-items:baseline;justify-content:space-between"><span class="anton" style="font-size:96px;line-height:1">CALENDÁRIO</span><span class="hand" style="font-size:46px;color:#C4A1FF;transform:rotate(-4deg)">T9</span></div>
<div class="a" style="left:1060px;right:80px;top:168px;display:flex;flex-direction:column;gap:12px">{rows}</div></div>"""
    nt = f'{pref}_Tela-Entrevistas_{ev}'
    r = render(out, nt, pagina(ent), ['#t']); res += r; res.append(vazar(r[0], (90, 560, 840, 473), 26))
    return res


def vazar(png, box, raio):
    """Cria a versão _OVERLAY com o quadro do vídeo transparente (para o OBS)."""
    x, y, w, h = box
    im = Image.open(png).convert('RGBA'); m = Image.new('L', im.size, 255)
    ImageDraw.Draw(m).rounded_rectangle([x, y, x + w, y + h], raio, fill=0)
    im.putalpha(m); o = png[:-4] + '_OVERLAY.png'; im.save(o); return o


def revisao(arqs, out):
    ims = [Image.open(a).convert('RGB') for a in arqs]
    alt = 480; th = [i.resize((int(i.width * alt / i.height), alt)) for i in ims]
    W = min(2400, sum(t.width for t in th) + 20 * (len(th) + 1))
    linhas, cur, x = [], [], 20
    for t in th:
        if x + t.width + 20 > W and cur: linhas.append(cur); cur, x = [], 20
        cur.append(t); x += t.width + 20
    linhas.append(cur)
    S = Image.new('RGB', (W, len(linhas) * (alt + 20) + 20), '#222')
    for li, row in enumerate(linhas):
        x = 20
        for t in row: S.paste(t, (x, 20 + li * (alt + 20))); x += t.width + 20
    p = os.path.join(out, 'revisao.png'); S.save(p); return p


if __name__ == '__main__':
    f = json.load(open(sys.argv[1]))
    out = os.path.abspath(f.get('saida') or os.path.dirname(os.path.abspath(sys.argv[1])))
    os.makedirs(out, exist_ok=True)
    for a in ('grain.png', 'logo.png'):
        shutil.copy(os.path.join(A, a), out)
    arqs = {'resultado': resultado, 'chamada': chamada, 'curiosidade': curiosidade, 'etapa': etapa}[f['tipo']](f, out)
    for a in ('grain.png', 'logo.png'):
        os.remove(os.path.join(out, a))
    print('\n'.join(arqs)); print('REVISAO:', revisao(arqs, out))
