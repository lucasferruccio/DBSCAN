import math
from matplotlib import pyplot as plt

'''
Algoritmo DBSCAN
1: Rotular todos os pontos como de centro, borda ou ruído
2: Eliminar os pontos de ruído
3: Colocar uma aresta entre todos os pontos de centro que estejam
em vizinhanças uns dos outros
4: Tornar cada grupo de centros conectados um grupo separado
5 : Atribuir cada ponto de limite a um dos grupos de seus pontos de
centro
'''

#Classe do ponto
class Ponto:
    def __init__(self, pos_x, pos_y,):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotulo = "nao identificado"
        self.visitado = False
        self.vizinhos = []

class Aresta:
    def __init__(self, ponto, vizinho):
        self.ponto = ponto
        self.vizinho = vizinho
        self.visitado = False


#Faz a leitura do arquivo e faz o tratamento dos dados
def lerArquivo(arquivo_src):
    arquivo = open(arquivo_src, 'r')

    pontos = []
    leitura_dados = False

    for linha in arquivo.readlines():
        if leitura_dados:
            info_ponto = linha.strip("\n").split(",")
            novoPonto = Ponto(float(info_ponto[0]), float(info_ponto[1]))
            pontos.append(novoPonto)

        if linha == "@DATA\n":
            leitura_dados = True
    return pontos

#Calculo da distancia entre dois pontos (Distancia Euclidiana)
def calculo_distancia(ponto, ponto_vizinho):
    ditancia = math.sqrt(pow(ponto.pos_x - ponto_vizinho.pos_x, 2) + pow(ponto.pos_y - ponto_vizinho.pos_y, 2))
    return ditancia

#Procura os vizinhos de um determinado ponto baseado no epsolon
def procurar_vizinhos(ponto, pontos, eps):
    vizinhos = []
    for ponto_viznho in pontos:
        if ponto != ponto_viznho:
            distancia = calculo_distancia(ponto, ponto_viznho)
            if distancia <= eps:
                vizinhos.append(ponto_viznho)
    return vizinhos

def dbscan(pontos, eps, minpts):


    #Parte 1 -> Rotular os pontos:
    for ponto in pontos:
        ruido = True
        ponto.visitado = True
        pontos_vizinhos = procurar_vizinhos(ponto, pontos, eps)
        ponto.vizinhos = pontos_vizinhos
        if len(pontos_vizinhos) >= minpts:
            ponto.rotulo = "centro"
        else:
            for ponto_vizinho in pontos_vizinhos:
                vizinhos2grau = procurar_vizinhos(ponto_vizinho, pontos, eps)
                if len(vizinhos2grau) >= minpts:
                    ponto.rotulo = "borda"
                    ruido = False
            if ruido:
                ponto.rotulo = "ruido"

    #Parte 2 -> Eliminar os ruidos
    pontos_filtrados = []
    for ponto in pontos:
        if ponto.rotulo != "ruido":
            pontos_filtrados.append(ponto)

    #Parte 3 -> Conectar arestas entre centros vizinhos (Evitando duplicidade):
    arestasCheckUP = []
    arestas = []
    for ponto in pontos_filtrados:
        if ponto.rotulo == "centro":
            for ponto_vizinho in ponto.vizinhos:
                if ponto_vizinho.rotulo == "centro":
                    if (ponto_vizinho,ponto) not in arestasCheckUP:
                        arestasCheckUP.append((ponto_vizinho,ponto))
                        novaAresta = Aresta(ponto_vizinho,ponto)
                        arestas.append(novaAresta)

    # Parte 4 -> Agrupar centros conectados (Utilizando uma pilha)
    clusters = []
    for aresta in arestas:
        if not aresta.visitado:
            cluster = []
            pilha = [aresta.ponto]
            #Expancao pelas arestas
            while pilha:
                ponto_atual = pilha.pop(0)
                if ponto_atual not in cluster:
                    cluster.append(ponto_atual)
                    for aresta_conectada in arestas:
                        if not aresta_conectada.visitado:
                            if aresta_conectada.ponto == ponto_atual:
                                aresta_conectada.visitado = True
                                pilha.append(aresta_conectada.vizinho)
                            elif aresta_conectada.vizinho == ponto_atual:
                                aresta_conectada.visitado = True
                                pilha.append(aresta_conectada.ponto)
            clusters.append(cluster)

    #Parte 5 -> Atribuir cada ponto de borda a um centro (O mais próximo)
    for ponto in pontos_filtrados:
        if ponto.rotulo == "borda":
            centro_proximo = None
            menor_distancia = float("inf")
            for vizinho in ponto.vizinhos:
                if vizinho.rotulo == "centro":
                    distancia = calculo_distancia(ponto, vizinho)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        centro_proximo = vizinho
            for cluster in clusters:
                if centro_proximo in cluster:
                    cluster.append(ponto)

    return clusters

#Plota o gráfico base com os dados iniciais do projeto (Sem tratamento)
def plotarGraficoBase(pontos):
    for ponto in pontos:
        plt.scatter(ponto.pos_x, ponto.pos_y, c = 'b')
    plt.show()


#Plota os gráficos apos a rotulacao dos pontos (CENTRO/RUIDO/BORDA)
def plotarGraficoMeio(pontos):
    for ponto in pontos:
        if ponto.rotulo == "centro":
            plt.scatter(ponto.pos_x, ponto.pos_y, c = "b")
        elif ponto.rotulo == "borda":
            plt.scatter(ponto.pos_x, ponto.pos_y, c = "y")
        elif ponto.rotulo == "ruido":
            plt.scatter(ponto.pos_x, ponto.pos_y, c = 'k', marker='x')
    plt.show()

#Funcao auxziliar para gerar cores diferentes para k grupos
def gerar_cores(num_clusters):
    cores = []
    passo = 255 // max(1, num_clusters)  # Evita divisão por zero
    for i in range(num_clusters):
        r = (i * passo) % 256
        g = (2 * i * passo) % 256
        b = (3 * i * passo) % 256
        cores.append((r / 255, g / 255, b / 255))  # Normaliza para Matplotlib (0-1)
    return cores

#Plota o gráfico final diferenciando os grupos
def plotarGraficoFinal(pontos, clusters):
    print(len(clusters))
    num_clusters = len(clusters)
    cores = gerar_cores(num_clusters)
    for indice in range(len(clusters)):
        for ponto in clusters[indice]:
            if ponto.rotulo == "centro" or ponto.rotulo == "borda":
                plt.scatter(ponto.pos_x, ponto.pos_y, color = cores[indice])
    for ponto in pontos:
        if ponto.rotulo == "ruido":
            plt.scatter(ponto.pos_x, ponto.pos_y, c = 'k' , marker = 'x')
    plt.show()


# Definicao das variaveis epslon (Raio), minpts (Pontos minimos para ser centro) e o caminho para o arquivo
def main():
    arquivo_src = "./datasets/aggregation.arff"
    eps = 1.5  # Raio da vizinhança
    minpts = 5  # Minimo de pontos necessarios para ser um ponto de centro
    pontos = lerArquivo(arquivo_src)
    plotarGraficoBase(pontos)
    clusters = dbscan(pontos, eps, minpts)
    plotarGraficoMeio(pontos)
    plotarGraficoFinal(pontos, clusters)

if __name__ == "__main__":
    main()