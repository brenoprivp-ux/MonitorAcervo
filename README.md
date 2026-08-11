# Ranking de Mídias — Bot de Telegram

Conta quantas fotos e vídeos cada pessoa envia no grupo e posta um ranking
automaticamente a cada 48 horas. A contagem é **acumulada** (nunca zera sozinha).

> ⚠️ O bot só consegue contar mídias enviadas a partir do momento em que ele
> está rodando no grupo — o Telegram não permite que bots leiam o histórico
> de mensagens antigas. A contagem começa do zero quando você ligar o bot.

## O que aparece no ranking

- Colocação (🥇🥈🥉 ou "Nº")
- `@usuario` (ou nome, se a pessoa não tiver @)
- Número de fotos
- Número de vídeos
- Total

## Comandos

- `/ranking` — mostra o ranking atual a qualquer momento.
- `/resetranking` — zera os contadores manualmente, se você quiser recomeçar do zero um dia.

## Já está configurado

O arquivo `.env` já vem com seu token e o ID do grupo preenchidos. Não precisa mexer em nada.

## Rodando localmente (no seu computador)

1. Instale o Python (3.10 ou mais recente) se ainda não tiver.
2. Abra um terminal dentro da pasta `media_ranking_bot`.
3. Rode:

```bash
pip install -r requirements.txt
python bot.py
```

4. Pronto — o bot vai ficar rodando e escutando o grupo. Pra ele continuar
   funcionando 24h, o computador precisa ficar ligado (ou use o deploy no
   Railway abaixo, que é mais prático).

## Deploy no Railway (recomendado, fica rodando sozinho na nuvem)

1. Crie uma conta grátis em [railway.app](https://railway.app).
2. Suba esta pasta para um repositório novo no GitHub
   **(NÃO suba o arquivo `.env` — ele já está no `.gitignore`, então o
   GitHub vai ignorá-lo sozinho)**.
3. No Railway: **New Project** → **Deploy from GitHub repo** → escolha o repositório.
4. Vá em **Variables** e adicione manualmente (copiando do seu `.env` local):
   - `BOT_TOKEN` = 8932480321:AAFaCRifM27RWEf6ds38Twke0wIpimlkWKQ
   - `GROUP_CHAT_ID` = -1004332387153
5. O Railway instala tudo sozinho e roda o bot (usa o `Procfile` incluso).

> Obs: como o token já está exposto nesta conversa, se você já vai apagá-la
> como comentou, tudo certo. Mas se algum dia desconfiar que o token vazou
> (por exemplo, se subiu o `.env` sem querer pro GitHub), gere um novo token
> no @BotFather com `/revoke` e atualize a variável.

## Testando

1. Adicione o bot no grupo (com Group Privacy desativado no BotFather).
2. Mande uma foto e um vídeo no grupo.
3. Digite `/ranking` — deve aparecer o placar.
4. Depois é só esperar: a cada 48h o ranking aparece sozinho.
