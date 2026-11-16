# Minha pequena linguagem

Trabalho semestral de **Compiladores** — Ciência da Computação, UNISAGRADO.
Prof. Luiz Ricardo Mantovani da Silva · 2026-2

Cada grupo escreve um **compilador completo** para a MPL, uma linguagem
pequena de palavras-chave em português. O compilador de vocês vai ler um
programa em `.mpl`, atravessar as quatro fases da disciplina e produzir um
arquivo que **roda de verdade** numa máquina virtual que vocês também vão
escrever.

No fim do semestre vocês executam um programa escrito por vocês, numa
linguagem compilada por vocês.

---

## Comece por aqui

```bash
git clone https://github.com/LuizRMSilva1973/compiladores-lab.git
cd compiladores-lab
```

```bash
make verificar E=1
```

Vai dar vermelho — é para dar. O esqueleto responde à linha de comando mas
ainda não tem nenhuma fase escrita. O vermelho é o seu ponto de partida, e
ele vai virando verde conforme vocês preenchem `mplc/`.

Não precisa instalar nada além do Python 3. Se o notebook de vocês der
trabalho, o [Google Cloud Shell](https://shell.cloud.google.com) já vem com
Python 3.12, Java 21 e git — e é o mesmo ambiente da correção.

---

## Os três documentos que mandam

| Arquivo | O que decide |
|---|---|
| [LINGUAGEM.md](LINGUAGEM.md) | **o que** o compilador aceita: a sintaxe e as regras de tipo da MPL |
| [CONTRATOS.md](CONTRATOS.md) | **como** ele se comunica: a linha de comando e o formato de cada despejo |
| [entregas/](entregas/) | o enunciado de cada entrega, com o que vale nota |

Quando a sua intuição discordar de um deles, é o arquivo que vale. Se o
arquivo estiver errado, me procurem — já aconteceu de eu escrever um exemplo
errado no contrato e só descobrir rodando.

---

## As entregas

| # | Entrega | Turma A (quarta) | Turma B (segunda) | Vale |
|---|---|---|---|---|
| [E1](entregas/E1.md) | Analisador léxico | 02/09 | 31/08 | 0,8 |
| [E2](entregas/E2.md) | Analisador sintático e árvore | 30/09 | 28/09 | 1,2 |
| [E3](entregas/E3.md) | Tabela de símbolos e tipos | 28/10 | 26/10 | 1,2 |
| [E4](entregas/E4.md) | Código intermediário, geração e VM | 18/11 | 16/11 | 1,8 |
| [Apres.](entregas/APRESENTACAO.md) | Demonstração e defesa | 25/11 | 23/11 | 1,0 |

São **quatro entregas sobre o mesmo compilador**, não quatro trabalhos. O que
vocês escreverem na E1 continua rodando na E4 — e o verificador da E4 confere
tudo o que veio antes. Deixar a E1 pela metade custa caro em novembro.

---

## Regras do jogo

**A entrega é o repositório, nunca a máquina de vocês.** A correção clona o
repositório numa máquina limpa e roda `make verificar E=n`. Se não passar
lá, não conta como entregue. Testem antes de entregar — de preferência na
Cloud Shell, que é o ambiente da correção.

**Grupos de até 3.** O mesmo grupo do começo ao fim. Mudança de grupo só até
a E1.

**Gerador de parser proibido nas Entregas 1 e 2.** ANTLR, PLY, yacc, lark e
parentes escondem exatamente a parte que está sendo ensinada. Da E3 em diante
o assunto é outro, e aí não faz diferença. Na apresentação vocês podem — e
devem — comparar o parser de vocês com o que um gerador produziria.

**A linguagem de implementação é de vocês, entre as que o ambiente da correção
já tem:** Python 3.12, Java 21, C e C++ (gcc 13), Ruby 3.2 ou PHP 8.3. O
verificador não olha para dentro — ele roda `./compilar` e `./executar` e
compara o que sai. O esqueleto em `mplc/` é Python porque é o caminho mais
curto, mas ninguém é obrigado a usá-lo.

A lista existe por um motivo prático: a correção roda numa Cloud Shell limpa, e
o que não estiver lá não roda. Querem outra linguagem? Falem comigo **antes** de
começar — o critério é ela existir no ambiente sem instalação. Em nenhum caso
dependam de biblioteca externa: só a biblioteca padrão.

**Escrever o compilador é a tarefa.** Usar IA para explicar um conceito,
revisar uma mensagem de erro ou entender um trecho é bem-vindo, e eu faço
isso também. Entregar um compilador que vocês não sabem alterar é outra
coisa — e a apresentação foi desenhada para separar os dois casos: cada grupo
recebe **uma alteração pequena na linguagem, na hora, com 10 minutos para
fazer**. Quem escreveu o compilador faz. Não é desconfiança; é o formato.

---

## O verificador

```bash
make verificar E=2      # confere a Entrega 2 e, junto, a 1
make verificar          # confere as quatro
make evidencias E=2     # grava evidencias/verificacao-2.txt, que vai na entrega
```

**Antes de entregar, rodem `make prova`.** Ele clona o repositório de vocês num
diretório limpo e verifica lá — que é exatamente o que a correção faz. É o
teste que pega o defeito mais comum de todos, e que não tem nada a ver com
compiladores: *funciona aqui e não no clone*. Arquivo esquecido fora do commit,
caminho absoluto, passo de compilação que ninguém roda. Vale para qualquer
linguagem, e é a única prova que realmente antecipa a correção.

Ele não lê o código de vocês. Ele roda o compilador e compara a saída com um
corpus de **10 programas válidos**, **26 programas que precisam ser
recusados na compilação** e **3 que precisam falhar na execução** — com a
fase e a linha do erro conferidas.

Os programas recusados são metade da nota escondida do trabalho. Um
compilador que aceita tudo passa em todos os testes positivos e não vale
nada: é por isso que o corpus tem mais programas errados do que certos.

**A correção usa um segundo corpus, que vocês não têm.** Mesma linguagem,
mesmas regras, programas diferentes. Um compilador de verdade passa nos dois
sem que vocês precisem fazer nada; um programa que apenas reproduza as saídas
esperadas deste corpus passa aqui e reprova lá. Estou dizendo isto abertamente
para ninguém perder tempo pelo caminho errado.

---

## Como entregar

1. `git push` no repositório do grupo.
2. Abram a [página do trabalho](https://profluiz.mantovanitec.com/disciplinas/aulas/compiladores/trabalho.html).
3. No formulário do fim da página: escolham a entrega, identifiquem os
   integrantes (nome, RA e e-mail), colem a URL do repositório e anexem o
   `evidencias/verificacao-N.txt`.
4. Cada integrante recebe uma cópia por e-mail. **Guardem esse e-mail**: é o
   comprovante.


## Gramática Sintática da MPL (Entrega #2)

```ebnf
programa       = { funcao } ;
funcao         = "funcao", tipo_retorno, ID, "(", [ parametros ], ")", bloco ;
parametros     = parametro, { ",", parametro } ;
parametro      = tipo, ID ;
tipo_retorno   = tipo | "vazio" ;
tipo           = "inteiro" | "real" | "logico" | "texto" ;

bloco          = "{", { comando }, "}" ;
comando        = declaracao | atribuicao | chamada, ";"
               | condicional | repeticao | escrita | retorno | bloco ;
declaracao     = tipo, ID, [ "=", expressao ], ";" ;
atribuicao     = ID, "=", expressao, ";" ;
condicional    = "se", "(", expressao, ")", bloco,
                 [ "senao", bloco ] ;
repeticao      = "enquanto", "(", expressao, ")", bloco ;
escrita        = "escreva", "(", expressao, ")", ";" ;
retorno        = "retorne", [ expressao ], ";" ;
chamada        = ID, "(", [ argumentos ], ")" ;
argumentos     = expressao, { ",", expressao } ;

expressao      = disjuncao ;
disjuncao      = conjuncao, { "ou", conjuncao } ;
conjuncao      = igualdade, { "e", igualdade } ;
igualdade      = relacional, { ( "==" | "!=" ), relacional } ;
relacional     = aditiva, { ( "<" | "<=" | ">" | ">=" ), aditiva } ;
aditiva        = multiplicativa, { ( "+" | "-" ), multiplicativa } ;
multiplicativa = unaria, { ( "*" | "/" | "%" ), unaria } ;
unaria         = ( "nao" | "-" ), unaria | primaria ;
primaria       = INTEIRO | REAL | LOGICO | TEXTO | chamada | ID
               | "(", expressao, ")" ;
```

A precedência é codificada pelas produções encadeadas de `disjuncao` até
`primaria`: cada nível chama o seguinte, mais forte. Os operadores binários
são acumulados da esquerda para a direita; os unários chamam `unaria` de
forma recursiva à direita.

## Tabela de Tokens da Linguagem MPL (Entrega #1)

| Tipo de Token | Exemplo / Lexema | Descrição |
| :--- | :--- | :--- |
| `FUNCAO`, `INTEIRO`, `REAL`, `TEXTO`, `BOOLEANO`, `VAZIO`, `SE`, `SENAO`, `ENQUANTO`, `RETORNE`, `VERDADEIRO`, `FALSO` | `funcao`, `inteiro`, `se`, ... | Palavras reservadas da linguagem MPL. |
| `ID` | `fatorial`, `n`, `i`, `principal` | Identificadores de variáveis e funções. |
| `LITERAL_INTEIRO` | `1`, `42`, `100` | Números inteiros. |
| `LITERAL_REAL` | `3.14`, `0.5` | Números com parte decimal. |
| `LITERAL_TEXTO` | `"exemplo"` | Cadeia de caracteres delimitada por aspas duplas (com suporte a escapes `\n`, `\t`, `\"`, `\\`). |
| `MENOR_IGUAL`, `MAIOR_IGUAL`, `IGUAL`, `DIFERENTE` | `<=`, `>=`, `==`, `!=` | Operadores relacionais compostos (reconhecidos com prioridade). |
| `MAIS`, `MENOS`, `VEZES`, `DIVISAO`, `RESTO`, `ATRIBUICAO`, `MENOR`, `MAIOR`, `NAO` | `+`, `-`, `*`, `/`, `%`, `=`, `<`, `>`, `!` | Operadores aritméticos, relacionais e lógicos simples. |
| `VIRGULA`, `PONTO_VIRGULA`, `ABRE_PAR`, `FECHA_PAR`, `ABRE_CHAVE`, `FECHA_CHAVE`, `ABRE_COLCHETE`, `FECHA_COLCHETE` | `,`, `;`, `(`, `)`, `{`, `}`, `[`, `]` | Símbolos e delimitadores. |
| `FIM_ARQUIVO` | `""` | Marcador de término do código-fonte. |


## Tabela de Tokens — Entrega 1

O analisador léxico reconhece os seguintes tokens:

| Token           | Reconhece                                                  |
| --------------- | ---------------------------------------------------------- |
| `FUNCAO`        | `funcao`                                                   |
| `RETORNE`       | `retorne`                                                  |
| `SE`            | `se`                                                       |
| `SENAO`         | `senao`                                                    |
| `ENQUANTO`      | `enquanto`                                                 |
| `ESCREVA`       | `escreva`                                                  |
| `TIPO_INTEIRO`  | `inteiro`                                                  |
| `TIPO_REAL`     | `real`                                                     |
| `TIPO_LOGICO`   | `logico`                                                   |
| `TIPO_TEXTO`    | `texto`                                                    |
| `TIPO_VAZIO`    | `vazio`                                                    |
| `LOGICO`        | `verdadeiro` e `falso`                                     |
| `E`             | `e`                                                        |
| `OU`            | `ou`                                                       |
| `NAO`           | `nao`                                                      |
| `ID`            | Identificadores, como `x`, `contador`, `valor10` e `_temp` |
| `INTEIRO`       | Números inteiros, como `10`, `0` e `123`                   |
| `REAL`          | Números reais, como `3.14` e `10.5`                        |
| `TEXTO`         | Textos entre aspas, como `"Ola"`                           |
| `MAIS`          | `+`                                                        |
| `MENOS`         | `-`                                                        |
| `VEZES`         | `*`                                                        |
| `DIVIDE`        | `/`                                                        |
| `RESTO`         | `%`                                                        |
| `IGUAL`         | `==`                                                       |
| `DIFERENTE`     | `!=`                                                       |
| `MENOR`         | `<`                                                        |
| `MENOR_IGUAL`   | `<=`                                                       |
| `MAIOR`         | `>`                                                        |
| `MAIOR_IGUAL`   | `>=`                                                       |
| `ATRIBUI`       | `=`                                                        |
| `ABRE_PAR`      | `(`                                                        |
| `FECHA_PAR`     | `)`                                                        |
| `ABRE_CHAVE`    | `{`                                                        |
| `FECHA_CHAVE`   | `}`                                                        |
| `VIRGULA`       | `,`                                                        |
| `PONTO_VIRGULA` | `;`                                                        |
| `FIM_ARQUIVO`   | Indica o final do arquivo                                  |

O analisador também ignora espaços em branco e comentários dos tipos `// comentario` e `/* comentario */`.

Para operadores compostos, como `<=`, `>=`, `==` e `!=`, a análise é feita antes dos operadores de um único caractere, evitando que `<=`, por exemplo, seja interpretado como `<` seguido de `=`.

## Escopos na tabela de símbolos (Entrega #3)

Cada escopo é um objeto `Escopo` com um dicionário de símbolos (que preserva a
ordem de declaração) e um ponteiro para o escopo pai — ou seja, um
**dicionário encadeado**, percorrido como uma **pilha** durante a análise: ao
abrir um bloco o escopo atual passa a ser o novo, ao fechar volta para o pai.
A busca de um nome sobe a cadeia de pais, então o sombreamento sai de graça: o
escopo mais interno que tem o nome vence. Escolhemos isso porque nenhum escopo
é descartado ao fechar — todos ficam numa lista na ordem em que abriram, que é
exatamente o que o `--tabela` precisa despejar e o que a Entrega 4 usa para
dar a cada variável o seu lugar no registro de ativação (variáveis sombreadas
viram `x.2`, `x.3`, … no código intermediário, com o número do escopo).

A análise faz duas passadas: a primeira só coleta as assinaturas das funções
(para permitir chamar uma função antes dela aparecer no arquivo); a segunda
percorre os corpos, confere os tipos e marca na árvore onde entra a conversão
`inteiro` → `real`.

## Código intermediário, `.mplb` e VM (Entrega #4)

```
fonte .mpl → árvore → tabela → três endereços (--ir) → .mplb (texto) → VM
```

**Três endereços** (`./compilar --ir programa.mpl`): no máximo um operador por
linha, com temporários `t0, t1, …` e rótulos `L0, L1, …`. Exemplo do fatorial:

```
funcao fatorial inteiro (n inteiro)
  t0 = n <= 1
  seFalso t0 desvie L0
  retorne 1
  desvie L1
L0:
  t1 = n - 1
  param t1
  t2 = chama fatorial, 1
  t3 = n * t2
  retorne t3
L1:
fim
```

**O `.mplb`** é texto, uma instrução por linha, para uma **máquina de pilha**.
Cada função vira um bloco `.funcao <nome> <nº parâmetros> <nº locais>` …
`.fim`; as linhas `.local <posição> <nome>` só documentam de onde veio cada
posição. Parâmetros, variáveis e temporários são posições `0, 1, 2…` do
**registro de ativação** da chamada (os parâmetros ocupam as primeiras).
Cada instrução de três endereços vira poucas de pilha — `t3 = n * t2` vira
`CARREGA 0`, `CARREGA 2`, `MULTIPLICA`, `GUARDA 3`.

**A VM** (`mplc/vm.py`) é um laço, não uma função recursiva: tem uma pilha de
operandos e uma pilha de registros de ativação. Cada `CHAMA` cria um registro
novo, com os **seus** locais, o seu ponto de execução e a linha do comando que
está rodando — é isso que faz a recursão funcionar. Divisão/resto por zero e
mais de 100 000 chamadas ativas (estouro de pilha) viram `erro execucao` na
linha do comando, com código de saída 2.

### Conjunto de instruções da VM

Notação: `… a b → … r` significa que a instrução tira `b` (topo) e `a` da
pilha de operandos e empilha `r`.

| Instrução | O que faz com a pilha |
|---|---|
| `EMPILHA_INTEIRO n` | `… → … n` — empilha o inteiro `n` |
| `EMPILHA_REAL x` | `… → … x` — empilha o real `x` |
| `EMPILHA_LOGICO v` | `… → … v` — empilha `verdadeiro` ou `falso` |
| `EMPILHA_TEXTO "s"` | `… → … s` — empilha o texto (escapes `\n \t \" \\` interpretados) |
| `CARREGA i` | `… → … local[i]` — empilha a posição `i` do registro de ativação atual |
| `GUARDA i` | `… v → …` — desempilha e grava na posição `i` do registro atual |
| `SOMA` | `… a b → … a+b` — soma números ou concatena textos |
| `SUBTRAI` | `… a b → … a-b` |
| `MULTIPLICA` | `… a b → … a*b` |
| `DIVIDE` | `… a b → … a/b` — entre inteiros, truncada em direção a zero; `b = 0` é erro de execução |
| `RESTO` | `… a b → … a%b` — com o sinal do dividendo (`-7 % 3 = -1`); `b = 0` é erro de execução |
| `NEGA` | `… a → … -a` — menos unário |
| `IGUAL` | `… a b → … (a == b)` |
| `DIFERENTE` | `… a b → … (a != b)` |
| `MENOR` | `… a b → … (a < b)` |
| `MENOR_IGUAL` | `… a b → … (a <= b)` |
| `MAIOR` | `… a b → … (a > b)` |
| `MAIOR_IGUAL` | `… a b → … (a >= b)` |
| `E` | `… a b → … (a e b)` — os dois lados já foram avaliados (sem curto-circuito) |
| `OU` | `… a b → … (a ou b)` |
| `NAO` | `… a → … (nao a)` |
| `PARA_REAL` | `… a → … real(a)` — a conversão implícita `inteiro` → `real` |
| `DESVIA L` | `… → …` — continua no rótulo `L` |
| `DESVIA_SE_FALSO L` | `… c → …` — desempilha `c`; se for `falso`, continua no rótulo `L` |
| `CHAMA f n` | `… a1 … an → …` — desempilha os `n` argumentos para os locais `0..n-1` de um registro de ativação novo e passa a executar `f` |
| `RETORNA` | `… v → … v` — descarta o registro atual e volta para quem chamou; o valor `v` fica no topo para o chamador |
| `RETORNA_VAZIO` | `… → …` — descarta o registro atual e volta para quem chamou, sem valor |
| `ESCREVA` | `… v → …` — desempilha e imprime no formato da seção 4.5 (`real` com 6 casas, `logico` como `verdadeiro`/`falso`) |
| `LINHA l c` | `… → …` — não mexe na pilha; registra a linha/coluna do comando atual, usada nas mensagens de erro de execução |

A execução começa por `principal` e termina quando ela retorna.

### Programa do grupo

[`exemplos/vitrine.mpl`](exemplos/vitrine.mpl) resolve quatro problemas
clássicos — Torre de Hanói (recursão em função `vazio`), raiz quadrada pelo
método de Newton (`real` e conversão de `inteiro`), números em binário
(recursão que devolve `texto`) e a sequência de Collatz (laços e escopos
aninhados). A saída esperada está em
[`exemplos/vitrine.saida`](exemplos/vitrine.saida).

```bash
./compilar exemplos/vitrine.mpl && ./executar exemplos/vitrine.mplb
```
