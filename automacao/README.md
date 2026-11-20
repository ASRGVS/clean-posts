# Automação Meta — Lavanderia Clean

Publica no Instagram (@lavanderia.cleangv) e na Página do Facebook "Lavanderia Clean" pela API oficial da Meta,
sem depender do computador do dono. Roda no GitHub Actions.

- App da Meta: **Clean Posts** (ID 1708873567490223), portfólio Lavanderia Clean.
- Chave: usuário do sistema **Publicador Posts** (sem validade), guardada no segredo `META_TOKEN` do repositório.
  Acesso: Página (conteúdos + estatísticas), Instagram (conteúdos + estatísticas), conta de anúncios (só ver desempenho).

## Como um post sai
1. O dono aprova o post na conversa com o Claude.
2. O Claude salva arte e legendas em `posts/AAAA-MM-DD/` e marca o item do `calendario.json` com `"api": "aprovado"` e hora fixa (`"hora": "HH:MM"`).
3. O workflow **Publicar Meta** roda a cada 15 min e publica quando chega a hora (até 3 h depois; passou disso, não publica sozinho).
4. O item fica com `"api": "publicado"`, `status` "Publicado DD/MM HH:MM (API)" e os IDs. Em erro: `"api": "erro"` + `api_erro`, e o GitHub manda e-mail.

Stories com enquete/quiz/caixinha precisam do adesivo pelo app: não marcar `api: aprovado` neles.

## Testar a chave
Actions › Publicar Meta › Run workflow › modo `verificar` (não publica nada).

## Anúncios (só leitura)
Workflow **Relatório de anúncios Meta**: todo dia 06:30 (Brasília) grava `relatorios/anuncios-meta.json`
com gasto, conversas e custo por conversa de ontem e do acumulado desde 17/11/2026, por conjunto e por anúncio.
