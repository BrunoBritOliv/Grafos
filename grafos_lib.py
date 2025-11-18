class Grafo:
    def __init__(self, num_vertices: int):
        
        self.n = num_vertices
        self.adj = {i: [] for i in range(num_vertices)}
        self.num_arestas = 0

    # Leitura do arquivo: Lembrar de definir o nome do arquivo

    @staticmethod
    def from_file(arquivo: str):
        
        with open(arquivo, "r") as f:
            linhas = f.read().strip().split("\n")

        n = int(linhas[0])
        grafo = Grafo(n)

        for linha in linhas[1:]:
            if linha.strip() == "":
                continue
            u, v = map(int, linha.split())
            grafo.add_arestas(u, v)

        return grafo

    # Adiciona arestas não direcionadas

    def add_arestas(self, u: int, v: int):
    
        self.adj[u].append(v)
        self.adj[v].append(u)
        self.num_arestas += 1

    # Gera arquivo de saída com:
    #número de vértices, número de arestas, grau de cada vértice

    def save_resumo(self, arquivo: str):
        
        with open(arquivo, "w") as f:
            f.write(f"Vértices: {self.n}\n")
            f.write(f"Arestas: {self.num_arestas}\n")
            f.write("Graus:\n")
            for v in range(self.n):
                f.write(f"vértice {v}: grau {len(self.adj[v])}\n")

    # Busca em Largura

    def busca_largura(self, inicio: int):
       
        from collections import deque

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
            f.write(f"Árvore de Busca em Largura a partir do vértice {inicio}\n")
            for v in range(self.n):
                f.write(f"vértice {v}: pai = {pai[v]}, nível = {nivel[v]}\n")

   
    # Busca em Profundidade
    
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
            f.write(f"Árvore de busca em profundidade a partir do vértice {inicio}\n")
            for v in range(self.n):
                f.write(f"vértice {v}: pai = {pai[v]}, nível = {nivel[v]}\n")

    
    # Cmponentes conexos
   
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
                componente.append(componente)

        return componentes

    def salvar_componentes(self, arquivo: str):
        componentes = self.componentes_conexos()

        with open(arquivo, "w") as f:
            f.write(f"Número de componentes conexas: {len(componentes)}\n\n")

            for i, componente in enumerate(componentes):
                f.write(f"Componente {i} — tamanho {len(componente)}\n")
                f.write("Vértices: " + " ".join(map(str, componente)) + "\n\n")

