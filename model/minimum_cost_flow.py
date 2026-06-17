import pyomo.environ as pyo
#import matplotlib.pyplot as plt
from networkx import (
    DiGraph,
    layout,
    draw,
    draw_networkx_labels as draw_labels,
    draw_networkx_edge_labels as draw_edge_labels,
    draw_networkx_edges as draw_edges,
)
from IPython.display import HTML, Markdown


def draw_network(network, ax=None, edge_flows=None):
    g = DiGraph(network["edges"].keys())
    pos = layout.kamada_kawai_layout(g, weight=None)
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
    for i, data in network["nodes"].items():
        label = ",".join(f"{k}={v}" for k, v in data.items())
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
        draw_edge_labels(
            g,
            pos=pos,
            ax=ax,
            font_size=9,
            edge_labels={
                i: ",".join(f"{k}={v}" for k, v in data.items())
                for i, data in network["edges"].items()
            },
        )
    else:
        draw_edges(g, pos=pos),
        draw_edge_labels(
            g, pos=pos, ax=ax, font_size=11, font_weight="bold", edge_labels=edge_flows
        )


def mincostflow(network):
    model = pyo.ConcreteModel("Minimum cost flow")

    model.x = pyo.Var(network["edges"], domain=pyo.NonNegativeReals)

    @model.Objective(sense=pyo.minimize)
    def objective(m):
        return sum(data["c"] * m.x[e] for e, data in network["edges"].items())

    @model.Expression(network["nodes"])
    def incoming_flow(m, j):
        return sum(m.x[i, j] for i in network["nodes"] if (i, j) in network["edges"])

    @model.Expression(network["nodes"])
    def outgoing_flow(m, j):
        return sum(m.x[j, i] for i in network["nodes"] if (j, i) in network["edges"])

    @model.Constraint(network["nodes"])
    def flow_conservation(m, j):
        return m.outgoing_flow[j] - m.incoming_flow[j] == network["nodes"][j]["b"]

    @model.Constraint(network["edges"])
    def flow_upper_bound(m, *e):
        return m.x[e] <= network["edges"][e]["u"]

    return model