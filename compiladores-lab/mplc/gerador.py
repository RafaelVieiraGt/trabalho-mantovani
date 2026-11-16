"""
Entrega 4, segunda metade — geracao do codigo executavel.

Traduz o codigo de tres enderecos para a maquina de pilha da nossa VM. O
.mplb e texto, uma instrucao por linha; o conjunto de instrucoes esta
documentado no README.md.

Cada funcao vira:

  .funcao <nome> <n_parametros> <n_locais>
    <instrucoes>
  .fim

Os locais (parametros, variaveis e temporarios) viram posicoes 0, 1, 2...
do registro de ativacao; os parametros ocupam as primeiras. O cabecalho
`.local <posicao> <nome>` registra de onde veio cada posicao, para quem le.
Cada instrucao de tres enderecos vira poucas de pilha:

  t3 = n * t2   ->   CARREGA 0 / CARREGA 2 / MULTIPLICA / GUARDA 3
"""
from mplc.intermediario import Const

BINARIOS = {
    '+': 'SOMA', '-': 'SUBTRAI', '*': 'MULTIPLICA', '/': 'DIVIDE', '%': 'RESTO',
    '==': 'IGUAL', '!=': 'DIFERENTE', '<': 'MENOR', '<=': 'MENOR_IGUAL',
    '>': 'MAIOR', '>=': 'MAIOR_IGUAL', 'e': 'E', 'ou': 'OU',
}
UNARIOS = {'-': 'NEGA', 'nao': 'NAO'}
EMPILHA = {
    'inteiro': 'EMPILHA_INTEIRO', 'real': 'EMPILHA_REAL',
    'logico': 'EMPILHA_LOGICO', 'texto': 'EMPILHA_TEXTO',
}


def gerar(codigo_intermediario):
    """Devolve as linhas do arquivo .mplb."""
    linhas = ['; MPL bytecode — maquina de pilha. Comeca por principal.']
    for f in codigo_intermediario:
        linhas.append('')
        linhas.extend(_Funcao(f).gerar())
    return linhas


class _Funcao:
    def __init__(self, f):
        self.f = f
        self.locais = {}
        for nome, _ in f.parametros:
            self.posicao(nome)
        for ins in f.codigo:            # na ordem em que aparecem
            for x in _destinos_e_operandos(ins):
                if isinstance(x, str):
                    self.posicao(x)

    def posicao(self, nome):
        if nome not in self.locais:
            self.locais[nome] = len(self.locais)
        return self.locais[nome]

    def gerar(self):
        f = self.f
        out = [f'.funcao {f.nome} {len(f.parametros)} {len(self.locais)}']
        for nome, pos in self.locais.items():
            out.append(f'.local {pos} {nome}')
        for ins in f.codigo:
            out.extend(self.instrucao(ins))
        out.append('.fim')
        return out

    def carrega(self, a):
        if isinstance(a, Const):
            return f'  {EMPILHA[a.tipo]} {a.texto}'
        return f'  CARREGA {self.locais[a]}'

    def guarda(self, d):
        return f'  GUARDA {self.locais[d]}'

    def instrucao(self, ins):
        op = ins[0]
        if op == 'linha':
            return [f'  LINHA {ins[1]} {ins[2]}']
        if op == 'copia':
            return [self.carrega(ins[2]), self.guarda(ins[1])]
        if op == 'binario':
            return [self.carrega(ins[2]), self.carrega(ins[4]),
                    f'  {BINARIOS[ins[3]]}', self.guarda(ins[1])]
        if op == 'unario':
            return [self.carrega(ins[3]), f'  {UNARIOS[ins[2]]}', self.guarda(ins[1])]
        if op == 'real':
            return [self.carrega(ins[2]), '  PARA_REAL', self.guarda(ins[1])]
        if op == 'param':
            return [self.carrega(ins[1])]
        if op == 'chama':
            out = [f'  CHAMA {ins[2]} {ins[3]}']
            if ins[1] is not None:
                out.append(self.guarda(ins[1]))
            return out
        if op == 'retorne':
            if ins[1] is None:
                return ['  RETORNA_VAZIO']
            return [self.carrega(ins[1]), '  RETORNA']
        if op == 'escreva':
            return [self.carrega(ins[1]), '  ESCREVA']
        if op == 'rotulo':
            return [f'{ins[1]}:']
        if op == 'desvie':
            return [f'  DESVIA {ins[1]}']
        if op == 'seFalso':
            return [self.carrega(ins[1]), f'  DESVIA_SE_FALSO {ins[2]}']
        raise ValueError(op)


def _destinos_e_operandos(ins):
    op = ins[0]
    if op in ('copia', 'real'):
        return [ins[1], ins[2]]
    if op == 'binario':
        return [ins[1], ins[2], ins[4]]
    if op == 'unario':
        return [ins[1], ins[3]]
    if op in ('param', 'retorne', 'escreva', 'seFalso'):
        return [ins[1]]
    if op == 'chama':
        return [ins[1]]
    return []
