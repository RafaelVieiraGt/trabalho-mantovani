"""
Entrega 2 — analise sintatica.

Transformar a lista de tokens numa arvore.

Sugestao forte: descida recursiva, uma funcao por nivel de precedencia, na
ordem da secao 3.3 da especificacao. E como voces vao enxergar a precedencia
virar formato de arvore.

Gerador de parser (ANTLR, PLY, yacc) esta proibido nesta entrega e na
anterior — o objetivo e entender, e o gerador esconde exatamente a parte
que esta sendo ensinada.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 3.
"""
from mplc.erros import ErroMPL


class No:
    """Um no da arvore. O rotulo e o que sai no --ast."""

    def __init__(self, rotulo, filhos=None, linha=0, coluna=0, **extra):
        self.rotulo = rotulo      # 'binario +', 'literal inteiro 1', 'bloco', ...
        self.filhos = filhos or []
        self.linha = linha
        self.coluna = coluna
        self.extra = extra        # o que a semantica quiser pendurar depois


def analisar(tokens):
    """Recebe a lista de Token. Devolve a raiz da arvore (um No 'programa')."""
    return _Analisador(tokens).analisar()


class _Analisador:
    TIPOS = {
        'TIPO_INTEIRO': 'inteiro',
        'TIPO_REAL': 'real',
        'TIPO_LOGICO': 'logico',
        'TIPO_TEXTO': 'texto',
        'TIPO_VAZIO': 'vazio',
    }

    BINARIOS = {
        'OU': 'ou',
        'E': 'e',
        'IGUAL': '==',
        'DIFERENTE': '!=',
        'MENOR': '<',
        'MENOR_IGUAL': '<=',
        'MAIOR': '>',
        'MAIOR_IGUAL': '>=',
        'MAIS': '+',
        'MENOS': '-',
        'VEZES': '*',
        'DIVIDE': '/',
        'RESTO': '%',
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.indice = 0

    @property
    def atual(self):
        return self.tokens[self.indice]

    def aceitar(self, *tipos):
        if self.atual.tipo in tipos:
            token = self.atual
            self.indice += 1
            return token
        return None

    def exigir(self, tipo, descricao=None):
        token = self.aceitar(tipo)
        if token is None:
            esperado = descricao or tipo.lower().replace('_', ' ')
            raise ErroMPL(
                'sintatico', self.atual.linha, self.atual.coluna,
                f'esperado {esperado}'
            )
        return token

    @staticmethod
    def no(rotulo, token, filhos=None, **extra):
        return No(rotulo, filhos, token.linha, token.coluna, **extra)

    def analisar(self):
        inicio = self.atual
        funcoes = []
        while self.atual.tipo != 'FIM_ARQUIVO':
            funcoes.append(self.funcao())
        self.exigir('FIM_ARQUIVO')
        return self.no('programa', inicio, funcoes)

    def tipo(self):
        token = self.atual
        if token.tipo not in self.TIPOS:
            raise ErroMPL(
                'sintatico', token.linha, token.coluna,
                'esperado tipo'
            )
        self.indice += 1
        return self.TIPOS[token.tipo], token

    def funcao(self):
        inicio = self.exigir('FUNCAO', 'funcao')
        tipo, _ = self.tipo()
        nome = self.exigir('ID', 'nome da funcao')
        self.exigir('ABRE_PAR', "'('")

        parametros = []
        if self.atual.tipo != 'FECHA_PAR':
            while True:
                tipo_parametro, token_tipo = self.tipo()
                nome_parametro = self.exigir('ID', 'nome do parametro')
                parametros.append(self.no(
                    f'parametro {nome_parametro.lexema} {tipo_parametro}',
                    token_tipo,
                    nome=nome_parametro.lexema,
                    tipo=tipo_parametro,
                ))
                if not self.aceitar('VIRGULA'):
                    break
        self.exigir('FECHA_PAR', "')'")
        bloco = self.bloco()
        return self.no(
            f'funcao {nome.lexema} {tipo}', inicio,
            [self.no('parametros', nome, parametros), bloco],
            nome=nome.lexema,
            tipo=tipo,
        )

    def bloco(self):
        inicio = self.exigir('ABRE_CHAVE', "'{'")
        comandos = []
        while self.atual.tipo not in ('FECHA_CHAVE', 'FIM_ARQUIVO'):
            comandos.append(self.comando())
        self.exigir('FECHA_CHAVE', "'}'")
        return self.no('bloco', inicio, comandos)

    def comando(self):
        tipo = self.atual.tipo
        if tipo in self.TIPOS and tipo != 'TIPO_VAZIO':
            return self.declaracao()
        if tipo == 'ID':
            return self.comando_id()
        if tipo == 'SE':
            return self.condicional()
        if tipo == 'ENQUANTO':
            return self.repeticao()
        if tipo == 'ESCREVA':
            return self.escrita()
        if tipo == 'RETORNE':
            return self.retorno()
        if tipo == 'ABRE_CHAVE':
            return self.bloco()
        raise ErroMPL(
            'sintatico', self.atual.linha, self.atual.coluna,
            'esperado comando'
        )

    def declaracao(self):
        tipo, token_tipo = self.tipo()
        nome = self.exigir('ID', 'nome da variavel')
        filhos = []
        if self.aceitar('ATRIBUI'):
            filhos.append(self.expressao())
        self.exigir('PONTO_VIRGULA', "';'")
        return self.no(
            f'declaracao {nome.lexema} {tipo}', token_tipo, filhos,
            nome=nome.lexema, tipo=tipo,
        )

    def comando_id(self):
        nome = self.exigir('ID')
        if self.aceitar('ATRIBUI'):
            valor = self.expressao()
            self.exigir('PONTO_VIRGULA', "';'")
            return self.no(
                f'atribuicao {nome.lexema}', nome, [valor],
                nome=nome.lexema,
            )
        if self.atual.tipo == 'ABRE_PAR':
            chamada = self.chamada(nome)
            self.exigir('PONTO_VIRGULA', "';'")
            return chamada
        raise ErroMPL(
            'sintatico', self.atual.linha, self.atual.coluna,
            "esperado '=' ou chamada de funcao"
        )

    def condicional(self):
        inicio = self.exigir('SE')
        self.exigir('ABRE_PAR', "'('")
        condicao = self.expressao()
        self.exigir('FECHA_PAR', "')'")
        filhos = [condicao, self.bloco()]
        if self.aceitar('SENAO'):
            filhos.append(self.bloco())
        return self.no('se', inicio, filhos)

    def repeticao(self):
        inicio = self.exigir('ENQUANTO')
        self.exigir('ABRE_PAR', "'('")
        condicao = self.expressao()
        self.exigir('FECHA_PAR', "')'")
        return self.no('enquanto', inicio, [condicao, self.bloco()])

    def escrita(self):
        inicio = self.exigir('ESCREVA')
        self.exigir('ABRE_PAR', "'('")
        valor = self.expressao()
        self.exigir('FECHA_PAR', "')'")
        self.exigir('PONTO_VIRGULA', "';'")
        return self.no('escreva', inicio, [valor])

    def retorno(self):
        inicio = self.exigir('RETORNE')
        filhos = []
        if self.atual.tipo != 'PONTO_VIRGULA':
            filhos.append(self.expressao())
        self.exigir('PONTO_VIRGULA', "';'")
        return self.no('retorne', inicio, filhos)

    def expressao(self):
        return self.ou()

    def binario(self, proximo, tipos):
        esquerda = proximo()
        while self.atual.tipo in tipos:
            operador = self.atual
            self.indice += 1
            direita = proximo()
            esquerda = self.no(
                f'binario {self.BINARIOS[operador.tipo]}', operador,
                [esquerda, direita], operador=self.BINARIOS[operador.tipo],
            )
        return esquerda

    def ou(self):
        return self.binario(self.e, ('OU',))

    def e(self):
        return self.binario(self.igualdade, ('E',))

    def igualdade(self):
        return self.binario(self.relacional, ('IGUAL', 'DIFERENTE'))

    def relacional(self):
        return self.binario(
            self.aditivo, ('MENOR', 'MENOR_IGUAL', 'MAIOR', 'MAIOR_IGUAL')
        )

    def aditivo(self):
        return self.binario(self.multiplicativo, ('MAIS', 'MENOS'))

    def multiplicativo(self):
        return self.binario(self.unario, ('VEZES', 'DIVIDE', 'RESTO'))

    def unario(self):
        operador = self.aceitar('NAO', 'MENOS')
        if operador is not None:
            simbolo = 'nao' if operador.tipo == 'NAO' else '-'
            return self.no(
                f'unario {simbolo}', operador, [self.unario()],
                operador=simbolo,
            )
        return self.primario()

    def primario(self):
        token = self.atual
        if token.tipo in ('INTEIRO', 'REAL', 'LOGICO', 'TEXTO'):
            self.indice += 1
            tipo = {
                'INTEIRO': 'inteiro', 'REAL': 'real',
                'LOGICO': 'logico', 'TEXTO': 'texto',
            }[token.tipo]
            valor = token.lexema
            if token.tipo == 'REAL':
                valor = f'{float(valor):.6f}'
            return self.no(
                f'literal {tipo} {valor}', token,
                tipo=tipo, valor=valor,
            )
        if token.tipo == 'ID':
            self.indice += 1
            if self.atual.tipo == 'ABRE_PAR':
                return self.chamada(token)
            return self.no(
                f'variavel {token.lexema}', token,
                nome=token.lexema,
            )
        if self.aceitar('ABRE_PAR'):
            expressao = self.expressao()
            self.exigir('FECHA_PAR', "')'")
            return expressao
        raise ErroMPL(
            'sintatico', token.linha, token.coluna,
            'esperada uma expressao'
        )

    def chamada(self, nome):
        self.exigir('ABRE_PAR', "'('")
        argumentos = []
        if self.atual.tipo != 'FECHA_PAR':
            while True:
                argumentos.append(self.expressao())
                if not self.aceitar('VIRGULA'):
                    break
        self.exigir('FECHA_PAR', "')'")
        return self.no(
            f'chamada {nome.lexema}', nome, argumentos,
            nome=nome.lexema,
        )


def despejar(no, nivel=0, saida=None):
    """Imprime a arvore no formato do --ast. Ja esta pronto: dois espacos por nivel."""
    saida = saida if saida is not None else []
    saida.append('  ' * nivel + no.rotulo)
    for f in no.filhos:
        despejar(f, nivel + 1, saida)
    return saida
