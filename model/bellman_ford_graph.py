from pprint import pprint

def bellman_ford(graph, qtd_vertices, origem):
    # Inicialização dos dados
    dist = [float('inf')] * qtd_vertices
    dist[origem] = 0

    flux = [float('inf')] * qtd_vertices
    flux[origem] = 0
    
    caminho = {}
    
    # Soma dos dados
    for _ in range(qtd_vertices - 1):
        for u, v, custo, peso, dem, custo_maximo  in graph:
            if dist[u] == float('inf') :
                continue
            
            if dist[u] + custo < dist[v]: # and flux[u] + dem < flux[v] :
                dist[v] = dist[u] + custo
                flux[v] = flux[u] + peso
                caminho[(u,v)] = custo
                
    # Checkagem de ciclo
    for u, v, custo, peso, dem, custo_maximo in graph:
        if dist[u] != float('inf') and dist[u] + custo < dist[v]: # and flux[u] != float('inf') and flux[u] + dem < flux[v]:
            print("Ciclo negativo")
            return {"distancia": dist, "fluxo": flux, "caminho": caminho}

    return {"distancia": dist, "fluxo": flux, "caminho": caminho}

