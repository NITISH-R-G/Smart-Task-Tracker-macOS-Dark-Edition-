import json
import os

def generate_readme(analysis_file="repo_analysis.json", mermaid_file="scripts/diagrams/architecture.mermaid", ai_summary_file="ai_summary.md", output_file="README.md"):
    """Generates the README.md by combining all analysis outputs."""

    # 1. Load Analysis
    try:
        with open(analysis_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"dependencies": [], "frameworks": []}

    # 2. Load Mermaid
    try:
        with open(mermaid_file, 'r') as f:
            mermaid_content = f.read()
    except FileNotFoundError:
        mermaid_content = "graph TD\n  NoData[Diagram will be generated on next run]"

    # 3. Load AI Summary
    try:
        with open(ai_summary_file, 'r') as f:
            ai_summary = f.read()
    except FileNotFoundError:
        ai_summary = "AI Summary pending generation."

    readme = f"""# Autonomous Repository

![CI/CD](https://img.shields.io/github/actions/workflow/status/example/repo/ci-cd.yml?label=CI/CD)
![Auto-Doc](https://img.shields.io/badge/Documentation-Auto--Generated-blue)

This repository is self-documenting and self-maintaining. It uses GitHub Actions, repository bots, and AI agents to continuously analyze, document, and explain itself.

## Project Overview (AI Generated)
{ai_summary}

## Architecture Diagram

```mermaid
{mermaid_content}
```

## Technology Stack

**Detected Frameworks:**
"""
    if data.get("frameworks"):
        for fw in data.get("frameworks"):
            readme += f"- {fw}\n"
    else:
        readme += "- Standard libraries/Unknown\n"

    readme += "\n**Key Dependencies:**\n"
    if data.get("dependencies"):
        for dep in data.get("dependencies")[:10]:
            readme += f"- {dep}\n"
        if len(data.get("dependencies", [])) > 10:
            readme += f"- ...and {len(data['dependencies']) - 10} more.\n"
    else:
        readme += "- None detected.\n"

    readme += """
## Repository Structure

Automatically mapped knowledge graph is available at `scripts/diagrams/knowledge_graph.json`.

## Setup Instructions

1. Clone the repository.
2. Install dependencies listed above.
3. Run standard build commands based on your framework.

## Contribution Guide

When you push changes, the repository will automatically:
1. Scan the new structure.
2. Update the knowledge graph and diagrams.
3. Generate AI summaries.
4. Commit the updated README back to the repository.

Please do not edit this README directly! It is auto-generated on every build.
"""

    with open(output_file, 'w') as f:
        f.write(readme)

    print(f"README generated successfully at {output_file}")

if __name__ == "__main__":
    generate_readme()
