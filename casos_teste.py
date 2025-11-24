import sys
import time
import tracemalloc
import numpy as np

# Importa as classes de grafo. O script assume:
# - Lista_Grafo (grafos_lib.py): Indexação 0-based (vértices 0 a N-1).
# - Grafo_Matriz (grafos_lib_matrix.py): Indexação 1-based (vértices 1 a N).
from grafos_lib import Lista_Grafo
from grafos_lib_matrix import Grafo_Matriz

# Definir limites de recursão para DFS/Componentes Conexos em grafos grandes.
# O valor 100.000 é necessário para grafos com caminhos longos (72k vértices).
sys.setrecursionlimit(100000)

# --- FUNÇÃO AUXILIAR DE TESTE DE DESEMPENHO ---

def testar_desempenho(grafo_class, arquivo: str, nome_representacao: str, vertice_inicio: int):
    """Mede o tempo e memória para carregamento, BFS e Componentes Conexos."""
    
    resultados = {}
    print(f"\n--- Testando {nome_representacao} ({grafo_class.__name__}) ---")
    
    # 1. Carregamento e Memória
    tracemalloc.start()
    t0 = time.perf_counter()
    try:
        # Usa o método de carregamento apropriado para cada classe
        if nome_representacao.startswith("Lista"):
            grafo = grafo_class.ler_de_arquivo(arquivo)
        else: # Grafo_Matriz
            grafo = grafo_class.from_file(arquivo)
            
    except Exception as e:
        print(f"Erro ao carregar o grafo {nome_representacao}: {e}")
        tracemalloc.stop()
        return None, None
        
    t_carregamento = time.perf_counter() - t0
    # mem_pico: memória máxima alocada
    mem_atual, mem_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    resultados['carregamento_tempo'] = t_carregamento
    # Converte para Megabytes (MB)
    resultados['carregamento_memoria_MB'] = mem_pico / 1024**2
    resultados['n_vertices'] = grafo.n
    resultados['n_arestas'] = grafo.num_arestas
    
    print(f"Vértices: {grafo.n}, Arestas: {grafo.num_arestas}")
    print(f"Tempo de Carregamento: {t_carregamento:.4f} s")
    print(f"Memória Pico (Carregamento): {resultados['carregamento_memoria_MB']:.2f} MB")
    
    
    # 2. Busca em Largura (BFS) - Pior Caso
    tracemalloc.start()
    t0 = time.perf_counter()
    grafo.busca_largura(vertice_inicio)
    t_bfs = time.perf_counter() - t0
    mem_atual, mem_pico_bfs = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    resultados['bfs_tempo'] = t_bfs
    print(f"Tempo de Execução (BFS - Início {vertice_inicio}): {t_bfs:.4f} s")
    print(f"Memória Pico (BFS): {mem_pico_bfs / 1024**2:.2f} MB")
    
    
    # 3. Componentes Conexos
    tracemalloc.start()
    t0 = time.perf_counter()
    componentes = grafo.componentes_conexos()
    t_comp = time.perf_counter() - t0
    mem_atual, mem_pico_comp = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    resultados['comp_tempo'] = t_comp
    resultados['comp_memoria_pico_MB'] = mem_pico_comp / 1024**2
    resultados['n_componentes'] = len(componentes)
    
    # Simplifica a obtenção do tamanho, tratando a lista de componentes
    if componentes:
        tamanhos = [len(c) for c in componentes]
        resultados['max_comp_size'] = max(tamanhos)
        resultados['min_comp_size'] = min(tamanhos)
    else:
        resultados['max_comp_size'] = 0
        resultados['min_comp_size'] = 0
    
    print(f"Tempo de Execução (Componentes): {t_comp:.4f} s")
    print(f"N° Componentes: {resultados['n_componentes']}")
    print(f"Maior Componente: {resultados['max_comp_size']}")
    print(f"Menor Componente: {resultados['min_comp_size']}")
    
    return grafo, resultados

# --- FUNÇÃO PARA CÁLCULO DE DIÂMETRO (Exige O(N * (N+E))) ---

def calcular_diametro(grafo: Lista_Grafo, nome_grafo: str):
    """Calcula o diâmetro (maior caminho mínimo) do grafo usando N BFS."""
    
    print(f"\n--- Calculando Diâmetro para {nome_grafo} ---")
    
    # Para grafos muito grandes, como o AS Graph, calcular N*BFS é proibitivo.
    # Limitamos o número de vértices testados para obter uma estimativa rápida.
    if grafo.n > 10000:
        vertices_para_testar = min(50, grafo.n)
        print(f"AVISO: O grafo tem {grafo.n} vértices. O diâmetro completo é muito lento.")
        print(f"Calculando apenas a excentricidade dos primeiros {vertices_para_testar} vértices como ESTIMATIVA.")
    else:
        vertices_para_testar = grafo.n

    max_distancia_encontrada = 0
    t0 = time.perf_counter()
    
    # A Lista_Grafo usa indexação 0-based
    for v_inicio in range(grafo.n):
            
        if v_inicio >= vertices_para_testar:
            break
            
        # Executa a BFS a partir do vértice v_inicio
        # Pai, Nível = busca_largura(v_inicio)
        try:
            pai, nivel = grafo.busca_largura(v_inicio)
        except Exception as e:
            print(f"Erro na BFS a partir de {v_inicio}: {e}")
            continue

        # O maior nível é a excentricidade do vértice
        excentricidade = max(n for n in nivel if n != -1) # Ignora vértices inacessíveis (-1)
        
        if excentricidade > max_distancia_encontrada:
            max_distancia_encontrada = excentricidade
            
        # Exibir progresso
        if v_inicio % 10 == 0 and v_inicio > 0:
            print(f"Progresso: {v_inicio}/{vertices_para_testar}. Diâmetro parcial: {max_distancia_encontrada}")
            
    t_diametro = time.perf_counter() - t0
    
    print(f"\nDiâmetro estimado / Diâmetro Máximo encontrado: {max_distancia_encontrada}")
    print(f"Tempo total gasto: {t_diametro:.2f} segundos")
    
    return max_distancia_encontrada

# --- EXECUÇÃO PRINCIPAL DOS ESTUDOS DE CASO ---

def main_testes():
    
    if len(sys.argv) != 3:
        print("Uso correto:")
        print("python3 estudo_casos.py collaboration_graph.txt as_graph.txt")
        sys.exit(1)

    COLLAB_FILE = sys.argv[1]
    AS_FILE = sys.argv[2]
    
    print("==============================================")
    print("  INICIANDO TESTES DO TRABALHO DE GRAFOS")
    print("==============================================")

    # ==========================================================
    #                 ESTUDO DE CASO 1: COLABORAÇÃO
    # ==========================================================
    
    print("\n\n##################################################")
    print("## ESTUDO DE CASO 1: GRAFO DE COLABORAÇÃO")
    print("##################################################")
    
    # --- 1, 2 e 3: Teste de Desempenho e Componentes Conexos ---
    
    # 1. Lista de Adjacência (0-based)
    grafo_l_collab, res_l = testar_desempenho(Lista_Grafo, COLLAB_FILE, "Lista de Adjacência", vertice_inicio=0)
    
    # 2. Matriz de Adjacência (1-based). Pode falhar por memória (N^2 ~ 5 GB).
    grafo_m_collab, res_m = testar_desempenho(Grafo_Matriz, COLLAB_FILE, "Matriz de Adjacência", vertice_inicio=1)

    print("\n--- Sumário EC1 ---")
    print(f"1. Memória Lista (MB): {res_l['carregamento_memoria_MB']:.2f}")
    if res_m:
        print(f"   Memória Matriz (MB): {res_m['carregamento_memoria_MB']:.2f}")
        print(f"2. Tempo BFS Lista (s): {res_l['bfs_tempo']:.4f}")
        print(f"   Tempo BFS Matriz (s): {res_m['bfs_tempo']:.4f}")
    print(f"3. Componentes: {res_l['n_componentes']} | Maior: {res_l['max_comp_size']} | Menor: {res_l['min_comp_size']}")

    # ==========================================================
    #                 ESTUDO DE CASO 2: AS GRAPH
    # ==========================================================
    
    print("\n\n##################################################")
    print("## ESTUDO DE CASO 2: AS GRAPH (INTERNET)")
    print("##################################################")
    
    # Usar APENAS a Lista de Adjacência, pois a Matriz é inviável para este grafo.
    grafo_l_as, res_l_as = testar_desempenho(Lista_Grafo, AS_FILE, "Lista de Adjacência (AS)", vertice_inicio=0)

    if grafo_l_as:
        # 1. Obter Graus (Mínimo e Máximo)
        print("\n--- 1. Análise de Graus ---")
        # A Lista_Grafo usa um dicionário, então iteramos sobre os valores.
        graus = [len(vizinhos) for vizinhos in grafo_l_as.adj.values()]
        
        max_grau = max(graus)
        min_grau = min(graus)
        
        print(f"Maior Grau do Grafo: {max_grau}")
        print(f"Menor Grau do Grafo: {min_grau}")
        print(f"Maior Grau Possível (N-1): {grafo_l_as.n - 1}")

        # 2. Componentes Conexos (Já obtido no testar_desempenho)
        print("\n--- 2. Componentes Conexos ---")
        print(f"N° Componentes: {res_l_as['n_componentes']}")
        print(f"Maior Componente: {res_l_as['max_comp_size']}")
        print(f"Menor Componente: {res_l_as['min_comp_size']}")

        # 3. Busca em Largura a partir do Vértice 1 (Excentricidade)
        print("\n--- 3. Excentricidade do Vértice 1 (ou 0) ---")
        # Inicia no vértice 0 (para 0-based Lista_Grafo)
        pai, nivel = grafo_l_as.busca_largura(0) 
        max_nivel_v0 = max(n for n in nivel if n != -1)
        
        print(f"Maior Nível (Distância Máxima) a partir do Vértice 0: {max_nivel_v0}")
        print("Conclusão esperada: Este valor é baixo (propriedade de Mundo Pequeno).")
        
        # 4. Diâmetro da Internet
        diametro = calcular_diametro(grafo_l_as, "AS Graph")
        print(f"\n[FIM] Diâmetro Final Estimado (AS Graph): {diametro}")
        
    print("\n==============================================")
    print("TESTES CONCLUÍDOS. VERIFIQUE OS RESULTADOS.")
    print("==============================================")

if __name__ == "__main__":
    main_testes()