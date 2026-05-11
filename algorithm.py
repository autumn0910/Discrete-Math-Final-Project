import networkx as nx

def build_graph(raw_edges):
    """Constructs the base graph from the raw edge data."""
    G = nx.Graph()
    for edge in raw_edges:
        # edge format: [Node_A, Node_B, Weight]
        G.add_edge(edge[0], edge[1], weight=edge[2])
    return G

def get_mst(graph):
    """Computes the Minimum Spanning Tree (MST) using Kruskal's algorithm."""
    # networkx uses Kruskal's by default for minimum_spanning_tree
    mst = nx.minimum_spanning_tree(graph, weight='weight')
    return mst

def get_delivery_route(mst, start_node, required_stops):
    """Generates the delivery sequence, filtering out intersection/road nodes."""
    # 1. Get the raw DFS path (which includes roads)
    raw_route = list(nx.dfs_preorder_nodes(mst, source=start_node))
    
    # 2. Filter it! Only keep nodes that are in our required stops (plus the start)
    final_route = []
    for node in raw_route:
        if node in required_stops or node == start_node:
            final_route.append(node)
            
    return final_route

def calculate_route_cost(original_graph, route):
    """
    Calculates the total distance of the delivery route.
    Since DFS shortcuts through the original graph, we use shortest paths
    to find the true driving distance between sequential deliveries.
    """
    total_cost = 0
    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]
        try:
            # Find the shortest path distance in the ORIGINAL map
            cost = nx.shortest_path_length(original_graph, source=u, target=v, weight='weight')
            total_cost += cost
        except nx.NetworkXNoPath:
            pass
            
    return total_cost

def get_mst_weight(mst):
    """Returns the total weight (theoretical minimum) of the MST backbone."""
    return mst.size(weight='weight')
