# Projeto: Análise de Grafos — Lista vs Matriz

Este repositório contém uma implementação de estruturas e algoritmos sobre grafos
e scripts para comparação de desempenho entre **Lista de Adjacência** e **Matriz de Adjacência**.

## Arquivos principais
- `grafos_lib.py`: implementação de `Lista_Grafo` (indexação 0-based) — leitura, BFS, DFS, componentes.
- `grafos_lib_matrix.py`: implementação de `Grafo_Matriz` (indexação 1-based) usando NumPy; inclui `from_file`, `criar_matriz_adjacencias`, e impressão da matriz.
- `casos_teste.py`: scripts de teste e análise (medição de tempo, memória; BFS amostral; componentes; diâmetro; plotting opcional).
- `main.py`: interface interativa (permite escolher Lista ou Matriz e executar relatórios/algoritmos).

## Resumo das decisões de projeto
- Código modular: separação de responsabilidades (leitura/algoritmos/benchmarks/CLI).
- Medições: `time.perf_counter()` para tempo; `tracemalloc` para picos de memória.
- Heurística de diâmetro: cálculo exato (N BFS) para N ≤ 10.000; heurística _double-sweep_ com amostras para N > 10.000.

## Resumo dos resultados (saída de execução dos scripts)
> Execução usada: `python3 casos_teste.py collaboration_graph.txt as_graph.txt`

### Estudo de Caso 1 — Grafo de Colaboração
- Vértices: 71998 | Arestas: 123379
- Memória de carregamento (pico):
  - Lista: 26.89 MB
  - Matriz: 4951.70 MB (~4.95 GB)
- Tempo de BFS (medido):
  - Lista (vértice 0): ~0.0429 s
  - Matriz (vértice 1): ~1.1629 s
- Componentes Conexos:
  - N° de componentes: 14.384
  - Maior componente: 33.533 vértices
  - Menor componente: 1 vértice

### Estudo de Caso 2 — AS Graph (Internet)
- Vértices: 32385 | Arestas: 46736
- Carregamento: 0.2362 s | Pico Mem: 10.08 MB
- BFS (origem 0): 0.0171 s
- Componentes: 1 (grafo conectado)
- Grau:
  - Maior grau: 2159
  - Menor grau: 1
  - Maior possível (N-1): 32384
- Excentricidade (a partir de 0): 6
- Diâmetro (estimado via heurística): 11

## Observações e recomendações
- Para grafos esparsos, preferir Lista de Adjacência (memória e velocidade melhores).
- Matrizes só para grafos pequenos ou operações vetoriais específicas.
- Para diâmetro em grafos grandes: usar a heurística double-sweep; calcular diâmetro exato apenas quando N ≤ 10.000.

## Como reproduzir os resultados
1) Instalar dependências:
```bash
pip install -r requirements.txt
```
2) Gerar métricas dos dois grafos:
```bash
python3 casos_teste.py collaboration_graph.txt as_graph.txt
```
3) Alternativamente, usar interface interativa para matriz/lista:
```bash
python3 main.py <arquivo_entrada>
```

## Geração de gráfico da distribuição de graus (AS Graph)
`casos_teste.py` tenta gerar um plot em `degree_distribution_AS_<N>.png` usando `matplotlib`.
Se `matplotlib` não estiver instalado, instale via `pip install -r requirements.txt`.

## Saída gerada pelo projeto
- Arquivos de resumo: `resumo_grafo_lista.txt`, `resumo_grafo_matriz.txt`, `busca_largura_*.txt`, `componentes_conexos_*.txt`.

## Extensões e próximos passos sugeridos
- Exportar as métricas para CSV/JSON para facilitar análises comparativas.
- Implementar CLI para `main.py` com flags de configuração (`--representation`, `--amostra-bfs`, `--plot`, `--diametro-exato`).
- Incluir testes unitários e ferramentas de validação para os métodos principais (BFS, DFS, componentes, leitura de arquivo).

## Contato / Autor
- Repositório: (https://github.com/BrunoBritOliv/Grafos.git)
- Autor do relatório: William Soares / Bruno Brito

**Observação**: Para reproduzir exatamente os resultados registrados no relatório, execute os scripts com os arquivos `collaboration_graph.txt` e `as_graph.txt` providos e use as mediçãoes exibidas.

Fim
