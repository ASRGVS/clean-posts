#!/usr/bin/env python3
"""Publicador automático da Lavanderia Clean (Instagram + Página do Facebook) pela API oficial da Meta.

Roda no GitHub Actions (.github/workflows/publicar-meta.yml) a cada 15 minutos.

Regra de segurança: só publica itens do calendario.json que tenham o campo
    "api": "aprovado"
(colocado depois da aprovação do dono). Itens sem esse campo são ignorados.

Tipos suportados (campo "tipo"):
  post      -> feed do Instagram + Página do Facebook (posts/AAAA-MM-DD/feed1.jpg, ou feed1..feedN.jpg = carrossel)
               legendas: legenda-feed.txt (Instagram) e legenda-facebook.txt (Facebook)
  facebook  -> só Página do Facebook (fb-extra.jpg + legenda-fb-extra.txt)
  story     -> story do Instagram (story.jpg). Stories de enquete/quiz precisam do adesivo pelo app: não use api=aprovado neles.
  reels     -> Reels do Instagram, compartilhado no feed. Vídeo/legenda/capa lidos do campo "precisa"
               ("Vídeo pronto: <caminho.mp4> · legenda <caminho.txt>"); capa = <video>-capa.jpg se existir.

Publica quando a data/hora (horário de Brasília) chegou e no máximo JANELA_HORAS depois.
Depois de publicar grava no item: status "Publicado DD/MM HH:MM (API)", "api": "publicado" e os IDs.
Em erro grava "api": "erro" e a mensagem em "api_erro" (não tenta de novo sozinho) e termina com código 1
para o GitHub avisar por e-mail.

Uso:
  python automacao/publicar_meta.py             # publica o que estiver na hora
  python automacao/publicar_meta.py --verificar # só testa a chave e lista contas (não publica nada)
  python automacao/publicar_meta.py --simular   # mostra o que publicaria agora, sem publicar
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

GRAPH = "https://graph.facebook.com/" + os.environ.get("META_API_VERSION", "v23.0")
PAGE_ID = os.environ.get("META_PAGE_ID", "109109548529077")
IG_ID = os.environ.get("META_IG_ID", "17841451314416418")
AD_ACCOUNT = os.environ.get("META_AD_ACCOUNT", "act_2060604801080316")
REPO_RAW = os.environ.get("REPO_RAW", "https://raw.githubusercontent.com/ASRGVS/clean-posts/main")
TZ = ZoneInfo("America/Sao_Paulo")
JANELA_HORAS = float(os.environ.get("JANELA_HORAS", "3"))
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(RAIZ, "calendario.json")


class ErroMeta(Exception):
    pass


def token():
    t = os.environ.get("META_TOKEN", "").strip()
    if not t:
        raise SystemExit("META_TOKEN não configurado nos segredos do repositório.")
    return t


def api(metodo, caminho, params=None, tok=None):
    params = dict(params or {})
    params["access_token"] = tok or token()
    url = f"{GRAPH}/{caminho.lstrip('/')}"
    dados = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(url + "?" + dados.decode())
    else:
        req = urllib.request.Request(url, data=dados, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        try:
            msg = json.loads(corpo).get("error", {}).get("message", corpo)
        except ValueError:
            msg = corpo
        raise ErroMeta(f"{metodo} {caminho}: HTTP {e.code} — {msg}") from None


def token_pagina():
    r = api("GET", PAGE_ID, {"fields": "access_token,name"})
    if "access_token" not in r:
        raise ErroMeta("A chave não tem acesso de publicação à Página (sem access_token da Página).")
    return r["access_token"]


def raw(caminho):
    return f"{REPO_RAW}/{urllib.parse.quote(caminho)}"


def ler(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return f.read().strip()


def existe(caminho):
    return os.path.isfile(os.path.join(RAIZ, caminho))


# ---------- Instagram ----------
def ig_esperar(container, limite=600):
    fim = time.time() + limite
    while time.time() < fim:
        st = api("GET", container, {"fields": "status_code,status"})
        cod = st.get("status_code")
        if cod == "FINISHED":
            return
        if cod in ("ERROR", "EXPIRED"):
            raise ErroMeta(f"Instagram recusou a mídia: {st.get('status')}")
        time.sleep(10)
    raise ErroMeta("Instagram demorou demais para processar a mídia.")


def ig_publicar(container):
    ig_esperar(container)
    return api("POST", f"{IG_ID}/media_publish", {"creation_id": container})["id"]


def ig_imagem(imagens, legenda):
    if len(imagens) == 1:
        c = api("POST", f"{IG_ID}/media", {"image_url": raw(imagens[0]), "caption": legenda})["id"]
        return ig_publicar(c)
    filhos = [api("POST", f"{IG_ID}/media", {"image_url": raw(i), "is_carousel_item": "true"})["id"] for i in imagens]
    for f in filhos:
        ig_esperar(f)
    c = api("POST", f"{IG_ID}/media", {"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda})["id"]
    return ig_publicar(c)


def ig_story(imagem):
    c = api("POST", f"{IG_ID}/media", {"image_url": raw(imagem), "media_type": "STORIES"})["id"]
    return ig_publicar(c)


def ig_reels(video, legenda, capa=None):
    p = {"media_type": "REELS", "video_url": raw(video), "caption": legenda, "share_to_feed": "true"}
    if capa:
        p["cover_url"] = raw(capa)
    c = api("POST", f"{IG_ID}/media", p)["id"]
    return ig_publicar(c)


# ---------- Facebook ----------
def fb_fotos(imagens, legenda, tok_pag):
    if len(imagens) == 1:
        r = api("POST", f"{PAGE_ID}/photos", {"url": raw(imagens[0]), "message": legenda, "published": "true"}, tok_pag)
        return r.get("post_id") or r["id"]
    ids = [api("POST", f"{PAGE_ID}/photos", {"url": raw(i), "published": "false"}, tok_pag)["id"] for i in imagens]
    p = {"message": legenda}
    for n, i in enumerate(ids):
        p[f"attached_media[{n}]"] = json.dumps({"media_fbid": i})
    return api("POST", f"{PAGE_ID}/feed", p, tok_pag)["id"]


# ---------- calendário ----------
def quando(item):
    h = item.get("hora", "")
    if not re.fullmatch(r"\d{1,2}:\d{2}", h or ""):
        return None
    try:
        return datetime.strptime(f"{item['data']} {h}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    except (KeyError, ValueError):
        return None


def imagens_feed(pasta):
    fs = sorted(f for f in os.listdir(os.path.join(RAIZ, pasta)) if re.fullmatch(r"feed\d+\.jpg", f))
    fs.sort(key=lambda f: int(re.findall(r"\d+", f)[0]))
    return [f"{pasta}/{f}" for f in fs]


def midia_reels(item):
    txt = item.get("precisa", "")
    v = re.search(r"(\S+\.mp4)", txt)
    l = re.search(r"legenda\s+(\S+\.txt)", txt)
    if not v or not l:
        raise ErroMeta("Reels sem caminho de vídeo/legenda no campo 'precisa'.")
    capa = v.group(1)[:-4] + "-capa.jpg"
    return v.group(1), ler(l.group(1)), capa if existe(capa) else None


def publicar_item(item):
    pasta = f"posts/{item['data']}"
    tipo = item.get("tipo")
    ids = {}
    if tipo == "post":
        imgs = imagens_feed(pasta)
        if not imgs:
            raise ErroMeta(f"Sem feed1.jpg em {pasta}.")
        leg_ig = ler(f"{pasta}/legenda-feed.txt")
        leg_fb = ler(f"{pasta}/legenda-facebook.txt") if existe(f"{pasta}/legenda-facebook.txt") else leg_ig
        ids["instagram"] = ig_imagem(imgs, leg_ig)
        ids["facebook"] = fb_fotos(imgs, leg_fb, token_pagina())
    elif tipo == "facebook":
        ids["facebook"] = fb_fotos([f"{pasta}/fb-extra.jpg"], ler(f"{pasta}/legenda-fb-extra.txt"), token_pagina())
    elif tipo == "story":
        ids["instagram"] = ig_story(f"{pasta}/story.jpg")
    elif tipo == "reels":
        video, leg, capa = midia_reels(item)
        ids["instagram"] = ig_reels(video, leg, capa)
    else:
        raise ErroMeta(f"Tipo '{tipo}' não suportado.")
    return ids


def verificar():
    me = api("GET", "me", {"fields": "id,name"})
    print("Chave OK — usuário:", me.get("name"), me.get("id"))
    pg = api("GET", PAGE_ID, {"fields": "name,access_token"})
    print("Página:", pg.get("name"), "| pode publicar:", "access_token" in pg)
    ig = api("GET", IG_ID, {"fields": "username,followers_count"})
    print("Instagram:", ig.get("username"), "| seguidores:", ig.get("followers_count"))
    lim = api("GET", f"{IG_ID}/content_publishing_limit", {"fields": "quota_usage,config"})
    print("Limite de publicação IG (24h):", json.dumps(lim.get("data", lim), ensure_ascii=False))
    try:
        ad = api("GET", AD_ACCOUNT, {"fields": "name,account_status"})
        print("Conta de anúncios:", ad.get("name"), "| status:", ad.get("account_status"))
    except ErroMeta as e:
        print("Conta de anúncios: sem acesso ->", e)


def main():
    if "--verificar" in sys.argv:
        verificar()
        return 0
    simular = "--simular" in sys.argv
    agora = datetime.now(TZ)
    with open(CAL, encoding="utf-8") as f:
        bruto = f.read()
    cal = json.loads(bruto)
    mudou, falhas = False, []
    for item in cal:
        if item.get("api") != "aprovado":
            continue
        t = quando(item)
        if t is None:
            print("Sem horário fixo, pulando:", item.get("data"), item.get("tipo"), item.get("tema", "")[:50])
            continue
        if agora < t:
            continue
        if agora - t > timedelta(hours=JANELA_HORAS):
            print("Passou da janela, não publico sozinho:", item["data"], item["hora"], item["tipo"])
            continue
        rotulo = f"{item['data']} {item['hora']} {item['tipo']} — {item.get('tema', '')[:60]}"
        if simular:
            print("PUBLICARIA:", rotulo)
            continue
        print("Publicando:", rotulo)
        try:
            ids = publicar_item(item)
        except ErroMeta as e:
            print("ERRO:", e)
            item["api"] = "erro"
            item["api_erro"] = str(e)[:500]
            falhas.append(rotulo)
        else:
            hora = datetime.now(TZ).strftime("%d/%m %H:%M")
            item["api"] = "publicado"
            item["status"] = f"Publicado {hora} (API)"
            item["api_ids"] = ids
            print("OK:", ids)
        mudou = True
    if mudou and not simular:
        with open(CAL, "w", encoding="utf-8") as f:
            f.write(json.dumps(cal, indent=1, ensure_ascii=False) + ("\n" if bruto.endswith("\n") else ""))
    if falhas:
        print("Falhas:", *falhas, sep="\n- ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
