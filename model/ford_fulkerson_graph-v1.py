from networkx import (
    DiGraph,
    petersen_graph,
    layout,
    draw,
    draw_networkx_labels as draw_labels,
    draw_networkx_edge_labels as draw_edge_labels,
    draw_networkx_edges as draw_edges,
)

import matplotlib.pyplot as plt
from pprint import pprint

class FordFulkersonGraphv1:
    def __init__(self, nos, vertices):
        self.nos = nos
        self.vertices = vertices
        self.size = len(nos)
        self.vertex_data = [''] * self.size
        #self.vertex_data = vertices
        # self.vertex_data = [{"c":0}] * self.size
        self.adj_matrix = [[0] * self.size for _ in range(self.size)]
        pprint(self.adj_matrix)

        for n, d in vertices.items():
            self.adj_matrix[n[0]][n[1]] = d["c"]
            self.adj_matrix[n[1]][n[0]] = d["c"]

        for f in range(len(nos)):
            filial = nos[f]
            self.vertex_data[f] = filial
            #print(f"Filial {f}:{filial}")
            # g.add_vertex_data(f, filial)

        print("matriz_adj")
        pprint(self.adj_matrix)
        print("vertices")
        pprint(self.vertex_data)

    def add_edge(self, u, v, c):
        self.adj_matrix[u][v] = c

    def add_vertex_data(self, vertex, data):
        if 0 <= vertex < self.size:
            self.vertex_data[vertex] = data

    def dfs(self, s, t, visited=None, path=None):
        if visited is None:
            visited = [False] * self.size
        if path is None:
            path = []

        visited[s] = True
        path.append(s)

        if s == t:
            return path

        for ind, val in enumerate(self.adj_matrix[s]):
            if not visited[ind] and val > 0:
                result_path = self.dfs(ind, t, visited, path.copy())
                if result_path:
                    return result_path

        return None

    def fordFulkerson(self, no_origem, no_destino):
        max_flow = 0
        path_edges = {}
        path = self.dfs(no_origem, no_destino)
        print(f"path: {path}")
        while path:
            path_flow = float("Inf")
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                print(f"min(path_flow, self.adj_matrix[u][v]: ({path_flow}, {self.adj_matrix[u][v]})")
                # path_flow = min(path_flow, self.vertex_data[(u,v)]["c"] )
                path_flow = min(path_flow, self.adj_matrix[u][v])
                

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.adj_matrix[u][v] -= path_flow
                self.adj_matrix[v][u] += path_flow
                # self.vertex_data[(u,v)]["c"] -= path_flow
                # self.vertex_data[(v,u)]["c"] += path_flow
                path_edges[(u, v)] = self.vertex_data[(u,v)]

            print(f"{max_flow}+{path_flow}")

            max_flow += path_flow
            #path_data = {node: self.vertex_data[node] for node in path}
            path_data = {}
            path = self.dfs(no_origem, no_destino)

        return {"path_data": path_data, "path_flow": path_flow, "max_flow": max_flow, "path_edges": path_edges}

    def plot(self, filiais, trajetos, ax=None, edge_flows=None, image_path="./img/ford-fulkerson/ff.png"): 
        g = DiGraph(trajetos.keys())
        # g = petersen_graph()
        #flows = {e: round(model.x[e].value) for e in network["edges"]}
        pos = layout.kamada_kawai_layout(g, weight=None)
        # pprint(pos)
        draw(g, pos=pos, ax=ax, with_labels=True, font_color="white")
        if not (edge_flows is None):
            F = {k: v for k, v in edge_flows.items() if v > 0}
            draw_edges(
                g,
                pos=pos,
                edgelist=F.keys(),
                width=10,
                edge_color="lightblue",
                style="solid",
                alpha=None,
                arrowstyle="-",
            ),
        shifted_pos = {k: (x, y - 0.08) for k, (x, y) in pos.items()}
        pprint(filiais.items())

        for i, data in filiais.items():
            label = ",".join(f"{v}" for v in data)
            value = data.get("b", 0)

            if value < 0:
                color = "red"
            elif value == 0:
                color = "gray"
            else:
                color = "green"
            draw_labels(
                g,
                ax=ax,
                pos={i: shifted_pos[i]},
                labels={i: label},
                font_color=color,
                font_weight="bold",
            )


        if edge_flows is None:
            pprint(data)
            draw_edge_labels(
                g,
                pos=pos,
                ax=ax,
                font_size=9,
                edge_labels={
                    i: ",".join(f"{data}")
                    for i, data in trajetos.items()
                },
            )
        else:
            draw_edges(g, pos=pos),
            draw_edge_labels(
                g, pos=pos, ax=ax, font_size=11, font_weight="bold", edge_labels=edge_flows
            )
        plt.savefig(image_path)
