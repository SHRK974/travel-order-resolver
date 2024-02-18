import networkx as nx
import pandas as pd
import json

class FranceGraphBuilder:
    def __init__(self, city_data_file='module/data/fr.csv', graph_data_file='module/data/fr.json'):
        self.city_data_file = city_data_file
        self.graph_data_file = graph_data_file

    def create_graph(self) -> nx.Graph:
        """Creates a graph from the city data and graph data files.
        
        Returns:
            nx.Graph: Graph of France
        """
        graph = nx.Graph()
        df = pd.read_csv(self.city_data_file)
        for _, row in df.iterrows():
            graph.add_node(row['city'], pos=(row['lat'], row['lng']))

        with open(self.graph_data_file) as f:
            data = json.load(f)
            for summit_def in data['graph']:
                summit = summit_def['from_city']
                edges = summit_def['to_cities']
                for edge in edges:
                    to_summit = edge['name']
                    weight = edge['weight']
                    graph.add_edge(summit, to_summit, weight=weight)

        graph.remove_nodes_from(list(nx.isolates(graph)))
        return graph