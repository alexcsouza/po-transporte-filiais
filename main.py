import pyomo.environ as pyo
import matplotlib.pyplot as plt
# import networkx as nx
import time

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

# Solução do problema de minimização do custo
start = time.process_time()
print(f"\nSolução do problema de minimização do custo")

# Selecionando o solver
solver = 'appsi_highs'
# solver = 'glpk'

SOLVER = pyo.SolverFactory(solver)
assert SOLVER.available(), f"Solver {solver} não instalado."

network = {"nodes": filiais, "edges": trajetos}

# network = {
#     "nodes": {
#         0: {"b":1},
#         1: {"b":1},
#         2: {"b":1},
#         3: {"b":1},
#         4: {"b":1},
#         5: {"b":1},
#         6: {"b":1},
#         7: {"b":1},
#         8: {"b":1},
#         9: {"b":1},
#         10: {"b":1},
#     },
#     "edges": {
#         (0, 1)  : {"u": 15, "c": 1  },
#         (1, 2)  : {"u": 14, "c": 1  },
#         (2, 9)  : {"u": 10, "c": 1  },
#         (2, 3)  : {"u": 15, "c": 1  },
#         (3, 4)  : {"u": 15, "c": 1  },
#         (3, 5)  : {"u": 10, "c": 2  },
#         (3, 4)  : {"u": 10, "c": 3  },
#         (4, 7)  : {"u": 4,  "c": 1  },
#         (4, 8)  : {"u": 5,  "c": 4  },
#         (5, 8)  : {"u": 5,  "c": 3  },
#         (5, 9)  : {"u": 6,  "c": 2  },
#         (5, 10) : {"u": 5,  "c": 1  },
#         (8, 6)  : {"u": 8,  "c": 3  },
#         (6, 10) : {"u": 1,  "c": 3  },
#         (7, 8)  : {"u": 4,  "c": 2  },
#         (7, 10) : {"u": 2,  "c": 2  },
#         (8, 10) : {"u": 5,  "c": 3  },
#         (9, 10) : {"u": 3,  "c": 1  },
#     },
# }
v = 0
for (o, d) in network["edges"]:
    network["edges"][(o, d)]["u"] = veiculos[v]["capacidade_maxima_kg"]
    network["edges"][(o, d)]["c"] = matriz_custos[v][o][d]
    network["nodes"][o]["b"] = fluxo[v][o][d]

#for i in range(len(matriz_custos)):
#    for j in range(len(matriz_custos[i])):    
#        for k in range(len(matriz_custos[i][j])):
#            print(matriz_custos[i][j][k])
#            # network["edges"][(j,k)]["u"] = matriz_custos[i][j][k]


pprint(network)

model = mincostflow(network)
SOLVER.solve(model)
flows = {e: round(model.x[e].value) for e in network["edges"]}
print(f"\nOptimal solution:")

output = []
for e in network["edges"]:
    output.append(f"x_{e} = {model.x[e].value}")

print("\n".join(output))

print(f"Objective value: {model.objective():.0f}")
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
draw_network(network, ax=ax, edge_flows=flows)

file_path_grafo_custo_minimo = f'{img_base_path}/minimum-cost-graph.png'
plt.savefig(file_path_grafo_custo_minimo)

end = time.process_time()
print(f"\nTempo total: {end - start} segundos")
print(f"\n--- FIM ----")


