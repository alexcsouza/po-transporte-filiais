import pyomo.environ as pyo
import matplotlib.pyplot as plt
# import networkx as nx
import time
import sys

from model.po_util import *
from model.minimum_cost_flow import *
# from model.bellman_ford_graph import bellman_ford
# from model.ford_fulkerson_graph import FordFulkersonGraph
from pathlib import Path
from pprint import pprint
from IPython.display import HTML, Markdown

# Pasta de dados
csv_base_path = Path('data/')

# Pasta de imagens
img_base_path = Path('img/')

start_total = time.process_time()
print(f"\n--- INÍCIO ---")


# Carregando filiais
start = time.process_time()
print(f"\nCarregando filiais")
file_path_filiais = f'{csv_base_path}/filiais.csv'
filiais = load_filiais_csv(file_path_filiais)
#pprint(filiais)
end = time.process_time()
print(f"Ok: {end - start} segundos")

# Carregando trajetos
start = time.process_time()
print(f"\nCarregando trajetos")
file_path_trajetos = f'{csv_base_path}/trajetos.csv'
trajetos = load_trajetos_csv(file_path_trajetos)
pprint(trajetos)
end = time.process_time()
print(f"Ok: {end - start} segundos")

start = time.process_time()
print(f"\nCarregando veículos")
file_path_veiculos = f'{csv_base_path}/veiculos.csv'
veiculos = load_veiculos_csv(file_path_veiculos)
pprint(veiculos)
end = time.process_time()
print(f"Ok: {end - start} segundos")

start = time.process_time()
print(f"\nCarregando matriz de custos (gerada préviamente)")
file_path_matriz_custos = f'{csv_base_path}/matriz_custos.csv'
m = load_matriz_custos_csv(file_path_matriz_custos, len(veiculos), len(filiais))
end = time.process_time()
print(f"Ok: {end - start} segundos")

if(len(m) == 0):
#if True:
   print(f"\nMatriz de custos não encontrada!!")
   
   print(f"\nCriando matriz de custos")
   start = time.process_time()
   m = criar_matriz_custos(filiais, trajetos, veiculos)
   matriz_custos = m["matriz_custos"]
   caminhos = m["caminhos"]
   end = time.process_time()
   print(f"Ok: {end - start} segundos")
   
   start = time.process_time()
   print(f"\nGerando gráficos de custos por veículo")
   criar_graficos_custos(veiculos, trajetos, matriz_custos)
   end = time.process_time()
   print(f"Ok: {end - start} segundos")

matriz_custos = m["matriz_custos"]
fluxo = m["fluxo"]
caminhos = m["caminhos"]

# for i in range(len(matriz_custos)):
#     for j in range(len(matriz_custos[i])):    
#         for k in range(len(matriz_custos[i][j])):
#             print(matriz_custos[i][j][k])
#             # network["edges"][(j,k)]["u"] = matriz_custos[i][j][k]



# Solução do problema de minimização do custo
start = time.process_time()
print(f"\nSolução do problema de minimização do custo")


def solve_min_cost(solver, filiais, trajetos, veiculos, matriz_custos): 

    SOLVER = pyo.SolverFactory(solver)
    assert SOLVER.available(), f"Solver {solver} não instalado."

    edges = {}
    nodes = {}

#for v in range(len(veiculos.keys())): 
    v=5
    for (o, d) in trajetos:
        #pprint(fluxo[v][o][d])
        #exit(0)
        
        trajetos[(o, d)]["u"] = (-1) * filiais[d]["demanda_kg"]
        edges[(o, d)] = {"u": (-1) * filiais[d]["demanda_kg"], "c": matriz_custos[v][o][d]}
        nodes[o] = {"b": fluxo[v][o][d]}
        
#           
# 
#           network["edges"][(o, d)]["u"] = veiculos[v]["capacidade_maxima_kg"]
#           network["edges"][(o, d)]["c"] = matriz_custos[v][o][d]
#
#           network["nodes"][o]["b"] = fluxo[v][o][d]

    network = {"nodes": nodes, "edges": edges}
    #network = {"nodes": filiais, "edges": trajetos}
    
    pprint(network)
    #exit(0)

    #for i in range(len(matriz_custos)):
    #    for j in range(len(matriz_custos[i])):    
    #        for k in range(len(matriz_custos[i][j])):
    #            print(matriz_custos[i][j][k])
    #            # network["edges"][(j,k)]["u"] = matriz_custos[i][j][k]


    # pprint(network)

    model = mincostflow(network)
    SOLVER.solve(model)
    
    model = mincostflow(network)
    SOLVER.solve(model)
    flows = {e: round(model.x[e].value) for e in network["edges"]}
    print(f"\nOptimal solution:")
    display(
        Markdown(
            ", ".join("$x_{%s} = %d$" % (e, model.x[e].value) for e in network["edges"])
        )
    )
    print(f"Objective value: {model.objective():.0f}")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    draw_network(network, ax=ax, edge_flows=flows)

    file_path_grafo_custo_minimo = f'{img_base_path}/minimum-cost-graph.png'
    plt.savefig(file_path_grafo_custo_minimo)
    end = time.process_time()

    print(f"\nTempo do solver ({solver}): {end - start} segundos")


# Selecionando o solver
# solver = 'gurobi_direct'
# solver = 'appsi_highs'
solver = 'glpk'
solve_min_cost(solver, filiais, trajetos, veiculos, matriz_custos)


end_total = time.process_time()
print(f"\nTempo total: {end_total - start_total} segundos")
print(f"\n--- FIM ----")


