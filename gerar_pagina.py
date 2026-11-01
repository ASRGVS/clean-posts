import json, datetime, base64, html, sys
base = sys.argv[1] if len(sys.argv) > 1 else '.'
cal = json.load(open(f'{base}/calendario.json'))
logo = base64.b64encode(open(f'{base}/logo-cor.png', 'rb').read()).decode()
dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
fer = {'2026-11-02': 'Feriado · Finados', '2026-11-15': 'Feriado · domingo, fechado', '2026-11-20': 'Feriado · Consciência Negra', '2026-11-27': 'Black Friday'}
fases = {1: ('Semana 1 · 1 a 8/11', 'Feed principal às 19h; terça e quinta também às 12h. Stories em horário diferente do feed.'),
         2: ('Semana 2 · 9 a 15/11', 'Inverte: feed principal às 12h; terça e quinta também às 19h.'),
         3: ('Semana 3 · 16 a 22/11', 'Testa manhã (8h) contra noite (19h).'),
         4: ('Semana 4 · 23 a 30/11 · Black Friday', 'Feed no horário vencedor; stories no horário oposto.')}
def sem(d):
    n = int(d[-2:]); return 1 if n <= 8 else 2 if n <= 15 else 3 if n <= 22 else 4
def hora(h):
    return {'melhor': 'Horário vencedor', 'oposto': 'Horário oposto'}.get(h, h.replace(':00', 'h'))
def item(it):
    st = f'<span class="ok">{it["status"]}</span>' if it.get('status') else ''
    pr = f'<div class="pr">⚠ {html.escape(it["precisa"])}</div>' if it.get('precisa') else ''
    f0 = it['formato'].split(' ·')[0]
    cls = {'Edredom': 'ed', 'Plano mensal': 'pl', 'Pacote avulso': 'pa'}.get(f0, '')
    badge = f'<span class="lb {cls}">{f0}</span>' if cls else ''
    return f'<div class="it"><div class="meta"><b>{hora(it["hora"])}</b> · {badge if cls else it["formato"]}{(' · ' + it['formato'].split(' · ',1)[1]) if cls and ' · ' in it['formato'] else ''}</div><div class="tm">{html.escape(it["tema"])} {st}</div>{pr}</div>'
datas = sorted({x['data'] for x in cal})
rows = ''; cur = 0
for d in datas:
    s = sem(d)
    if s != cur:
        cur = s; t, desc = fases[s]
        rows += f'<tr class="fase"><td colspan="3"><b>{t}</b> — {desc}</td></tr>'
    dt = datetime.date.fromisoformat(d)
    f = fer.get(d, '')
    posts = ''.join(item(x) for x in cal if x['data'] == d and x['tipo'] == 'post')
    stories = ''.join(item(x) for x in cal if x['data'] == d and x['tipo'] == 'story')
    rows += f'<tr><td class="dt"><b>{dt.day:02d}/11</b><br><span>{dias[dt.weekday()]}</span>{"<div class=fer>" + f + "</div>" if f else ""}</td><td>{posts}</td><td class="sto">{stories}</td></tr>'
pend = sorted({x['precisa'] for x in cal if x.get('precisa')})
ned = len([x for x in cal if x['tipo']=='post' and x['formato'].startswith('Edredom')]); npl = len([x for x in cal if x['tipo']=='post' and x['formato'].startswith('Plano')]); npa = len([x for x in cal if x['tipo']=='post' and x['formato'].startswith('Pacote')])
np = len([x for x in cal if x['tipo'] == 'post']); ns = len([x for x in cal if x['tipo'] == 'story'])
page = f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calendário de posts · Novembro 2026 · Clean</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;font-family:Poppins,sans-serif;background:#f3f9fd;color:#0a2f57}}
.wrap{{max-width:1100px;margin:0 auto;padding:32px 20px 60px}}
header{{display:flex;align-items:center;gap:24px;flex-wrap:wrap}}header img{{height:64px}}
h1{{font-size:28px;margin:0}}header p{{margin:4px 0 0;color:#4a6078}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:28px 0}}
.card{{background:#fff;border-radius:16px;padding:18px 20px;box-shadow:0 1px 3px rgba(10,47,87,.08)}}
.card b{{display:block;font-size:28px;color:#0f62ac}}.card span{{color:#4a6078;font-size:14px}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 1px 3px rgba(10,47,87,.08)}}
td{{padding:12px 14px;border-bottom:1px solid #e6eef5;vertical-align:top;font-size:15px}}
th{{text-align:left;background:#0f62ac;color:#fff;padding:12px 14px;font-size:14px}}
th.sto{{background:#00afef}}td.sto{{background:#f7fcff}}
tr.fase td{{background:#e3f4fd;color:#0f62ac;font-size:14px}}
.dt{{width:90px}}.dt span{{color:#4a6078;font-size:13px}}.fer{{font-size:11px;color:#f58634;font-weight:600;margin-top:2px}}
.it+.it{{margin-top:12px;padding-top:12px;border-top:1px dashed #d5e4ef}}
.meta{{font-size:13px;color:#4a6078}}.meta b{{color:#0f62ac}}.tm{{font-weight:600;margin-top:2px}}
.pr{{color:#c05a10;font-size:13px;margin-top:4px}}
.lb{{font-size:11px;font-weight:700;color:#fff;padding:2px 8px;border-radius:10px;margin-left:4px}}.ed{{background:#f58634}}.pl{{background:#0f62ac}}.pa{{background:#00afef}}
.ok{{background:#25a35a;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;margin-left:6px}}
h2{{font-size:20px;margin:36px 0 10px}}ul{{background:#fff;border-radius:16px;padding:18px 18px 18px 38px;margin:0}}li{{margin:6px 0}}
@media(max-width:640px){{td{{font-size:13px;padding:10px 8px}}th{{font-size:12px;padding:10px 8px}}.dt{{width:56px}}}}
</style></head><body><div class="wrap">
<header><img src="data:image/png;base64,{logo}" alt="Clean"><div><h1>Calendário de posts · Novembro 2026</h1><p>@lavanderia.cleangv · todo post e story passa por aprovação antes de publicar</p></div></header>
<div class="cards">
<div class="card"><b>{np}</b><span>posts no feed</span></div>
<div class="card"><b>{ns}</b><span>stories, um por dia, com tema diferente do feed; 15 com preço</span></div>
<div class="card"><b>{ned} · {npl} · {npa}</b><span>posts de edredom · planos mensais · pacotes avulsos</span></div>
<div class="card"><b>2/11 e 20/11</b><span>posts avisando que abrimos no feriado</span></div>
</div>
<table><tr><th>Dia</th><th>Feed</th><th class="sto">Stories</th></tr>{rows}</table>
<h2>Regras fixas</h2><ul>
<li>A Clean é especializada em roupas: nada de tapetes, cortinas ou estofados.</li>
<li>Todo feriado de segunda a sábado tem um post leve avisando que estamos funcionando para ajudar as famílias na rotina. Domingo é fechado.</li>
<li>Story e feed do mesmo dia nunca repetem o assunto. Metade dos stories mostra preço, em dias alternados.</li><li>WhatsApp: pessoa física (33) 98761-0434 · empresas, Airbnb, restaurantes, salões e uniformes (33) 98749-0985. Posts marcados com PJ usam o número de empresas.</li><li>Prioridade de captação: higienização de edredom, pacotes Limpo + Dobrado e planos mensais (um post para cada plano). Feed testa 12h × 19h × 8h nas 3 primeiras semanas.</li></ul>
<h2>O que preciso de você ao longo do mês</h2><ul>{''.join(f'<li>{html.escape(p)}</li>' for p in pend)}</ul>
<h2>Como vamos medir</h2><ul><li>Para cada post, comparo o alcance, os salvamentos e os compartilhamentos nas primeiras 24h.</li><li>No dia 22 escolho o horário vencedor e uso nele a semana da Black Friday.</li><li>Responder os comentários na primeira hora ajuda o post a chegar em mais gente.</li></ul>
</div></body></html>'''
open(f'{base}/index.html', 'w').write(page)
