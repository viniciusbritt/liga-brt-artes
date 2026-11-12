# Kit de artes da Liga BRT

Uma ficha JSON vira PNGs prontos com um único comando. Os modelos são os que a Helo já aprovou. NÃO reescreva HTML nem o arte.py para fazer um post: copie um exemplo, mude só os textos e as fotos, e rode.

```
python3 /mnt/project-files/kit-artes/arte.py ficha.json
```
O comando leva de 2 a 6 s. Os PNGs saem em `saida` e, junto, sai `revisao.png`. **Olhe só a revisao.png.** Se precisar ajustar um texto, edite a ficha e rode de novo.

## Tipos (exemplos em `exemplos/`)
| tipo | o que gera | modelo aprovado |
|---|---|---|
| `resultado` | feed 1080×1350 | layout FIXO de 10/11 (pódio + grade 4–10 + destaque + rodapé) |
| `chamada` | feed 1080×1350 + story 1080×1920 (`<nome>-story.png`) | pré-corrida / É HOJE (foto P&B translúcida + traçado + pílulas) |
| `curiosidade` | carrossel 1080×1350, 1 PNG por slide | rebranding de 04/11 (foto real colorida em tela cheia + degradê roxo) |
| `etapa` | banner da live + tela de espera + tela de entrevistas (1920×1080) + versões `_OVERLAY` com o vídeo vazado | banner de 31/10, telas de 06/11 |

### Campos
- **resultado**: `manuscrito` (pista), `linha`, `podio` [[nome,pts]×3 na ordem P1,P2,P3], `grade` [[nome,pts]×7 = P4…P10], `destaque` [valor, texto] (opcional), `rodape` (HTML curto; `<b>` fica preto), `titulo` (opcional, padrão RESULTADO). Dados: ligabrt.com.br/etapas/<site_id> (ids em assets/t9.json).
- **chamada**: `layout` "a" (texto à esquerda) ou "b" (espelhado, texto à direita): ALTERNE a cada post. `circuito` (id do traçado, ver t9.json), `foto` + `foto_pos` (enquadramento CSS, ex. "30% 40%"; tire a marca d'água da EA do quadro), `pilula`, `manuscrito` ("Domingo é Mônaco!" / "É hoje, Mônaco!"), `pista` (use `<br>` para 2 linhas; o tamanho se ajusta sozinho), `data`, `hora`, `chamada_live`, `rodape_feed`, `rodape_story`.
- **curiosidade**: `slides` = lista. Em cada slide: `foto`, `pos`, `espelhar`, e os blocos de cima para baixo: `pilula`, `manuscrito_antes`, `titulo` (+`titulo_tam`, `titulo_alt`), `manuscrito`, `linhas` [[texto, valor]] (pílulas alternando branco e preto), `texto`, `live` (pílula com ▶), `siga` (true), `cta` (pílula no canto, ex. "QUEM? ARRASTA →"), `base` (distância do fundo). O contador 01/03 é automático. A capa precisa de GANCHO emocional, nunca de título genérico.
- **etapa**: `etapa` (número; pista, local, circuito e data vêm de assets/t9.json), `data_arquivo` (AAAA-MM-DD), `manuscrito`, `pista_arquivo` (para o nome do arquivo), `foto_banner`, `foto_espera`, `foto_entrevistas` (+ `pos_*`). Nomes de saída: `AAAA-MM-DD_Capa-Live_T9-Etapa-N_<Pista>.png` etc. CORINGA: preencha pista/local/circuito no t9.json quando a pista for sorteada.

## Fotos
`/mnt/project-files/fotos/indice.png` = miniaturas de TODAS as fotos com o caminho. Olhe só ela para escolher a foto, sem abrir uma por uma. Varie a foto de semana para semana. Foto nova do Drive (pasta 1I_ccehGo3Dy5XRVBupCAMgMxZmzvJKyO): baixe para fotos/drive/ e rode de novo o bloco que gera o indice.png (está no fim deste arquivo).

## Depois de gerar
1. Repositório `viniciusbritt/liga-brt-artes`, branch **main**: copie os PNGs para `<AAAA-MM-DD>-<nome>/` (pacote da etapa: `banners-live/`, `tela-espera/`, `tela-entrevistas/`), depois commit e push. URL do Buffer: `https://raw.githubusercontent.com/viniciusbritt/liga-brt-artes/main/<pasta>/<arquivo>`.
2. Banner da semana: sobrescreva também `banners-live/capa-live-atual.png` no main **e** no branch `claude/project-thread-r0cbb1`, porque o link fixo que o narrador já tem aponta para esse branch.
3. Buffer: SOMENTE o canal @liga_brt `6ae2bd2c2f1f5ed648084ca2` (org `6ae2bc4082663d76d494c180`). Confira se o post já está agendado e se o limite de 10 agendados no canal permite.
4. Texto de WhatsApp para cada post de feed ou Reels, no modelo abaixo.

## Texto de WhatsApp (modelo fixo, só o texto, pronto para copiar)
```
🟣 <GANCHO EM CAIXA ALTA> <emoji>

<2–3 linhas contando o post, com um detalhe que dê vontade de ver + pergunta para o público>

👉 <link do post; enquanto estiver agendado: https://www.instagram.com/liga_brt/>

E a emoção continua: a Etapa <N> é em <PISTA>, domingo (<dd/mm>), às 20h, ao vivo no YouTube. Ativa o lembrete e chama a galera pra assistir junto 🏁
📺 https://www.youtube.com/@LIGABRT/featured
```

## Arte especial (fora dos 4 tipos)
Só para posts novos de verdade (lançamento, inscrições, ideia nova). Parta do HTML mais parecido em `posts/` e reaproveite `arte.py` (funções `cacos`, `tracado`, `pagina`, `render`). Se o formato for se repetir, transforme-o num tipo novo do kit.

## Regerar o índice de fotos
```
cd /mnt/project-files && python3 -c "
from PIL import Image,ImageDraw;import glob
fs=sorted(glob.glob('fotos/drive/*.png'))+['fotos/6979.png','fotos/bahrein-pelotao.jpg','fotos/williams-paisagem.jpg','tela-entrevistas/foto.png']
th=[]
for f in fs:
 i=Image.open(f).convert('RGB');i.thumbnail((480,270));c=Image.new('RGB',(480,300),'#111');c.paste(i);ImageDraw.Draw(c).text((6,276),f,fill='white');th.append(c)
S=Image.new('RGB',(4*488,((len(th)+3)//4)*308))
[S.paste(t,((k%4)*488,(k//4)*308)) for k,t in enumerate(th)];S.save('fotos/indice.png')"
```
Requisitos: python3 + Pillow, node + playwright (Chromium), Google Fonts liberado.
