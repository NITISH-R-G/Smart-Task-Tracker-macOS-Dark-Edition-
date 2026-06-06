import json
import os

def generate_knowledge_graph(analysis_file="repo_analysis.json", output_file="scripts/diagrams/knowledge_graph.json"):
    """Builds a knowledge graph representation from repository analysis data."""
    try:
        with open(analysis_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {analysis_file} not found.")
        return

    graph = {
        "nodes": [],
        "edges": []
    }

    # Add Repository Node
    graph["nodes"].append({"id": "Repository", "label": "Repository", "type": "root"})

    # Add directory nodes and edges
    for d in data.get("directories", []):
        graph["nodes"].append({"id": d, "label": d, "type": "directory"})

        # Link to parent
        parent = os.path.dirname(d)
        if parent:
            graph["edges"].append({"source": parent, "target": d, "relationship": "contains"})
        else:
            graph["edges"].append({"source": "Repository", "target": d, "relationship": "contains"})

    # Add file nodes and edges
    for f in data.get("files", []):
        graph["nodes"].append({"id": f, "label": os.path.basename(f), "type": "file"})

        parent = os.path.dirname(f)
        if parent:
            graph["edges"].append({"source": parent, "target": f, "relationship": "contains"})
        else:
            graph["edges"].append({"source": "Repository", "target": f, "relationship": "contains"})

    # Add dependencies nodes and edges
    for dep in data.get("dependencies", []):
        dep_id = f"dep_{dep}"
        graph["nodes"].append({"id": dep_id, "label": dep, "type": "dependency"})
        graph["edges"].append({"source": "Repository", "target": dep_id, "relationship": "depends_on"})

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(graph, f, indent=2)

    print(f"Knowledge graph generated at {output_file}")

if __name__ == "__main__":
    generate_knowledge_graph()
