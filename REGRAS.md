# Regras de comunicação — Lavanderia Clean

- A Clean é especializada em ROUPAS. Nunca mencionar tapetes, cortinas, sofás ou estofados.
- Funciona em todos os feriados de segunda a sábado. Fecha aos domingos.
- Todo post precisa ser aprovado pelo dono antes de publicar.
- Usar as logos da pasta marca/ e as cores: azul #0f62ac, azul claro #00afef, laranja #f58634. Fonte Poppins.
- Carrosséis curtos (3 telas). Legendas curtas e naturais, nada engessado.
- Todo feriado de segunda a sábado: criar um post leve avisando que a Clean está funcionando para ajudar as famílias na rotina.
- Um story por dia, sempre com assunto diferente do post do feed do mesmo dia, revezando os temas. Story em horário diferente do feed.
- Prioridade de captação: 1) higienização de edredom (serviço principal), 2) pacotes Limpo + Dobrado, 3) planos mensais — um post por plano, mostrando a facilidade de receber roupa limpa (e passada) toda semana pagando por mês.
- Preços oficiais: ver as páginas clean-roupa-de-cama, lavanderia-clean-planos, clean-roupas-sociais (asrgv14.chatgpt.site) e lavanderiacleangv.com. WhatsApp (33) 98761-0434.
- WhatsApp: pessoa física → (33) 98761-0434. Empresas, Airbnb, restaurantes, salões e uniformes → (33) 98749-0985.
- Stories: metade com preço (dias alternados), sempre de um serviço diferente do post do feed do mesmo dia.
- Horário: segunda a sexta 7h às 17h (sem parada), sábado 7h às 11h, domingo fechado. Feriados de seg a sáb: horário normal do dia.
- Prazo médio de entrega: 2 a 3 dias (peças especiais podem variar).
- Pagamento: Pix, dinheiro e todos os cartões. Serviços acima de R$ 100: até 3x no cartão (confirmar com o dono antes de divulgar parcelamento para planos mensais).
- Como funciona o plano mensal: coleta semanal em dia e horário fixos (ex.: segunda 8h); na semana seguinte, no mesmo horário, devolve a roupa limpa e coleta a nova. Ciclo contínuo.
- Planos incluem roupas do dia a dia, e também peças sociais e de cama (com condições explicadas no WhatsApp — não divulgar as condições). NÃO incluem ternos, vestidos de festa, edredons etc. (são avulsos), mas assinante de plano tem desconto especial nesses itens.
- Peças excedentes no plano têm adicional; a quantidade vale por ciclo de 4 semanas e reinicia. Fidelidade de 3 ciclos (pode divulgar).
- Parcelamento em até 3x no cartão para qualquer serviço acima de R$ 100, inclusive planos.
- Empresas: orçamento/proposta enviado no mesmo dia da solicitação.
- Contagem de peças: todas as peças contam (1 par de meias = 1 peça). Fidelidade de 3 ciclos PODE ser divulgada.
- Referência para posts: 1 adulto mandando só roupa de sair/trabalho ≈ 14 peças/semana (plano 80); 1 adulto mandando toda a roupa ≈ 30/semana (plano 120). Jornada "Qual plano é o seu?" em site/qual-plano.html.
- Tabela completa de planos e pacotes (até 240 peças) em tabela-completa.md. Todas as faixas podem ser divulgadas (liberado pelo dono em 01/11/2026), inclusive as maiores, para famílias. Exceção: não divulgar 160 peças em L+D/L+P.
- Interno (não divulgar como destaque): nos serviços com passadoria, cabides limitados a 30% das peças.
- PROMOÇÃO ATIVA (desde 01/11/2026, vale em novembro e dezembro até o dono mandar parar): quem fechar qualquer plano mensal ganha a higienização grátis de 1 edredom de qualquer tamanho. Pode ser usada nos posts de planos.

## Facebook (aquecimento da Página)
- Todo post do feed do Instagram também sai na Página do Facebook (mesmo horário).
- Além disso, 1 post por dia SÓ no Facebook (itens com "tipo": "facebook" no calendario.json), em horário diferente do feed. Rodízio: seg edredom com preço; ter pacote Limpo + Dobrado; qua plano mensal da semana; qui pergunta para a comunidade de GV; sex empresas (WhatsApp 98749-0985); sáb como funciona; dom dica para salvar. Nunca repetir o tema nem a arte do feed ou do story do mesmo dia; variar o ângulo semana a semana.
- Arte: imagem gerada pelo Claude no Canva e aprovada pelo dono (ver seção "Imagens"), 1080x1350; legenda curta terminando com o link do WhatsApp.
- Posts de pergunta: o objetivo é comentário. Responder os comentários no mesmo dia.
- Stories: a API não publica story no Facebook; eles chegam à Página pelo compartilhamento automático de stories do Instagram (configurado no app).

## Imagem da peça nos posts de serviço
- Todo post de serviço de uma peça (edredom, camisa social, terno, vestido, mantas etc.) leva a imagem da peça na arte — nunca só texto e tabela.
- Preferência: foto real enviada pelo dono (peça embalada com a logo da Clean). Fotos aprovadas ficam em marca/fotos/ (edredom: marca/fotos/edredom-embalado.png).

## Imagens: o Claude gera pelo Canva e o dono só aprova (desde 08/11/2026)
- Substitui o fluxo BestContent de 03/11. O Claude gera cada imagem (feed, post exclusivo do Facebook e story) pelo conector do Canva (generate-image), no estilo aprovado "fotografia publicitária realista", e envia ao dono SOMENTE para aprovação. Autorizado pelo dono em 08/11/2026.
- LOGO (regra do dono, 08/11/2026): toda arte leva a logo OFICIAL (marca/logo-cor.png; no Canva, asset "Logo Clean oficial (cor)", media id MAHaVXGlgf4), aplicada por cima da imagem. Nunca deixar a IA desenhar a logo nem permitir variações. No prompt, pedir "sem logo e sem nenhuma marca escrita" e o canto superior esquerdo livre. Se o fundo atrás da logo for poluído, usar só um fundo branco arredondado atrás dela, sem alterar a logo.
- Montagem: copiar um design-base limpo (ex.: "Clean · feed1 · 09/11/2026 · Plano mensal 120 peças") com copy-design, trocar a imagem com update_fill e renomear "Clean · <peça> · <data> · <tema>". Nunca pedir página nova ao create-design (ele cria modelos de exemplo).
- Formatos: feed 4:5 1080x1350, logo 240x104 em top 44 / left 48; story 9:16 1080x1920 com 250 px livres no topo e 300 px embaixo, logo em top 270 / left 56.
- Stories precisam ser chamativos: selo, título grande, informação de serviço/preço e chamada (o dono reprovou em 08/11 um story só com pergunta). Enquete/caixinha: deixar área vazia para o adesivo, colocado pelo app.
- Conferir na prévia acentos, preços e telefone antes de mandar. Imagens aprovadas: salvar em posts/AAAA-MM-DD/ (feed1.jpg, story.jpg, fb-extra.jpg) em JPEG qualidade 92, commit e push.

## Prazos (confirmado pelo dono em 03/11/2026)
- Pacote avulso Limpo e Dobrado: fica PRONTO no mesmo dia. A entrega depende da próxima rota, ou o cliente pode retirar na Clean no mesmo dia. Nunca escrever "entrega em 24h" nem "entrega no mesmo dia".
- Prazo médio geral de entrega dos demais serviços: 2 a 3 dias.
