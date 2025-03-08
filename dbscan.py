import math
import matplotlib.pyplot as plt

#Classe do ponto
class Ponto:
    def __init__(self, pos_x, pos_y,):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotulo = "ruido"
        self.visitado = False

    def setRotulo(self, rotulo):
        self.rotulo = rotulo

    def setVisitado(self, visitado):
        self.visitado = visitado

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

#Faz a expansao do cluster expandido os vizinhos que forem centro
def expandir_cluster(pontos, vizinhos, eps, minpts):
    cluster = []
    indice = 0
    while indice < len(vizinhos):
        if not vizinhos[indice].visitado:
            vizinhos[indice].visitado = True
            novos_vizinhos = procurar_vizinhos(vizinhos[indice], pontos, eps)
            if len(novos_vizinhos) >= minpts:
                vizinhos[indice].rotulo = "centro"
                vizinhos.extend(novos_vizinhos)
            else:
                vizinhos[indice].rotulo = "borda"
            cluster.append(vizinhos[indice])
        indice += 1
    return cluster

#Laco inicial, percorre tentando encontrar os centros nao visitados
def dbscan(pontos, eps, minpts):
    clusters = []
    for ponto in pontos:
        if not ponto.visitado:
            vizinhos = procurar_vizinhos(ponto, pontos, eps)
            cluster = expandir_cluster(pontos, vizinhos, eps, minpts)
            if len(vizinhos) >= minpts:
                ponto.visitado = True
                ponto.rotulo = "centro"
                cluster.append(ponto)
                clusters.append(cluster)
    return clusters

#Definicao das variaveis epslon (Raio), minpts (Pontos minimos para ser centro) e o caminho para o arquivo
def main():
    arquivo_src = "./datasets/compound.arff"
    eps = 1.5  # Raio da vizinhança
    minpts = 5  # Minimo de pontos necessarios para ser um ponto de centro
    pontos = lerArquivo(arquivo_src)
    plotarGraficoBase(pontos)
    clusters = dbscan(pontos, eps, minpts)
    plotarGraficoMeio(pontos)
    plotarGraficoFinal(pontos, clusters)

if __name__ == "__main__":
    main()