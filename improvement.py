import random
from funcao_objetivo import funcao_objetivo

def melhoramento(solucao, lista_adjacencia, vertices, tipo_recurso, delta, T, n=500):
    func_obj_atual = funcao_objetivo(lista_adjacencia, vertices, solucao, tipo_recurso, delta, T)
    
    melhor_solucao = solucao
    melhor_objetivo = func_obj_atual

    for _ in range(n):
        v1, v2, v3  = random.sample(list(solucao.keys()), 3)

        if solucao[v1] != solucao[v2] and solucao[v1] != solucao[v3]:
            solucao[v1], solucao[v2] = solucao[v2], solucao[v1]
            solucao[v1], solucao[v3] = solucao[v3], solucao[v1]

            novo_func_obj = funcao_objetivo(lista_adjacencia, vertices, solucao, tipo_recurso, delta, T)
            if novo_func_obj < func_obj_atual:
                func_obj_atual = novo_func_obj 
                melhor_objetivo = novo_func_obj 
                melhor_solucao = solucao 
 
            else:
                solucao[v1], solucao[v3] = solucao[v3], solucao[v1]
                solucao[v3], solucao[v2] = solucao[v2], solucao[v3]
    
    print(melhor_objetivo)
    return melhor_solucao
                
