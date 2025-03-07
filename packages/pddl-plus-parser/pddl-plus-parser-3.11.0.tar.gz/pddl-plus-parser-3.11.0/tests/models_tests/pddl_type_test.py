"""Contains some tests for the functionality in the PDDL domain class."""
import networkx as nx

from pddl_plus_parser.models import PDDLType
from pddl_plus_parser.models.pddl_type import create_type_hierarchy_graph


def find_root_nodes(G: nx.DiGraph) -> str:
    """
    Finds the root nodes of the directed graph (nodes with in-degree 0).
    """
    return [node for node in G.nodes if G.in_degree(node) == 0][0]


def test_create_type_hierarchy_graph_creates_correct_graph_from_input_data():
    t1 = PDDLType("object")
    t2 = PDDLType("vehicle", t1)
    t3 = PDDLType("car", t2)
    t4 = PDDLType("truck", t2)
    t5 = PDDLType("sedan", t3)

    # Dictionary of types
    types_dict = {
        "object": t1,
        "vehicle": t2,
        "car": t3,
        "truck": t4,
        "sedan": t5
    }

    # Create the graph
    type_hierarchy_graph = create_type_hierarchy_graph(types_dict)
    hierarchy_bfs = list(nx.bfs_tree(type_hierarchy_graph, find_root_nodes(type_hierarchy_graph)).nodes())
    assert hierarchy_bfs == ["object", "vehicle", "car", "truck", "sedan"]



def test_create_type_hierarchy_graph_creates_correct_graph_from_input_data_when_more_complex_hierarchy_introduced():
    t1 = PDDLType("object")
    t2 = PDDLType("vehicle", t1)
    t3 = PDDLType("car", t2)
    t4 = PDDLType("truck", t2)
    t5 = PDDLType("sedan", t3)
    t6 = PDDLType("hatchback", t3)
    t7 = PDDLType("pickup", t4)
    t8 = PDDLType("bus", t2)

    # Dictionary of types
    types_dict = {
        "object": t1,
        "vehicle": t2,
        "car": t3,
        "truck": t4,
        "sedan": t5,
        "hatchback": t6,
        "pickup": t7,
        "bus": t8
    }

    # Create the graph
    type_hierarchy_graph = create_type_hierarchy_graph(types_dict)
    hierarchy_bfs = list(nx.bfs_tree(type_hierarchy_graph, find_root_nodes(type_hierarchy_graph)).nodes())
    assert hierarchy_bfs == ["object", "vehicle", "car", "truck", "bus", "sedan", "hatchback", "pickup"]