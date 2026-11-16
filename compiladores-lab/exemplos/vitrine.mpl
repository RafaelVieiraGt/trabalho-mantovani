// vitrine.mpl — o programa do grupo para a apresentacao.
//
// Quatro problemas classicos, cada um exercitando uma parte do compilador:
//   1. Torre de Hanoi       recursao em funcao vazio, texto concatenado
//   2. Raiz pelo Newton     real, conversao inteiro -> real, enquanto
//   3. Numero em binario    recursao que devolve texto, divisao inteira e %
//   4. Collatz              laco com se/senao, escopos aninhados
//
// Para rodar:  ./compilar exemplos/vitrine.mpl && ./executar exemplos/vitrine.mplb

// ---------------------------------------------------------------- 1. Hanoi
funcao vazio mover(inteiro n, texto origem, texto destino, texto auxiliar) {
  se (n == 0) {
    retorne;
  }
  mover(n - 1, origem, auxiliar, destino);
  escreva("  disco " + digito(n) + ": " + origem + " -> " + destino);
  mover(n - 1, auxiliar, destino, origem);
}

funcao texto digito(inteiro d) {
  se (d == 0) { retorne "0"; }
  se (d == 1) { retorne "1"; }
  se (d == 2) { retorne "2"; }
  se (d == 3) { retorne "3"; }
  se (d == 4) { retorne "4"; }
  se (d == 5) { retorne "5"; }
  se (d == 6) { retorne "6"; }
  se (d == 7) { retorne "7"; }
  se (d == 8) { retorne "8"; }
  retorne "9";
}

// ------------------------------------------------------- 2. Raiz (Newton)
funcao real raiz(real x) {
  real chute = x / 2;
  inteiro passos = 0;
  enquanto (passos < 20) {
    chute = (chute + x / chute) / 2;
    passos = passos + 1;
  }
  retorne chute;
}

// ------------------------------------------------------------ 3. Binario
funcao texto binario(inteiro n) {
  se (n < 2) {
    retorne digito(n);
  }
  retorne binario(n / 2) + digito(n % 2);
}

// ------------------------------------------------------------ 4. Collatz
funcao inteiro collatz(inteiro n) {
  inteiro passos = 0;
  enquanto (n != 1) {
    se (n % 2 == 0) {
      n = n / 2;
    } senao {
      n = 3 * n + 1;
    }
    passos = passos + 1;
  }
  retorne passos;
}

funcao vazio principal() {
  escreva("Torre de Hanoi com 3 discos:");
  mover(3, "A", "C", "B");

  escreva("Raiz quadrada pelo metodo de Newton:");
  escreva(raiz(2));
  escreva(raiz(144));

  escreva("Numeros em binario:");
  inteiro i = 1;
  enquanto (i <= 64) {
    escreva("  " + binario(i));
    i = i * 4;
  }

  escreva("Collatz: o numero ate 30 com o caminho mais longo");
  inteiro melhor = 1;
  inteiro maior = 0;
  inteiro n = 1;
  enquanto (n <= 30) {
    inteiro passos = collatz(n);
    se (passos > maior) {
      maior = passos;
      melhor = n;
    }
    n = n + 1;
  }
  escreva(melhor);
  escreva(maior);
  escreva(maior > 100 e melhor % 2 == 1);
}
