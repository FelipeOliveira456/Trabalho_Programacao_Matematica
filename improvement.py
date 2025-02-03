import random
from funcao_objetivo import funcao_objetivo

def melhoramento(solucao, lista_adjacencia, vertices, tipo_recurso, delta, T):
    func_obj_atual = funcao_objetivo(lista_adjacencia, vertices, solucao, tipo_recurso, delta, T)
    lista_trocas = []
    
    while True:
        v1, v2  = random.sample(list(solucao.keys()), 2)

        if (v1, v2) not in lista_trocas and solucao[v1] != solucao[v2]:
            lista_trocas.append((v1, v2))
            lista_trocas.append((v2, v1))
            solucao[v1], solucao[v2] = solucao[v2], solucao[v1]

            novo_func_obj = funcao_objetivo(lista_adjacencia, vertices, solucao, tipo_recurso, delta, T)
            if novo_func_obj < func_obj_atual:
                func_obj_atual = novo_func_obj  
                print(f"Melhoria encontrada: {novo_func_obj}")
                return solucao  
            else:
                solucao[v1], solucao[v2] = solucao[v2], solucao[v1]
