"""
Entrega 4, primeira metade — codigo de tres enderecos.

A propriedade que define a representacao, e a unica que o verificador mede:
cada linha de operacao tem NO MAXIMO UM OPERADOR. Uma expressao como
a + b * c vira duas linhas, com um temporario no meio.

Representacao
-------------
O programa vira uma lista de `Funcao`, e cada uma tem uma lista de
instrucoes (tuplas). Um operando e um nome (variavel ou temporario, uma str)
ou uma `Const` (literal com tipo). As instrucoes:

  ('copia',   destino, a)               destino = a
  ('binario', destino, a, op, b)        destino = a op b
  ('unario',  destino, op, a)           destino = op a       (op: '-' ou 'nao')
  ('real',    destino, a)               destino = real a     (inteiro -> real)
  ('param',   a)                        param a
  ('chama',   destino, f, n)            destino = chama f, n (destino None: funcao vazio)
  ('retorne', a)                        retorne a            (a None: retorne vazio)
  ('escreva', a)                        escreva a
  ('rotulo',  L)                        L:
  ('desvie',  L)                        desvie L
  ('seFalso', a, L)                     seFalso a desvie L
  ('linha',   l, c)                     marca a linha do comando (para erros
                                        de execucao); nao aparece no --ir

Nomes: cada variavel sai com o proprio nome. Quando a mesma funcao tem duas
variaveis com o mesmo nome (sombreamento), elas viram `nome.E`, onde E e o
numero do escopo da tabela de simbolos — assim cada uma ganha o seu lugar.
Temporarios sao t0, t1, ... (reiniciam em cada funcao); rotulos sao L0,
L1, ... (unicos no programa inteiro).
"""
import re


class Const:
    """Um literal: tipo e valor ja convertido para Python."""

    def __init__(self, tipo, valor, texto):
        self.tipo = tipo
        self.valor = valor
        self.texto = texto      # como aparece no --ir e no .mplb

    def __str__(self):
        return self.texto


class Funcao:
    def __init__(self, nome, tipo, parametros):
        self.nome = nome
        self.tipo = tipo
        self.parametros = parametros    # lista de (nome no IR, tipo)
        self.codigo = []


ESCAPES = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}


def desescapar(lexema):
    """'"a\\nb"' (com aspas e escapes do fonte) -> 'a<quebra>b'."""
    return re.sub(r'\\(.)', lambda m: ESCAPES[m.group(1)], lexema[1:-1])


def gerar(arvore, tabela):
    """Devolve o codigo de tres enderecos: uma lista de Funcao."""
    g = _Gerador()
    return [g.funcao(f) for f in arvore.filhos]


def despejar(codigo):
    """Devolve as linhas do --ir."""
    linhas = []
    for f in codigo:
        params = ', '.join(f'{n} {t}' for n, t in f.parametros)
        linhas.append(f'funcao {f.nome} {f.tipo} ({params})')
        for ins in f.codigo:
            texto = formatar(ins)
            if texto is not None:
                linhas.append(texto)
        linhas.append('fim')
        linhas.append('')
    return linhas[:-1]


def formatar(ins):
    op = ins[0]
    if op == 'copia':
        return f'  {ins[1]} = {ins[2]}'
    if op == 'binario':
        return f'  {ins[1]} = {ins[2]} {ins[3]} {ins[4]}'
    if op == 'unario':
        return f'  {ins[1]} = {ins[2]} {ins[3]}'
    if op == 'real':
        return f'  {ins[1]} = real {ins[2]}'
    if op == 'param':
        return f'  param {ins[1]}'
    if op == 'chama':
        if ins[1] is None:
            return f'  chama {ins[2]}, {ins[3]}'
        return f'  {ins[1]} = chama {ins[2]}, {ins[3]}'
    if op == 'retorne':
        return '  retorne' if ins[1] is None else f'  retorne {ins[1]}'
    if op == 'escreva':
        return f'  escreva {ins[1]}'
    if op == 'rotulo':
        return f'{ins[1]}:'
    if op == 'desvie':
        return f'  desvie {ins[1]}'
    if op == 'seFalso':
        return f'  seFalso {ins[1]} desvie {ins[2]}'
    if op == 'linha':
        return None
    raise ValueError(op)


PADRAO = {
    'inteiro': Const('inteiro', 0, '0'),
    'real': Const('real', 0.0, '0.0'),
    'logico': Const('logico', False, 'falso'),
    'texto': Const('texto', '', '""'),
}


class _Gerador:
    def __init__(self):
        self.rotulos = 0

    def novo_rotulo(self):
        r = f'L{self.rotulos}'
        self.rotulos += 1
        return r

    def novo_temp(self):
        t = f't{self.temps}'
        self.temps += 1
        return t

    def emitir(self, *ins):
        self.atual.codigo.append(ins)

    # ------------------------------------------------------------------
    def funcao(self, no):
        self.temps = 0
        parametros, bloco = no.filhos
        self.nomes = self.dar_nomes(no)
        params = [(self.nomes[id(p.extra['simbolo'])], p.extra['tipo']) for p in parametros.filhos]
        self.atual = Funcao(no.extra['nome'], no.extra['tipo'], params)
        self.comando(bloco)
        cod = self.atual.codigo
        if no.extra['tipo'] == 'vazio' and (not cod or cod[-1][0] != 'retorne'):
            self.emitir('retorne', None)
        return self.atual

    def dar_nomes(self, funcao):
        """Um nome no IR para cada simbolo (variavel ou parametro) da funcao."""
        simbolos = []

        def coletar(no):
            s = no.extra.get('simbolo')
            if no.rotulo.split()[0] in ('parametro', 'declaracao') and s is not None:
                simbolos.append(s)
            for f in no.filhos:
                coletar(f)

        coletar(funcao)
        contagem = {}
        for s in simbolos:
            contagem[s.nome] = contagem.get(s.nome, 0) + 1
        nomes = {}
        for s in simbolos:
            # um nome repetido, ou com cara de temporario, ganha o escopo junto
            if contagem[s.nome] > 1 or re.fullmatch(r't\d+', s.nome):
                nomes[id(s)] = f'{s.nome}.{s.escopo}'
            else:
                nomes[id(s)] = s.nome
        return nomes

    def nome(self, no):
        return self.nomes[id(no.extra['simbolo'])]

    # ------------------------------------------------------------------
    def comando(self, no):
        tipo = no.rotulo.split()[0]
        if tipo == 'bloco':
            for c in no.filhos:
                self.comando(c)
            return

        self.emitir('linha', no.linha, no.coluna)
        if tipo == 'declaracao':
            # sem valor inicial, recebe o padrao do tipo — e de novo a cada
            # volta, se a declaracao estiver dentro de um enquanto
            valor = self.expressao(no.filhos[0]) if no.filhos else PADRAO[no.extra['tipo']]
            self.emitir('copia', self.nome(no), valor)
        elif tipo == 'atribuicao':
            self.emitir('copia', self.nome(no), self.expressao(no.filhos[0]))
        elif tipo == 'escreva':
            self.emitir('escreva', self.expressao(no.filhos[0]))
        elif tipo == 'retorne':
            self.emitir('retorne', self.expressao(no.filhos[0]) if no.filhos else None)
        elif tipo == 'chamada':
            self.chamada(no)
        elif tipo == 'se':
            senao, fim = self.novo_rotulo(), None
            cond = self.expressao(no.filhos[0])
            self.emitir('seFalso', cond, senao)
            self.comando(no.filhos[1])
            if len(no.filhos) == 3:
                fim = self.novo_rotulo()
                self.emitir('desvie', fim)
            self.emitir('rotulo', senao)
            if fim is not None:
                self.comando(no.filhos[2])
                self.emitir('rotulo', fim)
        elif tipo == 'enquanto':
            inicio, fim = self.novo_rotulo(), self.novo_rotulo()
            self.emitir('rotulo', inicio)
            self.emitir('linha', no.linha, no.coluna)
            cond = self.expressao(no.filhos[0])
            self.emitir('seFalso', cond, fim)
            self.comando(no.filhos[1])
            self.emitir('desvie', inicio)
            self.emitir('rotulo', fim)
        else:
            raise ValueError(no.rotulo)

    # ------------------------------------------------------------------
    def expressao(self, no):
        """Gera o codigo da expressao e devolve o operando com o resultado."""
        valor = self._expressao(no)
        if no.extra.get('para_real'):
            t = self.novo_temp()
            self.emitir('real', t, valor)
            valor = t
        return valor

    def _expressao(self, no):
        tipo = no.rotulo.split()[0]
        if tipo == 'literal':
            return self.literal(no)
        if tipo == 'variavel':
            return self.nome(no)
        if tipo == 'chamada':
            return self.chamada(no)
        if tipo == 'unario':
            a = self.expressao(no.filhos[0])
            t = self.novo_temp()
            self.emitir('unario', t, no.extra['operador'], a)
            return t
        if tipo == 'binario':
            # sem curto-circuito: os dois lados sao sempre avaliados
            a = self.expressao(no.filhos[0])
            b = self.expressao(no.filhos[1])
            t = self.novo_temp()
            self.emitir('binario', t, a, no.extra['operador'], b)
            return t
        raise ValueError(no.rotulo)

    def literal(self, no):
        tipo, lexema = no.extra['tipo'], no.extra['lexema']
        if tipo == 'inteiro':
            return Const(tipo, int(lexema), lexema)
        if tipo == 'real':
            return Const(tipo, float(lexema), lexema)
        if tipo == 'logico':
            return Const(tipo, lexema == 'verdadeiro', lexema)
        return Const(tipo, desescapar(lexema), lexema)

    def chamada(self, no):
        args = [self.expressao(a) for a in no.filhos]
        for a in args:
            self.emitir('param', a)
        f = no.extra['funcao']
        # funcao com retorno chamada como comando: o valor vai para um
        # temporario que ninguem le, para nao sobrar nada na pilha da VM
        destino = None if f.tipo == 'vazio' else self.novo_temp()
        self.emitir('chama', destino, f.nome, len(args))
        return destino
