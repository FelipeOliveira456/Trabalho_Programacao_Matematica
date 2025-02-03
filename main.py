from ler_arquivo import ler_arquivo
from funcao_objetivo import funcao_objetivo
from conjunto_inicial import solucoes_aleatorias
from improvement import melhoramento

delta, T, m, recursos, lista_adjacencia, vertices = ler_arquivo("instances/fn5.dat")
solucoes = solucoes_aleatorias(m, recursos, vertices)
tipo_recurso = list(recursos.keys())
for solucao in solucoes:
    nova_solucao = melhoramento(solucao, lista_adjacencia, vertices, tipo_recurso, delta, T)
