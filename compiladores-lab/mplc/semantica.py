"""
Entrega 3 — analise semantica.

Tabela de simbolos, escopos aninhados e verificacao de tipos.

Como os escopos sao representados
---------------------------------
Cada escopo e um objeto `Escopo` com um dicionario de simbolos (que guarda a
ordem de declaracao) e um ponteiro para o escopo pai: um dicionario
encadeado. Durante a analise, o escopo "atual" anda para dentro quando um
bloco abre e volta para o pai quando ele fecha — na pratica, uma pilha. A
busca de um nome sobe a cadeia de pais, e por isso o sombreamento sai de
graca: o primeiro escopo que tem o nome vence. Nenhum escopo e apagado ao
fechar: todos ficam numa lista, na ordem em que abriram, que e exatamente o
que o --tabela despeja e o que a Entrega 4 usa para dar a cada variavel o seu
lugar no registro de ativacao.

O que a analise pendura na arvore (no.extra), para a Entrega 4 usar:
  - 'simbolo'   : em declaracao, parametro, variavel e atribuicao;
  - 'tipo_expr' : o tipo de cada expressao;
  - 'para_real' : True quando a expressao precisa da conversao inteiro→real;
  - 'funcao'    : em chamada, o simbolo da funcao chamada;
  - 'escopo'    : em funcao (o escopo dos parametros) e em bloco.
"""
from mplc.erros import ErroMPL

NUMERICOS = ('inteiro', 'real')


class Simbolo:
    def __init__(self, nome, categoria, tipo, linha, escopo, parametros=None):
        self.nome = nome
        self.categoria = categoria      # 'funcao', 'parametro' ou 'variavel'
        self.tipo = tipo                # para funcao: o tipo de retorno
        self.linha = linha
        self.escopo = escopo            # o numero do escopo onde vive
        self.parametros = parametros    # para funcao: lista de tipos

    def assinatura(self):
        if self.categoria == 'funcao':
            return f"{self.tipo}({','.join(self.parametros)})"
        return self.tipo


class Escopo:
    def __init__(self, numero, descricao, pai):
        self.numero = numero
        self.descricao = descricao
        self.pai = pai                  # o Escopo pai, ou None no global
        self.simbolos = {}              # nome -> Simbolo, em ordem de declaracao

    def buscar(self, nome):
        escopo = self
        while escopo is not None:
            if nome in escopo.simbolos:
                return escopo.simbolos[nome]
            escopo = escopo.pai
        return None


class Tabela:
    def __init__(self):
        self.escopos = []
        self.global_ = self.abrir('global', None)

    def abrir(self, descricao, pai):
        escopo = Escopo(len(self.escopos), descricao, pai)
        self.escopos.append(escopo)
        return escopo


def analisar(arvore):
    """Percorre a arvore, monta a tabela e confere os tipos. Devolve a tabela."""
    return _Analisador().analisar(arvore)


def despejar(tabela):
    """Devolve as linhas do --tabela, no formato da secao 4 do contrato."""
    linhas = []
    for e in tabela.escopos:
        if e.pai is None:
            linhas.append(f'escopo {e.numero} {e.descricao}')
        else:
            linhas.append(f'escopo {e.numero} {e.descricao} pai {e.pai.numero}')
        for s in e.simbolos.values():
            linhas.append(f'  {s.nome}|{s.categoria}|{s.assinatura()}|{s.linha}')
    return linhas


def _erro(no, mensagem):
    raise ErroMPL('semantico', no.linha, no.coluna, mensagem)


class _Analisador:
    def __init__(self):
        self.tabela = Tabela()
        self.atual = None               # escopo atual
        self.funcao = None              # simbolo da funcao sendo analisada

    # ------------------------------------------------------------------
    # As duas passadas
    # ------------------------------------------------------------------
    def analisar(self, programa):
        # 1a passada: so as assinaturas, para que uma funcao possa ser
        # chamada antes de aparecer no arquivo.
        globais = self.tabela.global_.simbolos
        for f in programa.filhos:
            nome = f.extra['nome']
            if nome in globais:
                _erro(f, f"funcao '{nome}' ja foi declarada na linha {globais[nome].linha}")
            tipos = [p.extra['tipo'] for p in f.filhos[0].filhos]
            globais[nome] = Simbolo(nome, 'funcao', f.extra['tipo'], f.linha, 0, tipos)
            f.extra['simbolo'] = globais[nome]

        principal = globais.get('principal')
        if principal is None:
            raise ErroMPL('semantico', 1, 1, "o programa nao tem a funcao 'principal'")
        no_principal = next(f for f in programa.filhos if f.extra['nome'] == 'principal')
        if principal.parametros:
            _erro(no_principal, "'principal' nao pode receber parametros")
        if principal.tipo != 'vazio':
            _erro(no_principal, "'principal' tem que devolver vazio")

        # 2a passada: os corpos.
        for f in programa.filhos:
            self.funcao_(f)
        return self.tabela

    def funcao_(self, no):
        self.funcao = no.extra['simbolo']
        parametros, bloco = no.filhos
        escopo = self.tabela.abrir(f"funcao {self.funcao.nome}", self.tabela.global_)
        no.extra['escopo'] = escopo
        self.atual = escopo
        for p in parametros.filhos:
            p.extra['simbolo'] = self.declarar(p, p.extra['nome'], 'parametro', p.extra['tipo'])
        self.bloco(bloco)
        self.atual = escopo.pai

        if self.funcao.tipo != 'vazio' and not self.garante_retorno(bloco):
            _erro(no, f"a funcao '{self.funcao.nome}' pode terminar sem 'retorne'")

    # ------------------------------------------------------------------
    # Escopos e simbolos
    # ------------------------------------------------------------------
    def declarar(self, no, nome, categoria, tipo):
        anterior = self.atual.simbolos.get(nome)
        if anterior is not None:
            _erro(no, f"'{nome}' ja foi declarado neste escopo, na linha {anterior.linha}")
        s = Simbolo(nome, categoria, tipo, no.linha, self.atual.numero)
        self.atual.simbolos[nome] = s
        return s

    def buscar_variavel(self, no, nome):
        s = self.atual.buscar(nome)
        if s is None or s.categoria == 'funcao':
            _erro(no, f"'{nome}' nao foi declarada")
        return s

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------
    def bloco(self, no):
        escopo = self.tabela.abrir('bloco', self.atual)
        no.extra['escopo'] = escopo
        self.atual = escopo
        for c in no.filhos:
            self.comando(c)
        self.atual = escopo.pai

    def comando(self, no):
        tipo = no.rotulo.split()[0]
        if tipo == 'declaracao':
            if no.filhos:
                self.coagir(no.filhos[0], no.extra['tipo'], no, 'inicializar')
            no.extra['simbolo'] = self.declarar(no, no.extra['nome'], 'variavel', no.extra['tipo'])
        elif tipo == 'atribuicao':
            s = self.buscar_variavel(no, no.extra['nome'])
            no.extra['simbolo'] = s
            self.coagir(no.filhos[0], s.tipo, no, 'atribuir')
        elif tipo in ('se', 'enquanto'):
            cond = no.filhos[0]
            if self.expressao(cond) != 'logico':
                _erro(cond, f"a condicao do '{tipo}' tem que ser logico, e veio {cond.extra['tipo_expr']}")
            for b in no.filhos[1:]:
                self.bloco(b)
        elif tipo == 'escreva':
            if self.expressao(no.filhos[0], aceita_vazio=True) == 'vazio':
                _erro(no.filhos[0], "nao da para escrever o resultado de uma funcao vazio")
        elif tipo == 'retorne':
            esperado = self.funcao.tipo
            if esperado == 'vazio':
                if no.filhos:
                    _erro(no, f"a funcao '{self.funcao.nome}' e vazio e nao devolve valor")
            else:
                if not no.filhos:
                    _erro(no, f"a funcao '{self.funcao.nome}' tem que devolver {esperado}")
                self.coagir(no.filhos[0], esperado, no, 'devolver')
        elif tipo == 'chamada':
            self.expressao(no, aceita_vazio=True)
        elif tipo == 'bloco':
            self.bloco(no)
        else:  # nao acontece: o parser so produz os comandos acima
            _erro(no, f'comando desconhecido: {no.rotulo}')

    def garante_retorno(self, no):
        """Olha a estrutura, nunca o valor das condicoes."""
        tipo = no.rotulo.split()[0]
        if tipo == 'retorne':
            return True
        if tipo == 'bloco':
            return any(self.garante_retorno(c) for c in no.filhos)
        if tipo == 'se' and len(no.filhos) == 3:
            return self.garante_retorno(no.filhos[1]) and self.garante_retorno(no.filhos[2])
        return False

    # ------------------------------------------------------------------
    # Tipos
    # ------------------------------------------------------------------
    def coagir(self, expr, alvo, onde, verbo):
        """Confere que a expressao cabe no tipo alvo (com a conversao de 3.1)."""
        tipo = self.expressao(expr)
        if tipo == alvo:
            return
        if tipo == 'inteiro' and alvo == 'real':
            expr.extra['para_real'] = True
            return
        _erro(onde, f'nao da para {verbo} {tipo} onde se espera {alvo}')

    def expressao(self, no, aceita_vazio=False):
        tipo = self._expressao(no)
        if tipo == 'vazio' and not aceita_vazio:
            _erro(no, f"a funcao '{no.extra['nome']}' e vazio e nao pode aparecer numa expressao")
        no.extra['tipo_expr'] = tipo
        return tipo

    def _expressao(self, no):
        tipo = no.rotulo.split()[0]
        if tipo == 'literal':
            return no.extra['tipo']
        if tipo == 'variavel':
            s = self.buscar_variavel(no, no.extra['nome'])
            no.extra['simbolo'] = s
            return s.tipo
        if tipo == 'chamada':
            return self.chamada(no)
        if tipo == 'unario':
            return self.unario(no)
        if tipo == 'binario':
            return self.binario(no)
        _erro(no, f'expressao desconhecida: {no.rotulo}')

    def chamada(self, no):
        nome = no.extra['nome']
        f = self.tabela.global_.simbolos.get(nome)
        if f is None:
            _erro(no, f"a funcao '{nome}' nao existe")
        no.extra['funcao'] = f
        if len(no.filhos) != len(f.parametros):
            _erro(no, f"'{nome}' recebe {len(f.parametros)} argumento(s), e vieram {len(no.filhos)}")
        for i, (arg, tipo) in enumerate(zip(no.filhos, f.parametros), 1):
            self.coagir(arg, tipo, arg, f'passar como argumento {i} de {nome}')
        return f.tipo

    def unario(self, no):
        op = no.extra['operador']
        t = self.expressao(no.filhos[0])
        if op == 'nao':
            if t != 'logico':
                _erro(no, f"'nao' exige logico, e veio {t}")
            return 'logico'
        if t not in NUMERICOS:
            _erro(no, f"'-' exige numero, e veio {t}")
        return t

    def binario(self, no):
        op = no.extra['operador']
        esq, dir_ = no.filhos
        a = self.expressao(esq)
        b = self.expressao(dir_)

        def promover():
            """inteiro com real: o lado inteiro vira real. Devolve o tipo comum."""
            if a == b:
                return a
            if a == 'inteiro':
                esq.extra['para_real'] = True
            else:
                dir_.extra['para_real'] = True
            return 'real'

        numericos = a in NUMERICOS and b in NUMERICOS
        if op == '+' and a == 'texto' and b == 'texto':
            return 'texto'
        if op in ('+', '-', '*', '/'):
            if not numericos:
                _erro(no, f"'{op}' nao aceita {a} com {b}")
            return promover()
        if op == '%':
            if a != 'inteiro' or b != 'inteiro':
                _erro(no, f"'%' so aceita inteiro com inteiro, e veio {a} com {b}")
            return 'inteiro'
        if op in ('<', '<=', '>', '>='):
            if not numericos:
                _erro(no, f"'{op}' so compara numeros, e veio {a} com {b}")
            promover()
            return 'logico'
        if op in ('==', '!='):
            if numericos:
                promover()
            elif a != b:
                _erro(no, f"'{op}' compara dois do mesmo tipo, e veio {a} com {b}")
            return 'logico'
        if op in ('e', 'ou'):
            if a != 'logico' or b != 'logico':
                _erro(no, f"'{op}' exige logico dos dois lados, e veio {a} com {b}")
            return 'logico'
        _erro(no, f'operador desconhecido: {op}')
