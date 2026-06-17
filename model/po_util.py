import math

import pyomo.environ as pyo
import matplotlib.pyplot as plt
import networkx as nx
import csv
from model.bellman_ford_graph import bellman_ford
# from model.ford_fulkerson_graph import FordFulkersonGraph

from pathlib import Path
from pprint import pprint

def load_list_csv(file_path):    
    file = open(file_path)
    reader = csv.reader(file)
    return list(reader)

def load_filiais_csv(file_path):
    data = load_list_csv(file_path)
    c = data[0][0].split(";")
    data.pop(0)
    obj = {}
    for i in range(len(data)):
        d = data[i][0].split(";")
        row = {"b": int(d[2]), "nome": d[1], "demanda_kg": int(d[2]), "custo_maximo": int(d[3])}
        pprint(row)
        obj[int(d[0])] = row

    return obj

def load_veiculos_csv(file_path):
    data = load_list_csv(file_path)
    c = data[0][0].split(";")
    data.pop(0)
    obj = {}
    for i in range(len(data)):
        d = data[i][0].split(";")
        row = {c[1].strip(): d[1].strip(), "custo_km": int(d[2]), "capacidade_maxima_kg": int(d[3])}
        obj[int(d[0])] = row

    return obj


def load_trajetos_csv(file_path):
    data = load_list_csv(file_path)
    c = data[0][0].split(";")
    data.pop(0)
    obj = {}
    for i in range(len(data)):
        d = data[i][0].split(";")
        # row = {"c": int(d[2]), "u": 0.0}
        row = {"c": int(d[2]), "u": 506}
        obj[(int(d[0]), int(d[1]))] = row
    
    return obj

def load_matriz_custos_csv(file_path, qtd_veiculos, qtd_filiais):
    if not Path(file_path).exists():
        print(f"Arquivo {file_path} não existe")
        return []

    file = open(file_path, mode="r")
    reader = csv.DictReader(file, delimiter=';')
    data = list(reader)
    if(len(data) == 0):
        print(f"Arquivo {file_path} vaizo")
        return []
    
    #data.pop(0)
    m = [[[0 for _ in range(qtd_filiais)] for _ in range(qtd_filiais)] for _ in range(qtd_veiculos)] 
    f = [[[0 for _ in range(qtd_filiais)] for _ in range(qtd_filiais)] for _ in range(qtd_veiculos)] 
    p = [[[0 for _ in range(qtd_filiais)] for _ in range(qtd_filiais)] for _ in range(qtd_veiculos)] 
    # pprint(obj)
    # exit(0)
    for r in data:        
        # pprint(r)
        m[int(r["veiculo"])][int(r["origem"])][int(r["destino"])] = int(r["custo"]) 
        f[int(r["veiculo"])][int(r["origem"])][int(r["destino"])] = int(r["fluxo"]) 
        p[int(r["veiculo"])][int(r["origem"])][int(r["destino"])] = eval(r["caminho"])

    return {"matriz_custos": m, "fluxo": f,"caminhos": p}

def criar_matriz_custos(filiais, trajetos, veiculos): 
    size = len(filiais.keys()) 
    m = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(len(veiculos.keys()))]
    f = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(len(veiculos.keys()))]
    p = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(len(veiculos.keys()))]

    # pprint(m)
    # pprint(f)
    # pprint(p)

    for i, veiculo in veiculos.items():
        # print(f"Veiculo: {veiculo["nome"]}:{veiculo["custo_km"]}")
        edges = []
        for nos, trajeto in trajetos.items():
            demanda_minima = filiais[nos[0]]["demanda_kg"]
            print(filiais[nos[0]])
            # custo_trajeto_veiculo = ((-1) * 2 * trajeto["c"] * veiculo["custo_km"]  / demanda_minima) if demanda_minima != 0 else 0
            custo_trajeto_veiculo = trajeto["c"]
            peso_maximo = veiculo["capacidade_maxima_kg"]-demanda_minima
            #demanda_minima = filiais[nos[1]]["demanda_kg"]
            custo_maximo = filiais[nos[1]]["custo_maximo"]
            edges.append([nos[0],nos[1], custo_trajeto_veiculo, peso_maximo, demanda_minima, custo_maximo])

        # pprint(edges)
        # exit(0)

        # matriz_custos = m[i]
        for origem in range(len(filiais)):
            # filial = filiais[origem]
            #print(f"Filial {f}:{filial}")
            # source = f
            result = bellman_ford(edges, len(filiais), origem)

            # pprint(result)

            m[i][origem] = result["distancia"]
            f[i][origem] = result["fluxo"]
            p[i][origem] = result["caminho"]
            
            
            # print(m[i])
            # pprint(p[i])

        #pprint(m[i])
        #    if i == 5: break
        
    # matriz_custos = m
    # pprint(matriz_custos)
    # pprint(m)
    # exit(0)
    
    # pprint(p)
    # exit(0)
    
    csv_base_path = Path('data/')
    file_path_filiais = f'{csv_base_path}/matriz_custos.csv'

    output_file = open(file_path_filiais, 'w', newline='')
    output_dict_writer = csv.DictWriter(output_file, ['origem', 'destino', 'veiculo', 'custo', 'fluxo', 'caminho'], delimiter=';')
    output_dict_writer.writeheader()
    # lista = []
    for i in range(len(m)):
        for j in range(len(m[i])):    
            for k in range(len(m[i][j])):
                c = {}
                if(m[i][j][k] != float('inf') and m[i][j][k] != 0):
                    for (u, v) in p[i][j].keys():
                        c[(u,v)] = p[i][j][(u,v)]
                        if v == k:
                            #p[i][j] = c
                            break;
                        
                output_dict_writer.writerow({'origem': j, 'destino': k, 'veiculo': i, 'custo': m[i][j][k], 'fluxo': f[i][j][k], 'caminho': c})

    return {"matriz_custos": m, "fluxo": f, "caminhos": p}

def criar_graficos_custos(veiculos, trajetos, matriz_custos):
    for i, veiculo in veiculos.items():
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        g = nx.DiGraph(ax=ax)
        for nos, trajeto in trajetos.items():
            g.add_edge(nos[0], nos[1], weight=matriz_custos[i][nos[0]][nos[1]])

        pos = nx.layout.kamada_kawai_layout(g, weight=None)
        nx.draw_networkx_nodes(g, pos, ax=ax, node_color="purple")
        nx.draw_networkx_edges(g, pos, ax=ax,edge_color="black")
        nx.draw_networkx_labels(g, pos, ax=ax, font_color="white", font_size=11)
        nx.draw_networkx_edge_labels(
            g, pos, ax=ax, font_size=11, edge_labels={(u, v): round(d["weight"],2) for u, v, d in g.edges(data=True)}
        )
        plt.title(f"Custo de transporte (por Km) {veiculo["nome"]}-{i}")
        plt.savefig(f"img/graph/graph-{veiculo["nome"]}-{i}.png")

def criar_graficos_caminhos(veiculos, trajetos, matriz_custos, caminhos):
    for i, veiculo in veiculos.items():
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        g = nx.DiGraph(ax=ax)
        for j in range(len(caminhos[i])):
            
            for k in range(len(caminhos[i][j])):

                
                if len(caminhos[i][j][k].items()) == 0:
                    continue
            # for nos, trajeto in trajetos.items():
                #labels = []
                # if matriz_custos[i][j][k] != float('inf') and matriz_custos[i][j][k] != 0:
                # pprint(caminhos[i][j])
                # exit(0)
                g.add_edge(j, k, weight=caminhos[i][j][k][(j, k)])

        pos = nx.layout.kamada_kawai_layout(g, weight=None)
        nx.draw_networkx_nodes(g, pos, ax=ax, node_color="red")
        nx.draw_networkx_edges(g, pos, ax=ax,edge_color="black")
        nx.draw_networkx_labels(g, pos, ax=ax, font_color="white", font_size=11)
        nx.draw_networkx_edge_labels(
            g, pos, ax=ax, font_size=11, edge_labels={(u, v): round(d["weight"],2) for u, v, d in g.edges(data=True)}
        )
        plt.title(f"Caminho {veiculo["nome"]}-{i}")
        plt.savefig(f"img/graph/cam-{veiculo["nome"]}-{i}.png")
        break;