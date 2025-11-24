import sys
import numpy as np

class Grafo_Matriz:
    def __init__(self, num_vertices: int):
        
        self.n = num_vertices
        
        self.adj = np.zeros((num_vertices + 1, num_vertices + 1), dtype=np.uint8)
        
        self.num_arestas = 0

    
    @staticmethod
    def from_file(arquivo: str):
        
        with open(arquivo, "r") as f:
            linhas = f.read().strip().split("\n")

        try:
            n = int(linhas[0].strip())
        except IndexError:
            raise ValueError("O arquivo está vazio ou não possui o número de vértices na primeira linha.")

        grafo = Grafo_Matriz(n)

        for linha in linhas[1:]:
            if linha.strip() == "":
                continue
            
            try:
                u, v = map(int, linha.split())
                grafo.add_arestas(u, v)
            except ValueError:
                print(f"Aviso: Linha inválida ignorada: {linha}")
            except IndexError:
                print(f"Erro: Aresta ({u}, {v}) inválida. Vértice(s) fora do intervalo [1, {n}].")


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