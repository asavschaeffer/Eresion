# text_based_RPG/visualizer.py
import networkx as nx
import matplotlib.pyplot as plt
from text_based_RPG.modules import SimpleNeuronalGraph

def visualize_graph(graph: SimpleNeuronalGraph, output_path: str):
    """
    Generates and saves a visualization of the Eresion temporal graph.
    """
    if not graph.graph:
        print("[Visualizer] Graph is empty, skipping visualization.")
        return

    G = nx.DiGraph()
    edge_labels = {}

    for source, destinations in graph.graph.items():
        G.add_node(source)
        for destination, data in destinations.items():
            G.add_node(destination)
            
            # Combine weights for display
            co_occurrence = data.get('cooccurrence_weight', 0)
            succession = data.get('succession_weight', 0)
            
            if succession > 0:
                G.add_edge(source, destination, weight=succession)
                label = f"S:{succession:.1f}"
                if co_occurrence > 0:
                     label += f"\nC:{co_occurrence:.1f}"
                edge_labels[(source, destination)] = label
            
            elif co_occurrence > 0 and not G.has_edge(source, destination):
                 # Represent co-occurrence as a two-way arrow for clarity
                 G.add_edge(source, destination, weight=co_occurrence/2, style='dashed')
                 G.add_edge(destination, source, weight=co_occurrence/2, style='dashed')


    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G, k=0.9, iterations=50) # 'k' adjusts spacing

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='skyblue', alpha=0.9)
    
    # Draw edges
    edges = G.edges(data=True)
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=[d['weight'] for u,v,d in edges], 
                           arrowstyle='->', arrowsize=20, edge_color='gray')

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Eresion Neuronal Graph")
    plt.axis('off')
    plt.savefig(output_path, format="PNG")
    plt.close()
    print(f"[Visualizer] Graph saved to {output_path}")