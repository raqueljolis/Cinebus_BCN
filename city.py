from typing import TypeAlias, Tuple
from buses import *
import networkx as nx
import osmnx as ox
from os.path import exists
import pickle
import staticmap
from datetime import timedelta


CityGraph: TypeAlias = nx.Graph
Stops: TypeAlias = str
OsmnxGraph: TypeAlias = nx.MultiDiGraph
Coord: TypeAlias = Tuple[float, float]   # (latitude, longitude)
Path: TypeAlias = list[str]


GRAPH_NAME = 'barcelona.grf'
BUS_STOP_LENGTH = 5
WALK_SPEED = 1.25  # m/s
BUS_SPEED = 3.5  # m/s


def get_osmnx_graph() -> OsmnxGraph:
    """
    If the graph is not alredy created it gets the graph of the streets of BCN from the OPM, 
    if it has been created previously it is search and load for its name
    """

    if not exists(GRAPH_NAME):
        graph: OsmnxGraph = ox.graph_from_place(
            "Barcelona", network_type='walk', simplify=True)
        for u, v, key, geom in graph.edges(data="geometry", keys=True):
            if geom is not None:
                del (graph[u][v][key]["geometry"])
        save_osmnx_graph(graph, GRAPH_NAME)
    else:
        graph: OsmnxGraph = load_osmnx_graph(GRAPH_NAME)

    return graph


def save_osmnx_graph(graph: OsmnxGraph, filename: str):
    """
    Saves the graph in the pickle
    """

    with open(filename, 'wb') as file:
        pickle.dump(graph, file)


def load_osmnx_graph(filename: str):
    """
    Loads the graph saved in the pickle
    """

    with open(filename, 'rb') as file:
        return pickle.load(file)


def add_street_nodes(g1: OsmnxGraph, G: CityGraph) -> None:
    """
    Adds the street nodes to the CityGraph
    """

    for n1 in g1.nodes:
        node = g1.nodes[n1]
        position: Coord = (node['y'], node['x'])
        G.add_node(n1, pos=position,  type='Cruilla')


def add_street_edges(g1: OsmnxGraph, G: CityGraph) -> None:
    """
    Adds the street edges to the CityGraph
    """

    for e1 in g1.edges:
        G.add_edge(e1[0], e1[1], type='Carrer', name=g1.edges[e1].get(
            'name', '-'), lenght=g1.edges[e1]['length'], speed=WALK_SPEED, time=g1.edges[e1]['length']/WALK_SPEED)


def add_buses_nodes(g1: OsmnxGraph, g2: BusesGraph, G: CityGraph) -> dict:
    """
    Adds the bus nodes to the Citygraph and search the nearest node of type 'Cruïlla' that is in the g1 graph.
    Then adds the edge that connects both nodes to the Citygraph
    """

    buses_stops: list[Stops] = [stop for stop in g2.nodes]
    coords_x: list[float] = [g2.nodes[stop]['pos'][0]
                             for stop in g2.nodes]  # Change the order of the coordinates
    coords_y: list[float] = [g2.nodes[stop]['pos'][1] for stop in g2.nodes]
    busos_cruilles: dict[str, int] = dict()

    # Add the nodes of type bus in the city graph G
    for i, stop in enumerate(buses_stops):
        position: Coord = (coords_x[i], coords_y[i])
        G.add_node(stop, pos=position, type='Parada', name=stop.split('_')[0])

    nearest_crossroads = ox.distance.nearest_nodes(g1, coords_y, coords_x)
    stops_crossroads = list(zip(buses_stops, nearest_crossroads))

    """stops_crossroads = []
    for a, b in zip(buses_stops, nearest_crossroads):
        stops_crossroads.append((a, b))"""

    busos_cruilles = {bus: cruilla for (bus, cruilla) in stops_crossroads}
    G.add_edges_from(stops_crossroads, type='Carrer', length=BUS_STOP_LENGTH,
                     speed=WALK_SPEED, time=BUS_STOP_LENGTH/WALK_SPEED)

    return busos_cruilles


def add_bus_edges(g1: OsmnxGraph, g2: BusesGraph, G: CityGraph, busos_cruilles: dict[str, int]) -> None:
    """
    Adds the bus edges to the CityGraph
    """

    for g2 in g2.edges:

        near_crui_1 = busos_cruilles[g2[0]]
        near_crui_2 = busos_cruilles[g2[1]]

        i = nx.shortest_path_length(
            g1, source=near_crui_1, target=near_crui_2, weight='time')
        G.add_edge(g2[0], g2[1], type='Bus', length=i,
                   speed=BUS_SPEED, time=i/BUS_SPEED)


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    """
    Builds the city graph by combining the Osmnx graph of streets (g1) and the BusesGraph (g2).
    """
    # Create an empty graph
    G: CityGraph = nx.Graph()

    add_street_nodes(g1, G)
    add_street_edges(g1, G)
    busos_cruilles = add_buses_nodes(g1, g2, G)
    add_bus_edges(g1, g2, G, busos_cruilles)

    return G


def find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> Path:
    """
    Returns the shortest path to arrive o a film.
    """

    x_coords = [src[1], dst[1]]
    y_coords = [src[0], dst[0]]

    src_node, dst_node = ox.distance.nearest_nodes(ox_g, x_coords, y_coords)
    path: list[str] = nx.shortest_path(
        g, source=src_node, target=dst_node, weight='time')

    return path


def find_path_time(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> float:
    """
    Finds the time in minutes that takes to go from src to dst and returns it
    """

    x_coords = [src[1], dst[1]]
    y_coords = [src[0], dst[0]]

    src_node, dst_node = ox.distance.nearest_nodes(ox_g, x_coords, y_coords)

    time: float = nx.shortest_path_length(
        g, source=src_node, target=dst_node, weight='time')
    return time


def show(g: CityGraph) -> None:
    """
    Displays the city graph interactively in a window.
    """

    pos = nx.get_node_attributes(g, 'pos')
    edges = [edge for edge in g.edges if edge[0]
             != edge[1]]  # Filter out self-loops
    nx.draw(g, pos=pos, edgelist=edges, node_size=5)
    plt.show()


def paint_nodes(G: CityGraph, m: staticmap.StaticMap) -> None:
    """
    Paints the nodes of the citygraph according to their type
    """

    for n in G.nodes:
        node = G.nodes[n]
        pos = node['pos']
        reversed_pos = (pos[1], pos[0])

        color = get_color(G, n)

        m.add_marker(staticmap.CircleMarker(reversed_pos, color, 10))


def paint_edges(G: CityGraph, m: staticmap.StaticMap) -> None:
    """
    Paints the edges of the citygraph according to their type
    """

    for n1 in G.edges.data():
        pos_node_1 = G.nodes[n1[0]]['pos']
        pos_node_2 = G.nodes[n1[1]]['pos']

        reversed_pos_1 = (pos_node_1[1], pos_node_1[0])
        reversed_pos_2 = (pos_node_2[1], pos_node_2[0])

        coord = (reversed_pos_1, reversed_pos_2)

        if G.edges[n1[0], n1[1]]['type'] == 'Carrer':
            line = staticmap.Line(coord, 'black', 1)
        else:
            line = staticmap.Line(coord, 'blue', 1)
        m.add_line(line)


def plot(G: CityGraph, filename: str) -> None:
    """
    Saves the CityGraph as an image with the city map in the background in a file called 'filename'
    """

    m = staticmap.StaticMap(6000, 6000)

    paint_nodes(G, m)
    paint_edges(G, m)

    image = m.render()
    image.save(filename)


def get_color(g: CityGraph, node: int | str) -> str:

    if g.nodes[node]['type'] == 'Cruilla':
        return 'green'
    else:
        return 'blue'


def plot_path(g: CityGraph, p: Path, filename: str) -> None:
    """
    Shows the path p on the city graph g and saves it as an image in the file specified by filename.
    """

    m = staticmap.StaticMap(2000, 2000)  # Create a StaticMap object
    coords1 = g.nodes[p[0]]['pos']
    color1 = get_color(g, p[0])

    coords1 = (coords1[1], coords1[0])
    coords2 = coords1
    start_marker = staticmap.CircleMarker(coords1, 'black', 15)
    m.add_marker(start_marker)

    for i in range(1, len(p)):
        coords2 = g.nodes[p[i]]['pos']
        coords2 = (coords2[1], coords2[0])
        color2 = get_color(g, p[i])

        line = staticmap.Line([list(coords1), list(coords2)], color1, 7)
        m.add_line(line)  # Add the line between consecutive nodes

        if color1 != color2:
            marker = staticmap.CircleMarker(coords2, color2, 12)
            m.add_marker(marker)
        else:
            marker = staticmap.CircleMarker(coords2, color1, 12)
            m.add_marker(marker)

        coords1 = coords2
        color1 = color2

    end_marker = staticmap.CircleMarker(coords2, "red", 30)
    m.add_marker(end_marker)

    image = m.render()
    image.save(filename)
