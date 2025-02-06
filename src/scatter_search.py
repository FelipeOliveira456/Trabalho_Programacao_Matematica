import random
from heapq import heappush, heappop
import math
import copy
from itertools import combinations
from ler_arquivo import ler_arquivo
import time
import threading
import os
import argparse
import sys

class ScatterSearch():
    def __init__(self, delta, T, m, recursos, lista_adjacencia, vertices):
        self.__delta = delta
        self.__T = T
        self.__m = m 
        self.__recursos = recursos
        self.__lista_adjacencia = lista_adjacencia
        self.__vertices = vertices
        self.__P = []
        self.__ref_set = []
        self.__tipo_recurso = list(recursos.keys()) #passa a quantidade de recursos para uma lista, para facilitar a manipulacao

    def solve(self, it_improv=1000, ref_size=6, ref_prop=0.5, it_scatter=5): 

        #it_improv: numero de iteracoes na funcao de melhoria de solucoes
        #P_size: tamanho do conjunto P
        #ref_size: tamanho do ref_set
        #ref_prop: proporção de solucoes de qualidade vs diversidade.
        #it_scatter: o número de iteracoes do algoritmo geral
        inicio = time.time()  

        P_size = int(ref_size**2 - ref_size/2)

        solucoes = self.solucoes_aleatorias(P_size) #modulo que gera solucoes aleatorias

        self.P = self.processar_solucoes(solucoes, it_improv) #modulo que melhora as solucoes do P

        self.ref_set = self.ref_set_update_method(ref_size, ref_prop) #gera o ref_set atraves do P 

        solucoes_obj = []
        for solucao in self.ref_set:
            solucoes_obj.append(self.funcao_objetivo(solucao))
        
        solucao_inicial = max(solucoes_obj)
        
        for i in range(it_scatter):
            print(i)
            if(i == (it_scatter - 1)):
                break

            pares = self.gera_subconjuntos() # gera (n^2 - n)/2 pares, onde o n é a quantidade de elementos do refset

            solucoes = self.recombinacao(pares) # combina os pares para gerar novas solucoes que são incluidas no P

            self.P = self.processar_solucoes(solucoes, it_improv) 

            self.ref_set = self.ref_set_update_method(ref_size, ref_prop)

        solucoes_obj = []
        for solucao in self.ref_set:
            solucoes_obj.append(self.funcao_objetivo(solucao))
        
        solucao_final = max(solucoes_obj)

        fim = time.time()

        tempo_gasto = fim - inicio

        return solucao_inicial, solucao_final, tempo_gasto

    def solucoes_aleatorias(self, P_size):
        n_vertices = len(self.vertices)
        solucoes = [{vertice : [0] * self.m for vertice in self.vertices} for  _ in range(P_size)]
        recursos_disponiveis = [valor for _, valor in self.recursos.items()]
        samples = set() #para evitar repeticao de solucoes

        for i in range(P_size):
            r = recursos_disponiveis.copy()
            n_s = random.sample(range(1, n_vertices-1), sum(recursos_disponiveis))
            
            while True:
                if(tuple(n_s) not in samples):
                    samples.add(tuple(n_s))
                    break
                else:
                    n = random.sample(range(1, n_vertices-1), sum(recursos_disponiveis))    #sorteia os vértices que receberao recursos     
            j = 0

            for n in n_s:
                v = self.vertices[n]

                if(r[j] == 0):
                    j += 1

                solucoes[i][v][j] = 1
                r[j] -= 1

        return solucoes

    def processar_solucoes(self, solucoes, it_improv):
        num_nucleos = os.cpu_count() #verifica o numero de nucleos da CPU para o processamento em threads

        s = []
        threads = []

        def processar_solucao(solucao, it_improv, resultado):
            solucao_melhorada = self.melhoramento(solucao, it_improv)
            resultado.append(solucao_melhorada)

        for solucao in solucoes:
            thread = threading.Thread(target=processar_solucao, args=(solucao, it_improv, s))
            threads.append(thread)
            
            if len(threads) >= num_nucleos: #se as threads ja foram preenchidas, entao executa
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                threads = []

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return s

    def dijkstra_com_interferencia(self, interferencias, origem):

        tempo_chegada = {v: math.inf for v in self.lista_adjacencia}
        tempo_chegada[origem] = 0

        pq = [(0, origem)]
        
        while pq:
            T_v, v = heappop(pq)
            
            if T_v > tempo_chegada[v]:
                continue
            
            for w, t_trans in self.lista_adjacencia[v]:
                atraso = 0

                if v in interferencias:
                    T_interf, delta = interferencias[v]
                    if T_v >= T_interf: #se o vértice possui uma interferencia e o tempo do vértice é maior que o tempo de ativacao, adiciona o atraso
                        atraso = delta
                
                T_w = T_v + t_trans + atraso

                if T_w < tempo_chegada[w]:
                    tempo_chegada[w] = T_w
                    heappush(pq, (T_w, w))
        
        return tempo_chegada

    def resultado(self, tempos):
        c = 0
        for _, tempo in tempos.items():
            if(tempo < self.T): #calcula o número de vertices atingidos pela fake news antes do tempo T
                c += 1
        return c

    def funcao_objetivo(self, solucao):
        interferencias = {}

        for v, c in solucao.items():
            posicao = c.index(1) if 1 in c else None

            if posicao is not None:
                r = self.tipo_recurso[posicao]
                interferencias[v] = (r, self.delta)
        
        s = []
        for vertice in self.vertices: #considera todos os vértices como possíveis iniciais
            tempos = self.dijkstra_com_interferencia(interferencias, vertice) 
            s.append(self.resultado(tempos))
        
        return max(s) #retorna a solucao maxima, i.e, a pior solucao
    
    def melhoramento(self, solucao, n):
        func_obj_atual = self.funcao_objetivo(solucao)
        
        for _ in range(n):
            v1, v2 = random.sample(list(solucao.keys()), 2) #escolhe dois vértices aleatorios

            while solucao[v1] == solucao[v2]: #itera ate possuir vertices distintos em relacao aos recursos aplicados
                v1, v2 = random.sample(list(solucao.keys()), 2)
        
            solucao[v1], solucao[v2] = solucao[v2], solucao[v1] #faz a inversao do vetor de recursos

            novo_func_obj = self.funcao_objetivo(solucao)
            if novo_func_obj < func_obj_atual:
                return solucao #first improvement
    
            else:
                solucao[v1], solucao[v2] = solucao[v2], solucao[v1] #se nao melhorou, destroca e tenta novamente ate o numero de iteracoes terminar

        return solucao
    
    def ref_set_update_method(self, ref_size, prop):
        
        n_qualidade= round(ref_size * prop) #solucoes por qualidade
        n_diversidade = int(ref_size - n_qualidade) #solucoes por diversidade
        
        self.P.sort(key=lambda x: self.funcao_objetivo(x)) 

        ref_set = self.P[:n_qualidade] #seleciona por qualidade, baseando-se na que tem menor funcao objetivo
        self.P = self.P[n_qualidade:]
        
        ref_set = self.solucoes_diversas(ref_set, n_diversidade)

        return ref_set

    def solucoes_diversas(self, ref_set, n):
        
        candidatos = []

        for p in self.P:
            dist = []
            for s in ref_set:
                dist.append(self.calcula_distancia(p, s))
            d = min(dist) #seleciona a distancia minima, isto é, a distancia do vértice mais proximo
            candidatos.append((p, d))

        candidatos_ordenados = sorted(candidatos, key=lambda x: x[1], reverse=True) 
        
        solucoes_div = [tupla[0] for tupla in candidatos_ordenados[:int(n)]] # seleciona aqueles cuja distancia mínima é maxima
        
        ref_set += solucoes_div

        return ref_set

    def calcula_distancia(self, x, y):
        
        #calculo da distancia consiste em concatenar os vetores de bits e, a partir disso, calcular o módulo do vetor diferença. 

        x_bits = sum(x.values(), []) 
        y_bits = sum(y.values(), [])
        
        somatorio = 0
        
        for a, b in zip(x_bits, y_bits):
            somatorio += (a - b)**2
        
        somatorio = math.sqrt(somatorio)
        return somatorio
    
    def gera_subconjuntos(self):
    
        pares = list(combinations(self.ref_set, 2)) #gera todos os pares

        return pares            
    
    def recombinacao(self, pares):
        solucoes = []

        for par in pares:
            sol_inicial = par[0]
            sol_target = par[1]

            sol_inicial_obj = self.funcao_objetivo(par[0])
            sol_target_obj = self.funcao_objetivo(par[1])

            if(sol_inicial_obj < sol_target_obj): #procura caminhar da pior solucao (inicial) para a melhor (target)

                sol_inicial, sol_target = sol_target, sol_inicial
            dif = self.diferencas(sol_inicial, sol_target)

            solucoes.append(self.path_relinking(sol_inicial, sol_target, dif))

        return solucoes

    def path_relinking(self, sol_inicial, sol_target, dif):
        
        sol_caminho = []

        while dif: 

            #caminha até não haver diferença entre a solucao da iteracao e a solucao target.

            v_1, _, r_2 = dif.pop(0)
            swap_realizado = False
        
            for v_2, s_1, _ in dif:
                if s_1 == r_2:
                    sol_inicial[v_1], sol_inicial[v_2] = sol_inicial[v_2], sol_inicial[v_1] 
                    
                    #caminhar consiste em realizar trocas na solucao inicial

                    swap_realizado = True
                    break  
        
            if swap_realizado:
                dif = self.diferencas(sol_inicial, sol_target) #apos a troca, recalcula a diferença
                sol_caminho.append(copy.deepcopy(sol_inicial))

        if sol_caminho:
            sol_caminho.sort(key=lambda x: self.funcao_objetivo(x)) #retorna a melhor solucao encontrada no caminhamento
            return sol_caminho[0]
        
        return sol_target
        

    def diferencas(self, sol_inicial, sol_target):

        #calcula a diferença entre duas solucoes

        dif = []

        for v in sol_inicial:
            if(sol_inicial[v] != sol_target[v]):
                dif.append((v, sol_inicial[v], sol_target[v]))

        return dif

    
    #abaixo temos getters e setters

    @property
    def delta(self):
        return self.__delta
    
    @property
    def T(self):
        return self.__T
    
    @property
    def m(self):
        return self.__m
    
    @property
    def recursos(self):
        return self.__recursos
    
    @property
    def lista_adjacencia(self):
        return self.__lista_adjacencia
    
    @property
    def vertices(self):
        return self.__vertices
    
    @property
    def P(self):
        return self.__P
    
    @P.setter
    def P(self, value):
        self.__P = value
    
    @property
    def ref_set(self):
        return self.__ref_set
    
    @ref_set.setter
    def ref_set(self, value):
        self.__ref_set = value

    @property
    def tipo_recurso(self):
        return self.__tipo_recurso


parser = argparse.ArgumentParser(description="Scatter Search arguments")
parser.add_argument("-i", "--input", type=str)
parser.add_argument("-o", "--output", type=str)
parser.add_argument("--it_improv", type=int)
parser.add_argument("--ref_size", type=int)
parser.add_argument("--ref_prop", type=float)
parser.add_argument("--it_scatter", type=int)
args = parser.parse_args()

if args.input is None:
    print("--input: caminho do arquivo de entrada faltando")
    sys.exit(1)
if args.output is None:
    print("--output: caminho do arquivo de saída faltando")
    sys.exit(1)
if args.it_improv is None or args.it_improv < 1:
    print("--it_improv deve receber um valor positivo")
    sys.exit(1)
if args.ref_size is None or args.ref_size < 1:
    print("--it_improv deve receber um valor positivo")
    sys.exit(1)
if args.ref_prop is None or not (0 <= args.ref_prop <= 1):
    print("--ref_prop deve receber um valor entre 0 e 1")
    sys.exit(1)
if args.it_scatter is None or args.it_scatter < 1:
    print("--it_scatter deve receber um valor positivo")
    sys.exit(1)
   
with open(args.output, "w") as f:
    delta, T, m, recursos, lista_adjacencia, vertices = ler_arquivo(args.input)
    modelo = ScatterSearch(delta, T, m, recursos, lista_adjacencia, vertices)
    solucao_inicial, solucao_final, tempo_gasto = modelo.solve(args.it_improv, args.ref_size, args.ref_prop, args.it_scatter)
    f.write(f"{args.input}: Solução Inicial: {solucao_inicial}, Solução Final: {solucao_final}, Tempo Gasto: {tempo_gasto} segundos\n")
