import random

def solucoes_aleatorias(m, recursos, vertices, s_size=10000):

    n_vertices = len(vertices)

    solucoes = [{vertice : [0] * m for vertice in vertices} for  _ in range(s_size)]

    recursos_disponiveis = [valor for _, valor in recursos.items()]

    samples = set()

    for i in range(s_size):

        r = recursos_disponiveis.copy()
            
        n_s = random.sample(range(1, n_vertices-1), sum(recursos_disponiveis))
            
        while True:
            if(tuple(n_s) not in samples):
                samples.add(tuple(n_s))
                break
            else:
                n = random.sample(range(1, n_vertices-1), sum(recursos_disponiveis))
        
        j = 0

        for n in n_s:
            v = vertices[n]

            if(r[j] == 0):
                j += 1

            solucoes[i][v][j] = 1
            r[j] -= 1

    return solucoes

