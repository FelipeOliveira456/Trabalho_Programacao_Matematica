from collections import defaultdict

def ler_arquivo(filename):
    with open(filename, 'r') as file:
        _, delta, T = map(int, file.readline().split())

        m = int(file.readline().strip())

        recursos = {}
        for _ in range(m):
            t, k = map(int, file.readline().split())
            recursos[t] = k

        lista_adjacencia = defaultdict(list)

        for line in file:
            partes = line.split()
            x1, y1 = map(int, partes[0].split('-'))
            x2, y2 = map(int, partes[1].split('-'))
            t = int(partes[2])
            
            lista_adjacencia[(x1, y1)].append(((x2, y2), t))
        
        vertices = retorna_vertices(lista_adjacencia)

        return delta, T, m, recursos, lista_adjacencia, vertices

def retorna_vertices(lista_adjacencia):
    vertices = list(lista_adjacencia.keys()) 
    return vertices
