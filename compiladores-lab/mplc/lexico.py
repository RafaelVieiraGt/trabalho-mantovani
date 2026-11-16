"""
Entrega 1 — analise lexica.

Transformar o texto do programa numa lista de tokens.

O que voces tem que devolver: uma lista de Token. O ultimo elemento e sempre
um token FIM_ARQUIVO. A regra de posicao dele esta em CONTRATOS.md, secao 7.

Leiam antes: LINGUAGEM.md secao 2, e CONTRATOS.md secao 2.
"""

from mplc.erros import ErroMPL


class Token:
    __slots__ = ('tipo', 'lexema', 'linha', 'coluna')

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"{self.linha},{self.coluna},{self.tipo},{self.lexema}"


# ============================================================
# PALAVRAS RESERVADAS
# ============================================================

PALAVRAS_RESERVADAS = {
    'funcao': 'FUNCAO',
    'retorne': 'RETORNE',
    'se': 'SE',
    'senao': 'SENAO',
    'enquanto': 'ENQUANTO',
    'escreva': 'ESCREVA',

    'inteiro': 'TIPO_INTEIRO',
    'real': 'TIPO_REAL',
    'logico': 'TIPO_LOGICO',
    'texto': 'TIPO_TEXTO',
    'vazio': 'TIPO_VAZIO',

    'verdadeiro': 'LOGICO',
    'falso': 'LOGICO',

    'e': 'E',
    'ou': 'OU',
    'nao': 'NAO',
}


# ============================================================
# OPERADORES
# IMPORTANTE: operadores de 2 caracteres devem ser testados
# antes dos operadores de 1 caractere.
# ============================================================

OPERADORES_DOIS = {
    '==': 'IGUAL',
    '!=': 'DIFERENTE',
    '<=': 'MENOR_IGUAL',
    '>=': 'MAIOR_IGUAL',
}


OPERADORES_UM = {
    '+': 'MAIS',
    '-': 'MENOS',
    '*': 'VEZES',
    '/': 'DIVIDE',
    '%': 'RESTO',

    '<': 'MENOR',
    '>': 'MAIOR',
    '=': 'ATRIBUI',

    '(': 'ABRE_PAR',
    ')': 'FECHA_PAR',
    '{': 'ABRE_CHAVE',
    '}': 'FECHA_CHAVE',
    ',': 'VIRGULA',
    ';': 'PONTO_VIRGULA',
}


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

def eh_letra(c):
    """
    Identificadores podem comecar com:
    a-z, A-Z ou _
    """
    return (
        ('a' <= c <= 'z')
        or ('A' <= c <= 'Z')
        or c == '_'
    )


def eh_digito(c):
    return '0' <= c <= '9'


def eh_identificador(c):
    """
    Depois do primeiro caractere, identificadores aceitam:
    letras, digitos e _
    """
    return eh_letra(c) or eh_digito(c)


# ============================================================
# ANALISADOR LEXICO
# ============================================================

def analisar(fonte):
    """Recebe o texto do programa. Devolve a lista de Token."""

    tokens = []

    i = 0
    linha = 1
    coluna = 1

    tamanho = len(fonte)

    while i < tamanho:

        c = fonte[i]

        # ====================================================
        # 1. ESPACOS
        # ====================================================

        if c in (' ', '\t', '\r'):
            i += 1
            coluna += 1
            continue

        # Quebra de linha
        if c == '\n':
            i += 1
            linha += 1
            coluna = 1
            continue

        # ====================================================
        # 2. COMENTARIO DE UMA LINHA
        #
        # // comentario
        # ====================================================

        if (
            c == '/'
            and i + 1 < tamanho
            and fonte[i + 1] == '/'
        ):
            i += 2
            coluna += 2

            while i < tamanho and fonte[i] != '\n':
                i += 1
                coluna += 1

            continue

        # ====================================================
        # 3. COMENTARIO DE BLOCO
        #
        # /*
        #    comentario
        # */
        # ====================================================

        if (
            c == '/'
            and i + 1 < tamanho
            and fonte[i + 1] == '*'
        ):

            linha_inicio = linha
            coluna_inicio = coluna

            i += 2
            coluna += 2

            fechado = False

            while i < tamanho:

                # Encontrou */
                if (
                    fonte[i] == '*'
                    and i + 1 < tamanho
                    and fonte[i + 1] == '/'
                ):
                    i += 2
                    coluna += 2
                    fechado = True
                    break

                # Comentario pode atravessar linhas
                if fonte[i] == '\n':
                    i += 1
                    linha += 1
                    coluna = 1

                else:
                    i += 1
                    coluna += 1

            # Chegou ao final sem encontrar */
            if not fechado:
                raise ErroMPL(
                    'lexico',
                    linha_inicio,
                    coluna_inicio,
                    'comentario de bloco nao foi fechado'
                )

            continue

        # ====================================================
        # 4. LITERAL DE TEXTO
        #
        # "ola"
        # "linha\n"
        # ====================================================

        if c == '"':

            inicio_i = i

            linha_inicio = linha
            coluna_inicio = coluna

            # Pula a primeira "
            i += 1
            coluna += 1

            fechado = False

            while i < tamanho:

                c = fonte[i]

                # Texto nao pode atravessar linha
                if c == '\n' or c == '\r':

                    raise ErroMPL(
                        'lexico',
                        linha_inicio,
                        coluna_inicio,
                        'texto nao foi fechado'
                    )

                # Encontrou a aspa final
                if c == '"':

                    i += 1
                    coluna += 1

                    fechado = True
                    break

                # ============================================
                # ESCAPES
                #
                # permitidos:
                # \n
                # \t
                # \"
                # \\
                # ============================================

                if c == '\\':

                    coluna_escape = coluna

                    # Barra no fim do arquivo
                    if i + 1 >= tamanho:

                        raise ErroMPL(
                            'lexico',
                            linha_inicio,
                            coluna_inicio,
                            'texto nao foi fechado'
                        )

                    proximo = fonte[i + 1]

                    if proximo not in ('n', 't', '"', '\\'):

                        raise ErroMPL(
                            'lexico',
                            linha,
                            coluna_escape,
                            'escape invalido'
                        )

                    # Consome \ e o caractere seguinte
                    i += 2
                    coluna += 2

                    continue

                i += 1
                coluna += 1

            # Arquivo terminou antes da "
            if not fechado:

                raise ErroMPL(
                    'lexico',
                    linha_inicio,
                    coluna_inicio,
                    'texto nao foi fechado'
                )

            # Mantem o texto exatamente como apareceu
            # inclusive aspas e escapes
            lexema = fonte[inicio_i:i]

            tokens.append(
                Token(
                    'TEXTO',
                    lexema,
                    linha_inicio,
                    coluna_inicio
                )
            )

            continue

        # ====================================================
        # 5. NUMEROS
        #
        # inteiro:
        # 10
        #
        # real:
        # 3.14
        #
        # ERROS:
        # 3.
        # .5
        # ====================================================

        if eh_digito(c):

            inicio_i = i

            linha_inicio = linha
            coluna_inicio = coluna

            # Parte inteira
            while (
                i < tamanho
                and eh_digito(fonte[i])
            ):
                i += 1
                coluna += 1

            # Existe ponto?
            if (
                i < tamanho
                and fonte[i] == '.'
            ):

                coluna_ponto = coluna

                # Precisa obrigatoriamente existir
                # um digito depois do ponto
                if (
                    i + 1 >= tamanho
                    or not eh_digito(fonte[i + 1])
                ):

                    raise ErroMPL(
                        'lexico',
                        linha,
                        coluna_ponto,
                        'numero real mal formado'
                    )

                # Consome .
                i += 1
                coluna += 1

                # Parte decimal
                while (
                    i < tamanho
                    and eh_digito(fonte[i])
                ):
                    i += 1
                    coluna += 1

                lexema = fonte[inicio_i:i]

                tokens.append(
                    Token(
                        'REAL',
                        lexema,
                        linha_inicio,
                        coluna_inicio
                    )
                )

            else:

                lexema = fonte[inicio_i:i]

                tokens.append(
                    Token(
                        'INTEIRO',
                        lexema,
                        linha_inicio,
                        coluna_inicio
                    )
                )

            continue

        # ====================================================
        # 6. IDENTIFICADORES E PALAVRAS RESERVADAS
        #
        # x
        # soma
        # valor10
        # _contador
        #
        # ou:
        #
        # inteiro
        # se
        # funcao
        # enquanto
        # ====================================================

        if eh_letra(c):

            inicio_i = i

            linha_inicio = linha
            coluna_inicio = coluna

            while (
                i < tamanho
                and eh_identificador(fonte[i])
            ):
                i += 1
                coluna += 1

            lexema = fonte[inicio_i:i]

            # Se estiver na tabela, e palavra reservada.
            # Caso contrario, e ID.
            tipo = PALAVRAS_RESERVADAS.get(
                lexema,
                'ID'
            )

            tokens.append(
                Token(
                    tipo,
                    lexema,
                    linha_inicio,
                    coluna_inicio
                )
            )

            continue

        # ====================================================
        # 7. OPERADORES DE DOIS CARACTERES
        #
        # IMPORTANTE:
        #
        # <= precisa ser reconhecido antes de <
        #
        # >= precisa ser reconhecido antes de >
        #
        # == precisa ser reconhecido antes de =
        # ====================================================

        if i + 1 < tamanho:

            operador = fonte[i:i + 2]

            if operador in OPERADORES_DOIS:

                tokens.append(
                    Token(
                        OPERADORES_DOIS[operador],
                        operador,
                        linha,
                        coluna
                    )
                )

                i += 2
                coluna += 2

                continue

        # ====================================================
        # 8. OPERADORES DE UM CARACTERE
        # ====================================================

        if c in OPERADORES_UM:

            tokens.append(
                Token(
                    OPERADORES_UM[c],
                    c,
                    linha,
                    coluna
                )
            )

            i += 1
            coluna += 1

            continue

        # ====================================================
        # 9. CARACTERE INVALIDO
        #
        # Tambem faz .5 ser rejeitado porque "." nao e
        # um token valido sozinho.
        # ====================================================

        raise ErroMPL(
            'lexico',
            linha,
            coluna,
            f'caractere invalido: {c}'
        )

    # ========================================================
    # 10. FIM DO ARQUIVO
    #
    # Se o arquivo termina com \n:
    # fica na proxima linha, coluna 1.
    #
    # Se nao termina com \n:
    # fica imediatamente depois do ultimo caractere.
    # ========================================================

    tokens.append(
        Token(
            'FIM_ARQUIVO',
            '',
            linha,
            coluna
        )
    )

    return tokens