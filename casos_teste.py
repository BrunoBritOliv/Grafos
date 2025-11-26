import sys
import time
import tracemalloc
import numpy as np
import random

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None
    # Plotting is optional; we'll warn users later if trying to plot without matplotlib

# Importa as classes de grafo. O script assume:
# - Lista_Grafo (grafos_lib.py): Indexação 0-based (vértices 0 a N-1).
# - Grafo_Matriz (grafos_lib_matrix.py): Indexação 1-based (vértices 1 a N).
from grafos_lib import Lista_Grafo
from grafos_lib_matrix import Grafo_Matriz

# Definir limites de recursão para DFS/Componentes Conexos em grafos grandes.
# O valor 100.000 é necessário para grafos com caminhos longos (72k vértices).
sys.setrecursionlimit(100000)

# --- FUNÇÃO AUXILIAR DE TESTE DE DESEMPENHO ---

def testar_desempenho(grafo_class, arquivo: str, nome_representacao: str, vertice_inicio: int, amostra_bfs_count: int = 0):
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

    # Opcional: Executar amostragem de BFS para estimar o 'pior caso' de tempo
    if amostra_bfs_count and amostra_bfs_count > 0:
        # Seleciona vértices para testar: primeiro (inicio), maior grau, menor grau e aleatórios
        try:
            if isinstance(grafo.adj, dict):
                keys_vertices = list(grafo.adj.keys())
                degrees_dict = {v: len(nei) for v, nei in grafo.adj.items()}
            else:
                # Matriz (numpy): soma por linha. Inclui índice 0 no grafo matriz.
                keys_vertices = list(range(len(grafo.adj)))
                degrees_arr = np.sum(grafo.adj, axis=1).tolist()
                degrees_dict = {i: int(degrees_arr[i]) for i in keys_vertices}
        except Exception:
            keys_vertices = list(range(grafo.n))
            degrees_dict = {i: 0 for i in keys_vertices}

        max_deg_vertex = max(degrees_dict, key=degrees_dict.get)
        min_deg_vertex = min(degrees_dict, key=degrees_dict.get)
        sample_vertices = [vertice_inicio, max_deg_vertex, min_deg_vertex]
        # adiciona alguns aleatórios, respeitando o número pedido
        extras_count = max(0, amostra_bfs_count - len(sample_vertices))
        random.seed(1)
        if extras_count > 0:
            extras = random.sample(keys_vertices, min(extras_count, len(keys_vertices)))
            for v in extras:
                if v not in sample_vertices:
                    sample_vertices.append(v)

        # Executa BFS nas amostras e registra o maior tempo
        tempos_amostra = []
        for v in sample_vertices:
            tracemalloc.start()
            t0_v = time.perf_counter()
            pai_v, nivel_v = grafo.busca_largura(v)
            t_v = time.perf_counter() - t0_v
            mem_now, mem_peak_v = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            tempos_amostra.append((v, t_v, mem_peak_v / 1024**2))
            print(f"BFS amostra v={v}: tempo {t_v:.4f}s, pico MB {mem_peak_v/1024**2:.2f}")

        # Escolhe o tempo máximo e monta no dicionário
        tempos_sorted = sorted(tempos_amostra, key=lambda x: x[1], reverse=True)
        resultados['bfs_worst_tempo'] = tempos_sorted[0][1]
        resultados['bfs_worst_vertice'] = tempos_sorted[0][0]
    
    
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
    
    # Para grafos muito grandes, calcular N BFS é proibitivo.
    # Abordagem:
    # - Se o grafo é pequeno (<= 10000 vértices) realizamos BFS a partir de todos.
    # - Caso contrário usamos heurística (double-sweep) a partir de amostra de vértices.
    max_distancia_encontrada = 0
    t0 = time.perf_counter()

    if grafo.n <= 10000:
        vertices_para_testar = grafo.n
        print(f"O grafo tem {grafo.n} vértices. Calculando diâmetro exato (N BFS).")
        for v_inicio in range(grafo.n):
            try:
                pai, nivel = grafo.busca_largura(v_inicio)
            except Exception as e:
                print(f"Erro na BFS a partir de {v_inicio}: {e}")
                continue
            excentricidade = max(n for n in nivel if n != -1)
            max_distancia_encontrada = max(max_distancia_encontrada, excentricidade)
            if v_inicio % 50 == 0 and v_inicio > 0:
                print(f"Progresso: {v_inicio}/{vertices_para_testar}. Diâmetro parcial: {max_distancia_encontrada}")
    else:
        # Heurística: double-sweep em uma amostra de vértices (melhor estimativa do diâmetro)
        sample_size = min(100, grafo.n)
        print(f"AVISO: O grafo tem {grafo.n} vértices. Calculando diâmetro estimado com heurística (double-sweep) usando {sample_size} amostras.)")

        # Seleciona vértices amostrados uniformemente e alguns aleatórios
        all_vertices = list(grafo.adj.keys()) if isinstance(grafo.adj, dict) else list(range(grafo.n))
        step = max(1, len(all_vertices) // sample_size)
        sample = [all_vertices[i] for i in range(0, len(all_vertices), step)][:sample_size]
        # Adiciona alguns vértices aleatórios para diversificar a amostra
        random.seed(42)
        extras = random.sample(all_vertices, min(10, len(all_vertices)))
        for v in extras:
            if v not in sample:
                sample.append(v)

        for idx, v_inicio in enumerate(sample):
            try:
                _, nivel = grafo.busca_largura(v_inicio)
            except Exception as e:
                print(f"Erro na BFS a partir de {v_inicio}: {e}")
                continue
            # Encontrar vértice mais distante u
            # Observação: nivel é uma lista com níveis (ou -1)
            max_nivel = max(n for n in nivel if n != -1)
            # o vértice mais distante: pega índex do nível máximo
            farthest_indices = [i for i, lvl in enumerate(nivel) if lvl == max_nivel]
            u = farthest_indices[0]
            # BFS a partir de u
            try:
                _, nivel2 = grafo.busca_largura(u)
            except Exception as e:
                print(f"Erro na BFS a partir de {u}: {e}")
                continue
            candidate = max(n for n in nivel2 if n != -1)
            if candidate > max_distancia_encontrada:
                max_distancia_encontrada = candidate
            if idx % 10 == 0 and idx > 0:
                print(f"Progresso: {idx+1}/{len(sample)} amostras. Diâmetro parcial: {max_distancia_encontrada}")

    t_diametro = time.perf_counter() - t0

    print(f"\nDiâmetro estimado / Diâmetro Máximo encontrado: {max_distancia_encontrada}")
    print(f"Tempo total gasto: {t_diametro:.2f} segundos")
    return max_distancia_encontrada


def plot_degree_distribution(graus, nome_grafo: str, out_file: str = None):
    """Plota o histograma e a sequência de graus do grafo, se matplotlib estiver disponível."""
    if plt is None:
        print("Aviso: matplotlib não está disponível. Ignorando plotagem.")
        return None

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.hist(graus, bins=50, color='C0', alpha=0.8)
    plt.xlabel('Grau')
    plt.ylabel('Número de Vértices')
    plt.title(f'Distribuição de Graus - {nome_grafo}')

    plt.subplot(1, 2, 2)
    graus_sorted = sorted(graus, reverse=True)
    plt.plot(graus_sorted, marker='.', linestyle='-', color='C1')
    plt.xlabel('Índice (ordenado)')
    plt.ylabel('Grau')
    plt.title(f'Sequência de Graus - {nome_grafo}')
    plt.tight_layout()

    if out_file:
        try:
            plt.savefig(out_file)
            print(f"Plot salvo em: {out_file}")
        except Exception as e:
            print(f"Erro ao salvar plot: {e}")
    else:
        plt.show()

    return out_file


def testar_bfs_varios(grafo: Lista_Grafo, vertices, nome_grafo: str):
    """Executa BFS em vários vértices, mede tempo e excentricidade. Retorna lista de resultados."""
    resultados = []
    print(f"\nExecutando BFS em {len(vertices)} vértices de {nome_grafo}...")
    for v in vertices:
        tracemalloc.start()
        t0 = time.perf_counter()
        try:
            pai, nivel = grafo.busca_largura(v)
        except Exception as e:
            print(f"Erro na BFS a partir de {v}: {e}")
            tracemalloc.stop()
            continue
        t_bfs = time.perf_counter() - t0
        mem_atual, mem_pico_bfs = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        reachable = [n for n in nivel if n != -1]
        max_nivel = max(reachable) if reachable else -1
        unreachable_count = sum(1 for n in nivel if n == -1)

        resultados.append({
            'vertice': v,
            'bfs_tempo': t_bfs,
            'bfs_mem_pico_MB': mem_pico_bfs / 1024**2,
            'max_nivel': max_nivel,
            'unreachable': unreachable_count
        })

        print(f"Vértice {v} -> Tempo: {t_bfs:.4f}s | Pico Memória: {mem_pico_bfs/1024**2:.2f} MB | Max nível: {max_nivel} | Inacessíveis: {unreachable_count}")

    return resultados

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
    grafo_l_collab, res_l = testar_desempenho(Lista_Grafo, COLLAB_FILE, "Lista de Adjacência", vertice_inicio=0, amostra_bfs_count=5)
    
    # 2. Matriz de Adjacência (1-based). Pode falhar por memória (N^2 ~ 5 GB).
    grafo_m_collab, res_m = testar_desempenho(Grafo_Matriz, COLLAB_FILE, "Matriz de Adjacência", vertice_inicio=1, amostra_bfs_count=5)

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
    grafo_l_as, res_l_as = testar_desempenho(Lista_Grafo, AS_FILE, "Lista de Adjacência (AS)", vertice_inicio=0, amostra_bfs_count=5)

    if grafo_l_as:
        # 1. Obter Graus (Mínimo e Máximo)
        print("\n--- 1. Análise de Graus ---")
        # A Lista_Grafo usa um dicionário, então iteramos sobre os valores.
        degrees_dict = {v: len(vizinhos) for v, vizinhos in grafo_l_as.adj.items()}
        graus = list(degrees_dict.values())
        
        max_grau = max(graus)
        min_grau = min(graus)
        
        print(f"Maior Grau do Grafo: {max_grau}")
        print(f"Menor Grau do Grafo: {min_grau}")
        print(f"Maior Grau Possível (N-1): {grafo_l_as.n - 1}")

        # Salvar plot de distribuição de graus (se matplotlib disponível)
        out_plot = f"degree_distribution_AS_{grafo_l_as.n}.png"
        plot_degree_distribution(graus, "AS Graph", out_file=out_plot)

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
        # Repetir BFS para outros vértices (amostra: 0, máximo grau, mínimo grau, alguns aleatórios)
        keys_vertices = list(degrees_dict.keys())
        max_deg_vertex = max(degrees_dict, key=degrees_dict.get)
        min_deg_vertex = min(degrees_dict, key=degrees_dict.get)
        sample_vertices = [0, max_deg_vertex, min_deg_vertex]
        # adiciona alguns vértices aleatórios diferentes
        random.seed(123)
        rand_count = min(5, len(keys_vertices))
        rand_vertices = random.sample(keys_vertices, rand_count)
        for v in rand_vertices:
            if v not in sample_vertices:
                sample_vertices.append(v)

        print(f"\nExecutando BFS em vértices de amostra: {sample_vertices}")
        bfs_res = testar_bfs_varios(grafo_l_as, sample_vertices, "AS Graph")
        
        # 4. Diâmetro da Internet
        diametro = calcular_diametro(grafo_l_as, "AS Graph")
        print(f"\n[FIM] Diâmetro Final Estimado (AS Graph): {diametro}")
        
    print("\n==============================================")
    print("TESTES CONCLUÍDOS. VERIFIQUE OS RESULTADOS.")
    print("==============================================")

if __name__ == "__main__":
    main_testes()