import requests
import networkx as nx
from typing import TypeAlias
import matplotlib.pyplot as plt
import staticmap

BusesGraph: TypeAlias = nx.Graph


def get_buses_graph() -> BusesGraph:
    """
    Downloads the data from AMB and returns a not-directed graph containing all lines of buses in Barcelona.
    """

    # Download info
    url = "https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json"
    response = requests.get(url)

    # In each position of the list there is a list with the info of each stop
    data = response.json()['ObtenirDadesAMBResult']['Linies']['Linia']

    # Create an empty graph
    G = nx.Graph()

    for linea in data:
        prev_stop = None
        for parada in linea['Parades']['Parada']:
            # we filter the busos in bcn, however if there is a line that goes to another city and has some stop in bcn we consider just the ones of bcn
            if parada['Municipi'] == 'Barcelona':

                idLinia = str(parada['IdLinia'])
                ordre = str(parada['Ordre'])
                nodeId = idLinia + '_' + ordre

                posicio = (parada['UTM_X'],  parada['UTM_Y'])

                G.add_node(nodeId, pos=posicio)
                G.nodes[nodeId]['Nom'] = parada['Nom']

                if prev_stop is not None and nodeId != prev_stop:
                    G.add_edge(prev_stop, nodeId)
                    G.edges[prev_stop, nodeId]["nom_linia"] = linea['Nom']

                # We update the previous stop
                prev_stop = nodeId

    return G


def show_buses(g: BusesGraph) -> None:
    """
    Displays the graph interactively using network.draw
    """
    pos = nx.get_node_attributes(g, 'pos')
    nx.draw(g, pos=pos, node_size=5)
    plt.show()


def paint_nodes(g: BusesGraph, m: staticmap.StaticMap) -> None:
    """
    Paints all the nodes from the Buses graph in red
    """
    for n in g.nodes():
        node = g.nodes[n]
        pos = node['pos']
        reversed_pos = (pos[1], pos[0])
        m.add_marker(staticmap.CircleMarker(reversed_pos, 'red', 40))


def paint_edges(g: BusesGraph, m: staticmap.StaticMap) -> None:
    """
    Paints all the edges from the Buses graph in blue
    """
    for edge in g.edges:
        pos_node_1 = g.nodes[edge[0]]['pos']
        pos_node_2 = g.nodes[edge[1]]['pos']

        reversed_pos_1 = (pos_node_1[1], pos_node_1[0])
        reversed_pos_2 = (pos_node_2[1], pos_node_2[0])

        coord = (reversed_pos_1, reversed_pos_2)
        line = staticmap.Line(coord, 'blue', 5)
        m.add_line(line)


def plot_buses(g: BusesGraph, nom_fitxer: str) -> None:
    """
    Saves the graph as an image with the city map of Barcelona in the background
    """

    m = staticmap.StaticMap(10000, 10000)
    paint_nodes(g, m)
    paint_edges(g, m)

    image = m.render()
    image.save(nom_fitxer)


def create_graph(i: str) -> None:
    """Function to be called from the demo, in order to call the functions."""
    g = get_buses_graph()
    if i == '3':
        show_buses(g)
    elif i == '4':
        plot_buses(g, 'graf_buses_bcn.png')
