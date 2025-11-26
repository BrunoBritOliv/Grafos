import sys
import numpy as np

class Grafo_Matriz:
    def __init__(self, num_vertices: int):
        
        self.n = num_vertices
        
        self.adj = np.zeros((num_vertices + 1, num_vertices + 1), dtype=np.uint8)
        
        self.num_arestas = 0

    
    @staticmethod
    def from_file(arquivo: str):
        # Usa o método estático criar_matriz_adjacencias para ler arquivo de forma robusta.
        matriz = Grafo_Matriz.criar_matriz_adjacencias(arquivo)
        if matriz is None:
            raise ValueError("Falha ao criar matriz de adjacências a partir do arquivo.")

        # Determina N a partir da forma da matriz (n+1 por conta do índice 0 não usado)
        N = matriz.shape[0] - 1
        grafo = Grafo_Matriz(N)
        grafo.adj = matriz
        # Conta arestas: cada aresta é contada duas vezes na matriz (i,j) e (j,i)
        grafo.num_arestas = int(np.sum(matriz) // 2)
        return grafo


    def add_arestas(self, u: int, v: int):
    
        if u < 0 or u > self.n or v < 0 or v > self.n:
            raise IndexError(f"Vértice(s) fora do intervalo [1, {self.n}]")

        if self.adj[u, v] == 0: 
            self.adj[u, v] = 1 # A->B
            self.adj[v, u] = 1 # B->A (Não-direcionado)
            self.num_arestas += 1

    def save_resumo(self, arquivo: str):
        
        graus = np.sum(self.adj, axis=1)

        with open(arquivo, "w") as f:
            f.write(f"Vértices: {self.n}\n")
            f.write(f"Arestas: {self.num_arestas}\n")
            f.write("Graus:\n")
            for v in range( self.n + 1):
                f.write(f"vértice {v}: grau {graus[v]}\n")

    
    def busca_largura(self, inicio: int):
       
        from collections import deque

        visitado = np.zeros(self.n + 1, dtype=bool)
        pai  = np.full(self.n + 1, -1, dtype=np.int32)
        nivel   = np.full(self.n + 1, -1, dtype=np.int32)

        fila = deque([inicio])
        visitado[inicio] = True
        nivel[inicio] = 0

        while fila:
            u = fila.popleft()
            
            vizinhos = np.where(self.adj[u] == 1)[0] 
            
            for v in vizinhos:
                if v >= 0 and not visitado[v]:
                    visitado[v] = True
                    pai[v] = u
                    nivel[v] = nivel[u] + 1
                    fila.append(v)

        return pai, nivel
    
    
    def salvar_busca_largura(self, inicio: int, arquivo: str):
        
        pai, nivel = self.busca_largura(inicio)

        with open(arquivo, "w") as f:
            f.write(f"Árvore de Busca em Largura a partir do vértice {inicio}\n")
            for v in range(self.n + 1): 
                f.write(f"vértice {v}: pai = {pai[v]}, nível = {nivel[v]}\n")


    def busca_profundidade(self, inicio: int):
        
        
        visitado = np.zeros(self.n + 1, dtype=bool)
        pai = np.full(self.n + 1, -1, dtype=np.int32)
        nivel = np.full(self.n + 1, -1, dtype=np.int32)
        
        def dfs_iterativa(u_inicial):
            stack = [u_inicial] 
            visitado[u_inicial] = True
            nivel[u_inicial] = 0

            while stack:
                u = stack[-1]

                vizinhos = np.where(self.adj[u] == 1)[0]
                proximo_vizinho = None
                
                for v in vizinhos:
                    if v >= 0 and v <= self.n and not visitado[v]:
                        proximo_vizinho = v
                        break 

                if proximo_vizinho is not None:
                    v = proximo_vizinho
                    pai[v] = u
                    nivel[v] = nivel[u] + 1
                    visitado[v] = True
                    stack.append(v)
                    
                else:
                    stack.pop() 

        if inicio >= 0 and inicio <= self.n and not visitado[inicio]:
            dfs_iterativa(inicio)

        for u in range(self.n + 1):
            if not visitado[u]: 
                dfs_iterativa(u) 

        return pai, nivel


    def salvar_busca_profundidade(self, inicio: int, arquivo: str):
    
        pai, nivel = self.busca_profundidade(inicio) 

        with open(arquivo, "w") as f:
            f.write(f"Árvore de Busca em Profundidade (DFS) a partir do vértice {inicio}\n")
            f.write("Vértice | Pai | Nível (Profundidade)\n") 
            f.write("-" * 40 + "\n")
            
            for v in range(self.n + 1):
                f.write(f"{v} | {pai[v]} | {nivel[v]}\n")


    def componentes_conexos(self):
        
        visitado = np.zeros(self.n + 1, dtype=bool) 
        componentes = []

        for v_inicial in range(self.n + 1):
            
            if not visitado[v_inicial]:
                
                componente_atual = []
                stack = [v_inicial]
                visitado[v_inicial] = True

                while stack:
                    u = stack.pop() 
                    componente_atual.append(u)
                    
                    vizinhos = np.where(self.adj[u] == 1)[0]
                    
                    for v in vizinhos:
                        if v >= 0 and v <= self.n and not visitado[v]: 
                            visitado[v] = True
                            stack.append(v) 
                
                componentes.append(componente_atual) 

        return componentes
    
    def salvar_componentes(self, arquivo: str):
            
            componentes = self.componentes_conexos()

            with open(arquivo, "w") as f:
                f.write(f"Número de componentes conexas: {len(componentes)}\n\n")

                for i, componente in enumerate(componentes):
                    f.write(f"Componente {i+1} — tamanho {len(componente)}\n") 
                    
                    f.write("Vértices: " + " ".join(map(str, componente)) + "\n\n")
    

    @staticmethod
    def criar_matriz_adjacencias(arquivo: str) -> np.ndarray:
        """
        Lê um arquivo de conexões de grafo e cria sua matriz de adjacências.

        O arquivo deve ter:
        - A primeira linha com a quantidade de vértices (N).
        - As linhas seguintes com pares de vértices representando as arestas (v1 v2).

        :param nome_arquivo: O caminho para o arquivo de entrada.
        :return: Uma matriz de adjacências como um array NumPy (uint8).
        """
        try:
            with open(arquivo, 'r') as f:
                try:
                    primeira_linha = f.readline().strip()
                    if primeira_linha == "":
                        print("Erro: Arquivo vazio.")
                        return None

                    if primeira_linha.isdigit():
                        N = int(primeira_linha)
                        print(f"Número de vértices (N) lido: {N}")
                    else:
                        f.seek(0)
                        max_v = 0
                        edges = []
                        for linha_tmp in f:
                            linha_tmp = linha_tmp.strip()
                            if not linha_tmp or linha_tmp.startswith('#'):
                                continue
                            partes = linha_tmp.split()
                            if len(partes) != 2:
                                continue
                            try:
                                u_tmp = int(partes[0])
                                v_tmp = int(partes[1])
                                edges.append((u_tmp, v_tmp))
                                if u_tmp > max_v:
                                    max_v = u_tmp
                                if v_tmp > max_v:
                                    max_v = v_tmp
                            except ValueError:
                                continue
                        if max_v == 0:
                            print("Aviso: Não foi possível inferir N do arquivo; assumindo N=0.")
                            return None
                        N = max_v
                        f.seek(0)
                        print(f"Aviso: Primeira linha não continha N. Inferido N = {N} a partir das arestas.")

                except ValueError:
                    print("Erro: A primeira linha do arquivo deve ser um número inteiro (quantidade de vértices).")
                    return None
                
                matriz_adj = np.zeros((N + 1, N + 1), dtype=np.uint8)
                print(f"Matriz de adjacências {N}x{N} inicializada com tipo {matriz_adj.dtype}.")

                num_arestas = 0
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith('#'):
                        continue
                    
                    try:
                        partes = linha.split()
                        if len(partes) != 2:
                            continue

                        u = int(partes[0])
                        v = int(partes[1])

                        if 1 <= u <= N and 1 <= v <= N:
                            matriz_adj[u, v] = 1
                            matriz_adj[v, u] = 1
                            num_arestas += 1
                        else:
                            print(f"⚠️ Aviso: Vértice fora do limite (1 a {N}): {u} ou {v}. Linha ignorada.")

                    except ValueError:
                        print(f"⚠️ Aviso: Linha inválida ignorada: '{linha}'")
                
                print(f"Processamento concluído. {num_arestas} arestas lidas.")
                return matriz_adj

        except FileNotFoundError:
            print(f"Erro: O arquivo '{arquivo}' não foi encontrado.")
            return None
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            return None

    def representacao_matriz_adjacencias(self) -> None:
        """Imprime a representação da matriz de adjacências (1-based)."""
        N = self.adj.shape[0] - 1
        print("\n--- Matriz de Adjacências ---")
        # Cabeçalhos 1..N
        indices = [str(i) for i in range(1, N+1)]
        print("Vértice | " + " ".join(indices))
        print("\n" * (2))
        for i in range(1, N+1):
            linha_str = " ".join(map(str, self.adj[i, 1:N+1]))
            print(f"    {i}   | {linha_str}")
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso correto:")
        print("python3 main.py arquivo_entrada.txt")
        sys.exit(1)
    
    texto_entrada = sys.argv[1]
    
    grafo = Grafo_Matriz.from_file(texto_entrada)
    resumo_saida = "resumo_grafo.txt"
    grafo.salvar_componentes(resumo_saida)
    print(f"Resumo do grafo salvo em '{resumo_saida}'")