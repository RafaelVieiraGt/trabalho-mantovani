"""
Entrega 4, terceira metade (sim, sao tres) — a maquina virtual.

Le o .mplb e executa. Tem:
  - uma pilha de operandos, compartilhada por todas as chamadas;
  - uma pilha de registros de ativacao: cada chamada ganha o SEU vetor de
    locais, o ponto de volta (funcao + indice da instrucao) e a linha do
    comando que esta rodando;
  - deteccao de divisao por zero e de estouro de pilha, que viram erro de
    execucao (codigo de saida 2, pela principal.py).

A VM e um laco, nao uma funcao recursiva: a recursao do programa MPL vive
na pilha de registros, e nao na pilha do Python.
"""
import re

from mplc.erros import ErroMPL
from mplc.intermediario import desescapar

LIMITE_CHAMADAS = 100_000   # registros de ativacao vivos ao mesmo tempo


class Funcao:
    def __init__(self, nome, n_parametros, n_locais):
        self.nome = nome
        self.n_parametros = n_parametros
        self.n_locais = n_locais
        self.codigo = []        # lista de (operacao, argumento)
        self.rotulos = {}       # rotulo -> indice no codigo


class Registro:
    """O registro de ativacao de uma chamada."""
    __slots__ = ('funcao', 'locais', 'pc', 'linha', 'coluna')

    def __init__(self, funcao, locais):
        self.funcao = funcao
        self.locais = locais
        self.pc = 0
        self.linha = 1
        self.coluna = 1


def carregar(texto):
    """Le o .mplb e devolve {nome: Funcao}."""
    funcoes, atual = {}, None
    for bruta in texto.splitlines():
        linha = bruta.strip()
        if not linha or linha.startswith(';') or linha.startswith('.local'):
            continue
        if linha.startswith('.funcao'):
            _, nome, n_par, n_loc = linha.split()
            atual = funcoes[nome] = Funcao(nome, int(n_par), int(n_loc))
        elif linha == '.fim':
            atual = None
        elif linha.endswith(':'):
            atual.rotulos[linha[:-1]] = len(atual.codigo)
        else:
            op, _, arg = linha.partition(' ')
            atual.codigo.append((op, _argumento(op, arg.strip())))
    for f in funcoes.values():          # rotulo -> indice, de uma vez so
        f.codigo = [(op, f.rotulos[a]) if op in ('DESVIA', 'DESVIA_SE_FALSO') else (op, a)
                    for op, a in f.codigo]
    return funcoes


def _argumento(op, arg):
    if op == 'EMPILHA_INTEIRO' or op in ('CARREGA', 'GUARDA'):
        return int(arg)
    if op == 'EMPILHA_REAL':
        return float(arg)
    if op == 'EMPILHA_LOGICO':
        return arg == 'verdadeiro'
    if op == 'EMPILHA_TEXTO':
        if not re.fullmatch(r'"(\\.|[^"\\])*"', arg):
            raise ValueError(f'texto mal formado no .mplb: {arg}')
        return desescapar(arg)
    if op == 'CHAMA':
        nome, n = arg.split()
        return (nome, int(n))
    if op == 'LINHA':
        l, c = arg.split()
        return (int(l), int(c))
    return arg or None


def formatar(v):
    """A forma impressa de cada tipo (LINGUAGEM.md 4.5)."""
    if isinstance(v, bool):             # antes de int: bool e int no Python
        return 'verdadeiro' if v else 'falso'
    if isinstance(v, float):
        return f'{v:.6f}'
    return str(v)


def _divide(a, b):
    if isinstance(a, int) and isinstance(b, int):
        q = abs(a) // abs(b)            # truncada em direcao a zero
        return q if (a >= 0) == (b >= 0) else -q
    return a / b


def _resto(a, b):
    return a - b * _divide(a, b)        # sinal do dividendo: -7 % 3 == -1


BINARIAS = {
    'SOMA': lambda a, b: a + b,
    'SUBTRAI': lambda a, b: a - b,
    'MULTIPLICA': lambda a, b: a * b,
    'DIVIDE': _divide,
    'RESTO': _resto,
    'IGUAL': lambda a, b: a == b,
    'DIFERENTE': lambda a, b: a != b,
    'MENOR': lambda a, b: a < b,
    'MENOR_IGUAL': lambda a, b: a <= b,
    'MAIOR': lambda a, b: a > b,
    'MAIOR_IGUAL': lambda a, b: a >= b,
    'E': lambda a, b: a and b,
    'OU': lambda a, b: a or b,
}


def executar(texto_mplb, saida):
    """Executa o bytecode. Escreve o que o programa imprimir em `saida`."""
    funcoes = carregar(texto_mplb)
    pilha = []
    chamadas = [Registro(funcoes['principal'], [None] * funcoes['principal'].n_locais)]

    def erro(mensagem):
        r = chamadas[-1]
        return ErroMPL('execucao', r.linha, r.coluna, mensagem)

    while chamadas:
        r = chamadas[-1]
        codigo = r.funcao.codigo
        if r.pc >= len(codigo):
            raise erro(f"a funcao '{r.funcao.nome}' terminou sem retorne")
        op, arg = codigo[r.pc]
        r.pc += 1

        if op == 'CARREGA':
            pilha.append(r.locais[arg])
        elif op == 'GUARDA':
            r.locais[arg] = pilha.pop()
        elif op.startswith('EMPILHA_'):
            pilha.append(arg)
        elif op in BINARIAS:
            b = pilha.pop()
            a = pilha.pop()
            if op in ('DIVIDE', 'RESTO') and b == 0:
                raise erro('divisao por zero' if op == 'DIVIDE' else 'resto de divisao por zero')
            pilha.append(BINARIAS[op](a, b))
        elif op == 'NEGA':
            pilha.append(-pilha.pop())
        elif op == 'NAO':
            pilha.append(not pilha.pop())
        elif op == 'PARA_REAL':
            pilha.append(float(pilha.pop()))
        elif op == 'DESVIA':
            r.pc = arg
        elif op == 'DESVIA_SE_FALSO':
            if not pilha.pop():
                r.pc = arg
        elif op == 'ESCREVA':
            saida.write(formatar(pilha.pop()) + '\n')
        elif op == 'LINHA':
            r.linha, r.coluna = arg
        elif op == 'CHAMA':
            nome, n = arg
            if len(chamadas) >= LIMITE_CHAMADAS:
                raise erro(f"estouro de pilha: mais de {LIMITE_CHAMADAS} chamadas ativas (chamando '{nome}')")
            f = funcoes[nome]
            locais = [None] * f.n_locais
            if n:
                locais[:n] = pilha[-n:]
                del pilha[-n:]
            chamadas.append(Registro(f, locais))
        elif op == 'RETORNA':
            chamadas.pop()              # o valor fica no topo da pilha
        elif op == 'RETORNA_VAZIO':
            chamadas.pop()
        else:
            raise erro(f'instrucao desconhecida no .mplb: {op}')
