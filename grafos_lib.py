import sys
import numpy as np
from collections import deque


sys.setrecursionlimit(100000)

class Lista_Grafo:
    def __init__(self, num_vertices: int):
        
        self.n = num_vertices
        self.adj = {i: [] for i in range(num_vertices)}
        self.num_arestas = 0

    @staticmethod
    def ler_de_arquivo(arquivo: str):
        
        with open(arquivo, "r") as f:
            linhas = f.read().strip().split("\n")

        n = int(linhas[0])
        grafo = Lista_Grafo(n)

        for linha in linhas[1:]:
            if linha.strip() == "":
                continue
            u, v = map(int, linha.split())
            
            u_0 = u - 1
            v_0 = v - 1
            
            if u_0 < 0 or u_0 >= n or v_0 < 0 or v_0 >= n:
                 print(f"Aviso: Vértice(s) ({u}, {v}) fora do intervalo [1, {n}] ignorado(s).")
                 continue
                 
            grafo.add_arestas(u_0, v_0)

        return grafo

    def add_arestas(self, u: int, v: int):
    
        if v not in self.adj[u]: 
            self.adj[u].append(v)
            self.adj[v].append(u)
            self.num_arestas += 1

    def salvar_resumo(self, arquivo: str):
        
        with open(arquivo, "w") as f:
            f.write(f"Vértices: {self.n}\n")
            f.write(f"Arestas: {self.num_arestas}\n")
            f.write("Graus:\n")
            for v in range(self.n):
                f.write(f"vértice {v+1}: grau {len(self.adj[v])}\n")

    def busca_largura(self, inicio: int):
       
        visitado = [False] * self.n
        pai  = [-1] * self.n
        nivel   = [-1] * self.n

        fila = deque([inicio])
        visitado[inicio] = True
        nivel[inicio] = 0

        while fila:
            u = fila.popleft()
            for v in self.adj[u]:
                if not visitado[v]:
                    visitado[v] = True
                    pai[v] = u
                    nivel[v] = nivel[u] + 1
                    fila.append(v)

        return pai, nivel

    def salvar_busca_largura(self, inicio: int, arquivo: str):
        
        pai, nivel = self.busca_largura(inicio)

        with open(arquivo, "w") as f:
            f.write(f"Árvore de Busca em Largura a partir do vértice {inicio+1}\n")
            for v in range(self.n):
                pai_1based = pai[v] + 1 if pai[v] != -1 else -1
                f.write(f"vértice {v+1}: pai = {pai_1based}, nível = {nivel[v]}\n")

    
    def busca_profundidade(self, inicio: int):
        visitado = [False] * self.n
        pai  = [-1] * self.n
        nivel   = [-1] * self.n

        def visitar(u, profundidade):
            visitado[u] = True
            nivel[u] = profundidade
            for v in self.adj[u]:
                if not visitado[v]:
                    pai[v] = u
                    visitar(v, profundidade + 1)

        visitar(inicio, 0)
        return pai, nivel

    def salvar_busca_profundidade(self, inicio: int, arquivo: str):
        pai, nivel = self.busca_profundidade(inicio)

        with open(arquivo, "w") as f:
            f.write(f"Árvore de busca em profundidade a partir do vértice {inicio+1}\n")
            for v in range(self.n):
                pai_1based = pai[v] + 1 if pai[v] != -1 else -1
                f.write(f"vértice {v+1}: pai = {pai_1based}, nível = {nivel[v]}\n")

    
    def componentes_conexos(self):
        
        visitado = [False] * self.n
        componentes = []

        def dfs_coletar(u, componente):
            visitado[u] = True
            componente.append(u)
            for v in self.adj[u]:
                if not visitado[v]:
                    dfs_coletar(v, componente)

        for v in range(self.n):
            if not visitado[v]:
                componente = []
                dfs_coletar(v, componente)
                
                componentes.append(componente)

        return componentes

    def salvar_componentes(self, arquivo: str):
        componentes = self.componentes_conexos()

        with open(arquivo, "w") as f:
            f.write(f"Número de componentes conexas: {len(componentes)}\n\n")

            for i, componente_0based in enumerate(componentes):
                # Converte os vértices para 1-based na saída
                componente_1based = [v + 1 for v in componente_0based]
                f.write(f"Componente {i+1} — tamanho {len(componente_1based)}\n")
                f.write("Vértices: " + " ".join(map(str, componente_1based)) + "\n\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso correto:")
        print("python3 grafos_lib.py arquivo_entrada.txt")
        sys.exit(1)
    
    texto_entrada = sys.argv[1]
    grafo = Lista_Grafo.ler_de_arquivo(texto_entrada) 
    resumo_saida = "resumo_grafo_lista.txt"
    grafo.salvar_resumo(resumo_saida) 
    print(f"Resumo do grafo salvo em '{resumo_saida}'")