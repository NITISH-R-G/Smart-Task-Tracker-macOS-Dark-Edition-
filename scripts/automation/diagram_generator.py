import json
import os

def generate_interactive_diagram(analysis_file="repo_analysis.json", output_file="scripts/diagrams/interactive_architecture.html"):
    """Generates an interactive HTML diagram using vis.js from repository analysis data."""
    try:
        with open(analysis_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {analysis_file} not found.")
        return

    nodes = []
    edges = []

    # Root node
    nodes.append({"id": "Root", "label": "Repository", "group": "root", "url": "https://github.com"}) # In real scenario, link to repo root

    # Top-level directories
    top_dirs = set([d.split(os.sep)[0] for d in data.get("directories", []) if d])
    for d in top_dirs:
        node_name = d.replace("-", "_").replace(".", "_")
        nodes.append({"id": node_name, "label": d, "group": "dir", "url": f"https://github.com/tree/main/{d}"})
        edges.append({"from": "Root", "to": node_name})

        # Link files to their top-level directories
        files_in_dir = [f for f in data.get("files", []) if f.startswith(d + os.sep)]
        if files_in_dir:
            file_node_id = f"{node_name}_files"
            nodes.append({"id": file_node_id, "label": f"Files: {len(files_in_dir)}", "group": "files"})
            edges.append({"from": node_name, "to": file_node_id})

    # Files in root
    root_files = [f for f in data.get("files", []) if os.sep not in f]
    if root_files:
        nodes.append({"id": "Root_files", "label": f"Root Files: {len(root_files)}", "group": "files"})
        edges.append({"from": "Root", "to": "Root_files"})

    # Dependencies
    deps = data.get("dependencies", [])
    if deps:
        nodes.append({"id": "Deps", "label": "Dependencies", "group": "deps"})
        edges.append({"from": "Root", "to": "Deps"})
        for dep in deps[:15]: # Show up to 15 deps interactively
            dep_node = f"dep_{dep.replace('-', '_').replace('.', '_')}"
            frameworks = data.get("frameworks", [])
            is_python = any("Python" in fw for fw in frameworks) if frameworks else True
            url = f"https://pypi.org/project/{dep}/" if is_python else f"https://www.npmjs.com/package/{dep}"
            nodes.append({"id": dep_node, "label": dep, "group": "dep_item", "url": url})
            edges.append({"from": "Deps", "to": dep_node})

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Interactive Repository Architecture</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style type="text/css">
    #mynetwork {{
      width: 100%;
      height: 800px;
      border: 1px solid lightgray;
    }}
    body {{ font-family: sans-serif; }}
  </style>
</head>
<body>
<h2>Interactive Repository Architecture</h2>
<p>Click on nodes to navigate to source files or external dependencies.</p>
<div id="mynetwork"></div>

<script type="text/javascript">
  var nodes = new vis.DataSet({json.dumps(nodes)});
  var edges = new vis.DataSet({json.dumps(edges)});

  var container = document.getElementById('mynetwork');
  var data = {{
    nodes: nodes,
    edges: edges
  }};
  var options = {{
    nodes: {{
      shape: 'box',
      margin: 10,
      font: {{ size: 14 }}
    }},
    groups: {{
      root: {{ color: {{ background: '#f5b041', border: '#e67e22' }} }},
      dir: {{ color: {{ background: '#85c1e9', border: '#3498db' }} }},
      files: {{ color: {{ background: '#d7dbdd', border: '#99a3a4' }} }},
      deps: {{ color: {{ background: '#82e0aa', border: '#2ecc71' }} }},
      dep_item: {{ color: {{ background: '#eaeded', border: '#bdc3c7' }} }}
    }},
    layout: {{
      hierarchical: {{
        direction: 'UD',
        sortMethod: 'directed'
      }}
    }},
    physics: false
  }};
  var network = new vis.Network(container, data, options);

  network.on("click", function (params) {{
    if (params.nodes.length > 0) {{
      var nodeId = params.nodes[0];
      var node = nodes.get(nodeId);
      if (node.url) {{
        window.open(node.url, '_blank');
      }}
    }}
  }});
</script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)
    print(f"Interactive HTML diagram generated at {output_file}")


def generate_mermaid_diagram(analysis_file="repo_analysis.json", output_file="scripts/diagrams/architecture.mermaid"):
    """Generates a Mermaid diagram from repository analysis data."""
    try:
        with open(analysis_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {analysis_file} not found.")
        return

    mermaid_content = "graph TD\n"

    # Root node
    mermaid_content += "    Root[Repository]\n"

    # Top-level directories
    top_dirs = set([d.split(os.sep)[0] for d in data.get("directories", []) if d])
    for d in top_dirs:
        node_name = d.replace("-", "_").replace(".", "_")
        mermaid_content += f"    Root --> {node_name}[{d}]\n"

        # Link files to their top-level directories
        files_in_dir = [f for f in data.get("files", []) if f.startswith(d + os.sep)]
        # For simplicity, just show count of files or a generic 'files' node if there are many
        if files_in_dir:
            mermaid_content += f"    {node_name} --> {node_name}_files[Files: {len(files_in_dir)}]\n"

    # Files in root
    root_files = [f for f in data.get("files", []) if os.sep not in f]
    if root_files:
        mermaid_content += f"    Root --> Root_files[Root Files: {len(root_files)}]\n"

    # Add dependencies node
    deps = data.get("dependencies", [])
    if deps:
        mermaid_content += "    Root --> Deps[Dependencies]\n"
        # Just list top 5 to keep diagram manageable
        for dep in deps[:5]:
            dep_node = dep.replace("-", "_").replace(".", "_")
            mermaid_content += f"    Deps --> {dep_node}[{dep}]\n"
        if len(deps) > 5:
            mermaid_content += f"    Deps --> MoreDeps[... {len(deps) - 5} more]\n"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(mermaid_content)

    print(f"Mermaid diagram generated at {output_file}")

if __name__ == "__main__":
    generate_mermaid_diagram()
    generate_interactive_diagram()
