from grafos_lib import Lista_Grafo
from grafos_lib_matrix import Grafo_Matriz
import sys

def main():

    if len(sys.argv) != 2:
        print("Uso correto:")
        print("python3 main.py arquivo_entrada.txt")
        sys.exit(1)
    
    texto_entrada = sys.argv[1]

    print("1 - Usar Lista de Adjacência \n"
          "2 - Usar Matriz de Adjacência")

    escolha = input("Escolha a opção (1 ou 2): ").strip()

    entrada = sys.argv[1]

    if escolha == "1":
        print("\nLista de adjacência escolhida")
        grafo_l = Lista_Grafo.ler_de_arquivo(entrada)
        print("Grafo carregado com sucesso!\n")
        print("Qual função deseja chamar?\n")
        funcao = int(input("1 - Resumo do grafo \n"
                       "2 - Busca em Largura \n"
                       "3 - Busca em Profundidade \n"
                       "4 - Componentes conexos\n"))

        if funcao == 1:
            saida = "resumo_grafo_lista.txt"
            grafo_l.salvar_resumo(saida)
        elif funcao == 2:
            origem = int(input("Defina a origem da busca em largura"))
            saida = "busca_largura_lista.txt"
            grafo_l.salvar_busca_largura(origem, saida)
        elif funcao == 3:
            saida = "busca_profundidade_lista.txt"
            origem = int(input("Defina a origem da busca em profundidade"))
            grafo_l.salvar_busca_profundidade(origem, saida)
        elif funcao == 4:
            saida = "componentes_conexos_lista.txt"
            grafo_l.salvar_componentes(saida)
        else:
            print("Opção inválida!")
            return 

    elif escolha == "2":
        print("\nMatriz de Adjacência escolhida")
        
        grafo = Grafo_Matriz.from_file(entrada)
        
        print("Grafo carregado com sucesso!")

        print("Qual função deseja chamar?")
        funcao = int(input("1 - Resumo do grafo \n"
                       "2 - Busca em Largura \n"
                       "3 - Busca em Profundidade \n"
                       "4 - Componentes conexos"))

        if funcao == 1:
            saida = "resumo_grafo_matriz.txt"
            grafo.save_resumo(saida)
            print(f"Resumo salvo em '{saida}'")
        elif funcao == 2:
            origem = int(input("Defina a origem da busca em largura").strip())
            saida = "busca_largura_matriz.txt"
            grafo.salvar_busca_largura(origem, saida)
            print(f"Busca em Largura salva em '{saida}'")
        elif funcao == 3:
            origem = int(input("Defina a origem da busca em profundidade").strip())
            saida = "busca_profundidade_matriz.txt"
            grafo.salvar_busca_profundidade(origem, saida)
            print(f"Busca em Profundidade salva em '{saida}'")
        elif funcao == 4:
            saida = "componentes_conexos_matriz.txt"
            grafo.salvar_componentes(saida)
            print(f"Componentes Conexos salvos em '{saida}'")
        else:
            print("Opção inválida!")
            return
    

if __name__ == "__main__":
    main()