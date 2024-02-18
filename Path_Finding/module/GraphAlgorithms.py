import heapq
import numpy as np
import networkx as nx

class GraphAlgorithms:
    def __init__(self, graph):
        self.graph = graph
        
    def draw_graph(self) -> None:
        """Draws the graph.
        """
        pos = nx.circular_layout(self.graph)
        nx.draw(self.graph, pos=pos, with_labels=True, node_size=500, font_size=10)
        
    def draw_path(self, path: list) -> None:
        """Draws the path on the graph.
        
        Args:
            path (list): List of nodes in the path
        """
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        path_graph = nx.Graph()
        path_graph.add_edges_from(path_edges)

        pos = nx.circular_layout(self.graph)
        nx.draw(self.graph, pos=pos, with_labels=True, node_size=500, font_size=10)
        nx.draw_networkx_edges(path_graph, pos=pos, edgelist=path_edges, edge_color='b', width=2)
        
    def check_node_exists(self, node: str) -> bool:
        """Checks if a node exists in the graph.
        
        Args:
            node (str): Node
            
        Returns:
            bool: True if node exists, False otherwise
        """
        return node in self.graph.nodes

    def heuristic(self, node: str, goal_node: str) -> float:
        """Heuristic function for A* search algorithm.
        
        Args:
            node (str): Start node
            goal_node (str): Goal node
            
        Returns:
            float: Euclidean distance between two points in a two-dimensional plane
        """
        pos_node = self.graph.nodes[node]['pos']
        pos_goal = self.graph.nodes[goal_node]['pos']
        return ((pos_node[0] - pos_goal[0]) ** 2 + (pos_node[1] - pos_goal[1]) ** 2) ** 0.5

    def astar_search(self, start: str, goal: str) -> list | None:
        """A* search algorithm.
        
        Args:
            start (str): Start node
            goal (str): Goal node
            
        Returns:
            path (list): List of nodes in the path
            None: If no path is found
        """
        # The set of discovered nodes that may need to be (re-)expanded.
        # Initially, only the start node is known.
        # Implemented as a priority queue.
        open_set = [(0, start)]
        # For node n, g_scores[n] is the cost of the cheapest path from start to n currently known.
        g_scores = {node: float('inf') for node in self.graph.nodes}
        g_scores[start] = 0
        # For node n, f_scores[n] := g_scores[n] + h(n). f_scores[n] represents our current best guess as to
        # how short a path from start to finish can be if it goes through n.
        f_scores = {node: float('inf') for node in self.graph.nodes}
        f_scores[start] = self.heuristic(start, goal)
        came_from = {}

        while open_set:
            _, current_node = heapq.heappop(open_set)

            if current_node == goal:
                path = []
                while current_node in came_from:
                    path.append(current_node)
                    current_node = came_from[current_node]
                path.append(start)
                return path[::-1]  # Return reversed path

            for neighbor in self.graph.neighbors(current_node):
                # tentative_g_score is the distance from start to the neighbor through current_node
                tentative_g_score = g_scores[current_node] + self.graph[current_node][neighbor]['weight']

                if tentative_g_score < g_scores[neighbor]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[neighbor] = current_node
                    g_scores[neighbor] = tentative_g_score
                    f_scores[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_scores[neighbor], neighbor))
        # Open set is empty but goal was never reached
        return None

    def dijkstra(self, source: str, target: str) -> list | None:
        """Dijkstra's algorithm.

        Args:
            source (str): Start node
            target (str): Goal node

        Returns:
            path (list): List of nodes in the path
            None: If no path is found
        """
        visited = []
        unvisited = list(self.graph.nodes())
        for node in self.graph.nodes():
            self.graph.nodes[node]['dist'] = np.inf
            self.graph.nodes[node]['prev'] = None
        self.graph.nodes[source]['dist'] = 0

        while target not in visited:
            # Find summit with the shortest distance in unvisited
            summit = self.find_shortest_summit(unvisited)
            if summit is None:
                # No path found
                break
            unvisited.remove(summit)
            visited.append(summit)
            for neighbor in self.graph.neighbors(summit):
                if neighbor in unvisited:
                    # Calculate distance from source to neighbor
                    dist = self.graph.nodes[summit]['dist'] + self.graph.edges[summit, neighbor]['weight']
                    if dist < self.graph.nodes[neighbor]['dist']:
                        # Distance is shorter than previous distance -> update distance and previous node
                        self.graph.nodes[neighbor]['dist'] = dist
                        self.graph.nodes[neighbor]['prev'] = summit

        if self.graph.nodes[target]['prev'] is None:
            return None
        else:
            path = [target]
            while path[-1] != source:
                path.append(self.graph.nodes[path[-1]]['prev'])
            path.reverse()
            return path

    def find_shortest_summit(self, unvisited: list) -> str | None:
        """Finds the summit with the shortest distance.

        Args:
            unvisited (list): List of unvisited nodes

        Returns:
            summit (str): Summit with the shortest distance
            None: If no summit is found
        """
        min_dist = np.inf
        summit = None
        for node in unvisited:
            if self.graph.nodes[node]['dist'] < min_dist:
                min_dist = self.graph.nodes[node]['dist']
                summit = node
        return summit
    
    def compute_all_paths(self, start: str, end: str, keep: int) -> dict:
        """Computes all paths from a start node to an end node.
        
        Args:
            start (str): Start node
            end (str): End node
            keep (int): Number of paths to keep
            
        Returns:
            dict: Dictionary of paths
        """
        paths = {}
        for path in nx.all_simple_paths(self.graph, start, end):
            paths[tuple(path)] = self.compute_path_weight(path)
            
        # Sort paths by weight (ascending)
        paths = {k: v for k, v in sorted(paths.items(), key=lambda item: item[1])}
        # Keep only the first keep paths
        paths = dict(list(paths.items())[:keep])
        return paths
    
    def compute_path_weight(self, path: list) -> float:
        """Computes the weight of a path.
        
        Args:
            path (list): List of nodes in the path
            
        Returns:
            float: Weight of the path
        """
        weight = 0
        for i in range(len(path) - 1):
            weight += self.graph.get_edge_data(path[i], path[i + 1])['weight']
        return weight