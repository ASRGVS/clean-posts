#!/usr/bin/env python3
"""Lê (só leitura) o desempenho dos anúncios da Meta da Lavanderia Clean e grava em relatorios/.

Uso:
  python automacao/anuncios_meta.py                    # ontem e acumulado desde 17/11/2026
  python automacao/anuncios_meta.py 2026-11-17 2026-11-19
Saída: relatorios/anuncios-meta.json (sobrescrito a cada execução) com linhas por conjunto e por anúncio.
Não altera nada nas campanhas.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publicar_meta import AD_ACCOUNT, RAIZ, api  # noqa: E402

TZ = ZoneInfo("America/Sao_Paulo")
INICIO_PERIODO = os.environ.get("INICIO_PERIODO", "2026-11-17")
CAMPOS = ",".join([
    "campaign_name", "adset_name", "adset_id", "ad_name", "ad_id", "spend", "impressions", "reach",
    "frequency", "clicks", "ctr", "actions", "cost_per_action_type",
])
CONVERSA = "onsite_conversion.messaging_conversation_started_7d"


def insights(nivel, inicio, fim, quebra=None):
    linhas, depois = [], None
    while True:
        p = {"level": nivel, "fields": CAMPOS, "time_range": json.dumps({"since": inicio, "until": fim}), "limit": 200}
        if quebra:
            p["breakdowns"] = quebra
        if depois:
            p["after"] = depois
        r = api("GET", f"{AD_ACCOUNT}/insights", p)
        for l in r.get("data", []):
            acoes = {a["action_type"]: float(a["value"]) for a in l.pop("actions", [])}
            custos = {a["action_type"]: float(a["value"]) for a in l.pop("cost_per_action_type", [])}
            l["conversas"] = acoes.get(CONVERSA, 0)
            l["custo_por_conversa"] = custos.get(CONVERSA)
            linhas.append(l)
        depois = r.get("paging", {}).get("cursors", {}).get("after") if r.get("paging", {}).get("next") else None
        if not depois:
            return [l for l in linhas if "VAGA" not in (l.get("campaign_name", "") + l.get("adset_name", "")).upper()]


def orcamentos():
    r = api("GET", f"{AD_ACCOUNT}/adsets", {"fields": "name,status,effective_status,daily_budget,campaign{name}", "limit": 200})
    return [{"conjunto": a["name"], "campanha": a.get("campaign", {}).get("name"), "status": a.get("effective_status"),
             "orcamento_dia": int(a.get("daily_budget", 0)) / 100 if a.get("daily_budget") else None} for a in r.get("data", [])]


def main():
    hoje = datetime.now(TZ).date()
    ontem = (hoje - timedelta(days=1)).isoformat()
    if len(sys.argv) == 3:
        periodos = {"periodo": (sys.argv[1], sys.argv[2])}
    else:
        periodos = {"ontem": (ontem, ontem), "acumulado": (INICIO_PERIODO, ontem)}
    saida = {"gerado_em": datetime.now(TZ).isoformat(timespec="minutes"), "conta": AD_ACCOUNT, "orcamentos": orcamentos()}
    for nome, (a, b) in periodos.items():
        saida[nome] = {"de": a, "ate": b, "conjuntos": insights("adset", a, b), "anuncios": insights("ad", a, b)}
    # Facebook x Instagram (e demais posicionamentos): acumulado do período e últimos 30 dias, até hoje
    for nome, ini in (("plataformas_periodo", INICIO_PERIODO), ("plataformas_30d", (hoje - timedelta(days=30)).isoformat())):
        try:
            saida[nome] = {"de": ini, "ate": hoje.isoformat(),
                           "conjuntos": insights("adset", ini, hoje.isoformat(), "publisher_platform")}
        except Exception as e:  # não derruba o relatório diário
            saida[nome] = {"erro": str(e)}
    os.makedirs(os.path.join(RAIZ, "relatorios"), exist_ok=True)
    with open(os.path.join(RAIZ, "relatorios", "anuncios-meta.json"), "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    for nome in periodos:
        print(f"== {nome} ({saida[nome]['de']} a {saida[nome]['ate']})")
        for l in saida[nome]["conjuntos"]:
            print(f"  {l.get('adset_name','')[:45]:45} gasto R$ {float(l.get('spend',0)):7.2f} | conversas {l['conversas']:4.0f} | "
                  f"custo/conv {('R$ %.2f' % l['custo_por_conversa']) if l['custo_por_conversa'] else '-'}")


if __name__ == "__main__":
    main()
