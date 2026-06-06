import os
import json
import ast
from pathlib import Path

def analyze_repo(repo_path="."):
    """Scans the repository to build a structural representation."""
    repo_data = {
        "directories": [],
        "files": [],
        "dependencies": [],
        "frameworks": []
    }

    for root, dirs, files in os.walk(repo_path):
        # Ignore common hidden/build directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]

        rel_root = os.path.relpath(root, repo_path)
        if rel_root != '.':
            repo_data["directories"].append(rel_root)

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            repo_data["files"].append(rel_path)

            # Basic detection of dependencies and frameworks based on file names
            if file == "requirements.txt":
                with open(file_path, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    repo_data["dependencies"].extend(deps)
                    if any("flask" in d.lower() or "django" in d.lower() or "fastapi" in d.lower() for d in deps):
                        repo_data["frameworks"].append("Python Web Framework")

            elif file == "package.json":
                try:
                    with open(file_path, 'r') as f:
                        pkg_data = json.load(f)
                        deps = list(pkg_data.get("dependencies", {}).keys()) + list(pkg_data.get("devDependencies", {}).keys())
                        repo_data["dependencies"].extend(deps)
                        if "react" in deps or "vue" in deps or "angular" in deps:
                            repo_data["frameworks"].append("JavaScript Frontend Framework")
                except Exception:
                    pass

            # Additional simple parsing could be done here (e.g. Python ast to find imports)
            if file.endswith(".py"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for n in node.names:
                                    if n.name not in repo_data["dependencies"]:
                                        repo_data["dependencies"].append(n.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module and node.module not in repo_data["dependencies"]:
                                    repo_data["dependencies"].append(node.module)
                except Exception:
                    pass

    # Deduplicate
    repo_data["dependencies"] = list(set(repo_data["dependencies"]))
    repo_data["frameworks"] = list(set(repo_data["frameworks"]))

    return repo_data

if __name__ == "__main__":
    data = analyze_repo()
    with open("repo_analysis.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Repository analysis complete. Output saved to repo_analysis.json.")
