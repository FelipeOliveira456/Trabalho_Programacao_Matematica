from heapq import heappush, heappop
import math

def dijkstra_com_interferencia(lista_adjacencia, interferencias, origem):

    tempo_chegada = {v: math.inf for v in lista_adjacencia}
    tempo_chegada[origem] = 0

    pq = [(0, origem)]
    
    while pq:
        T_v, v = heappop(pq)
        
        if T_v > tempo_chegada[v]:
            continue
        
        for w, t_trans in lista_adjacencia[v]:
            atraso = 0

            if v in interferencias:
                T_interf, delta = interferencias[v]
                if T_v <= T_interf:
                    atraso = delta
            
            T_w = T_v + t_trans + atraso

            if T_w < tempo_chegada[w]:
                tempo_chegada[w] = T_w
                heappush(pq, (T_w, w))
    
    return tempo_chegada

def resultado(tempos, T):
    c = 0
    for _, tempo in tempos.items():
        if(tempo < T):
            c += 1
    return c

def funcao_objetivo(lista_adjacencia, vertices, solucao, tipo_recurso, delta, T):
    interferencias = {}

    for v, c in solucao.items():
        posicao = c.index(1) if 1 in c else None

        if posicao is not None:
            r = tipo_recurso[posicao]
            interferencias[v] = (r, delta)
    
    s = []
    somatorio = 0
    for vertice in vertices:
        tempos = dijkstra_com_interferencia(lista_adjacencia, interferencias, vertice)
        s.append(resultado(tempos, T))
    
    return max(s)
