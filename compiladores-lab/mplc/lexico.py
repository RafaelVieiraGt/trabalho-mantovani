"""
Entrega 1 — análise léxica.

Transformar o texto do programa numa lista de tokens.

O que vocês têm que devolver: uma lista de Token. O último elemento é sempre
um token FIM_ARQUIVO. A regra de posição dele está em CONTRATOS.md, seção 7.

Leiam antes: LINGUAGEM.md seção 2, e CONTRATOS.md seção 2.
"""

from mplc.erros import ErroLexico

# Mapeamento de palavras reservadas para os tipos de token conforme CONTRATOS.md
PALAVRAS_RESERVADAS = {
    'funcao': 'FUNCAO',
    'inteiro': 'INTEIRO',
    'real': 'REAL',
    'texto': 'TEXTO',
    'booleano': 'BOOLEANO',
    'vazio': 'VAZIO',
    'se': 'SE',
    'senao': 'SENAO',
    'enquanto': 'ENQUANTO',
    'retorne': 'RETORNE',
    'verdadeiro': 'VERDADEIRO',
    'falso': 'FALSO',
}


class Token:
    __slots__ = ('tipo', 'lexema', 'linha', 'coluna')

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo          # 'ID', 'INTEIRO', 'MAIS', ... (a lista está no contrato)
        self.lexema = lexema      # o texto exato como apareceu no fonte
        self.linha = linha
        self.coluna = coluna      # a coluna do PRIMEIRO caractere do token

    def __str__(self):
        # esta é a linha que o --tokens imprime; não mexam no formato
        return f"{self.linha},{self.coluna},{self.tipo},{self.lexema}"


def analisar(fonte):
    """Recebe o texto do programa. Devolve a lista de Token."""
    pos = 0
    linha = 1
    coluna = 1
    tam = len(fonte)
    tokens = []

    def char_atual():
        return fonte[pos] if pos < tam else None

    def espiar_proximo():
        return fonte[pos + 1] if pos + 1 < tam else None

    def avancar():
        nonlocal pos, linha, coluna
        ch = fonte[pos]
        pos += 1
        if ch == '\n':
            linha += 1
            coluna = 1
        else:
            coluna += 1
        return ch

    while pos < tam:
        ch = char_atual()

        # 1. Espaços em branco
        if ch in ' \t\r\n':
            avancar()
            continue

        # 2. Comentários
        if ch == '/':
            prox = espiar_proximo()
            if prox == '/':  # Comentário de linha (//)
                avancar()
                avancar()
                while pos < tam and char_atual() != '\n':
                    avancar()
                continue
            elif prox == '*':  # Comentário de bloco (/* ... */)
                lin_ini, col_ini = linha, coluna
                avancar()
                avancar()
                fechado = False
                while pos < tam:
                    if char_atual() == '*' and espiar_proximo() == '/':
                        avancar()
                        avancar()
                        fechado = True
                        break
                    avancar()
                if not fechado:
                    raise ErroLexico("comentário não fechado", lin_ini, col_ini)
                continue

        # 3. Identificadores e Palavras Reservadas
        if ch.isalpha() or ch == '_':
            lin_ini, col_ini = linha, coluna
            lexema = ""
            while pos < tam and (char_atual().isalnum() or char_atual() == '_'):
                lexema += avancar()

            tipo = PALAVRAS_RESERVADAS.get(lexema, 'ID')
            tokens.append(Token(tipo, lexema, lin_ini, col_ini))
            continue

        # 4. Números (INTEIRO e REAL)
        if ch.isdigit():
            lin_ini, col_ini = linha, coluna
            lexema = ""
            eh_real = False

            while pos < tam and char_atual().isdigit():
                lexema += avancar()

            if pos < tam and char_atual() == '.':
                if espiar_proximo() and espiar_proximo().isdigit():
                    eh_real = True
                    lexema += avancar()  # consome o '.'
                    while pos < tam and char_atual().isdigit():
                        lexema += avancar()

            tipo = 'LITERAL_REAL' if eh_real else 'LITERAL_INTEIRO'
            tokens.append(Token(tipo, lexema, lin_ini, col_ini))
            continue

        # 5. Cadeia de Texto (TEXTO) com tratamentos de escape
        if ch == '"':
            lin_ini, col_ini = linha, coluna
            avancar()  # consome aspas de abertura
            lexema = ""
            fechado = False

            while pos < tam:
                atual = char_atual()
                if atual == '"':
                    avancar()  # consome aspas de fechamento
                    fechado = True
                    break
                elif atual == '\\':
                    avancar()
                    escapado = char_atual()
                    if escapado == 'n':
                        lexema += '\n'
                    elif escapado == 't':
                        lexema += '\t'
                    elif escapado == '"':
                        lexema += '"'
                    elif escapado == '\\':
                        lexema += '\\'
                    else:
                        raise ErroLexico(f"sequência de escape inválida '\\{escapado}'", linha, coluna)
                    avancar()
                elif atual == '\n':
                    raise ErroLexico("cadeia de texto não fechada", lin_ini, col_ini)
                else:
                    lexema += avancar()

            if not fechado:
                raise ErroLexico("cadeia de texto não fechada", lin_ini, col_ini)

            tokens.append(Token('LITERAL_TEXTO', lexema, lin_ini, col_ini))
            continue

        # 6. Operadores Compostos (<=, >=, ==, !=) — Armadilha do <= evitada
        lin_ini, col_ini = linha, coluna
        prox = espiar_proximo()
        duplo = ch + (prox if prox else "")

        op_duplos = {
            '<=': 'MENOR_IGUAL',
            '>=': 'MAIOR_IGUAL',
            '==': 'IGUAL',
            '!=': 'DIFERENTE'
        }

        if duplo in op_duplos:
            avancar()
            avancar()
            tokens.append(Token(op_duplos[duplo], duplo, lin_ini, col_ini))
            continue

        # 7. Operadores Simples e Símbolos
        simbolos_simples = {
            '+': 'MAIS',
            '-': 'MENOS',
            '*': 'VEZES',
            '/': 'DIVISAO',
            '%': 'RESTO',
            '=': 'ATRIBUICAO',
            '<': 'MENOR',
            '>': 'MAIOR',
            '!': 'NAO',
            ',': 'VIRGULA',
            ';': 'PONTO_VIRGULA',
            '(': 'ABRE_PAR',
            ')': 'FECHA_PAR',
            '{': 'ABRE_CHAVE',
            '}': 'FECHA_CHAVE',
            '[': 'ABRE_COLCHETE',
            ']': 'FECHA_COLCHETE'
        }

        if ch in simbolos_simples:
            avancar()
            tokens.append(Token(simbolos_simples[ch], ch, lin_ini, col_ini))
            continue

        # Caractere não reconhecido
        raise ErroLexico(f"caractere inválido '{ch}'", linha, coluna)

    # 8. Token de Fim de Arquivo (FIM_ARQUIVO) conforme CONTRATOS.md
    tokens.append(Token('FIM_ARQUIVO', '', linha, coluna))
    return tokens