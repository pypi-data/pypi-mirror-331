# ligraph Package

ligraph is a Python package designed to provide a simple and efficient way to work with graph data structures. It includes functionalities to create graphs, add edges, and perform various graph operations and algorithms.

## Installation

To install the ligraph package, you can use pip:

```
pip install ligraph
```

## Usage

Here is a basic example of how to use the ligraph package:

```python
from ligraph.graph import Graph

# Create a new graph with 7 vertices
g = Graph(7)

# Add edges
g.addEdge(0, 1)
g.addEdge(0, 2)
g.addEdge(1, 3)
g.addEdge(1, 4)
g.addEdge(2, 5)
g.addEdge(2, 6)

# Check if a path exists using Iterative Deepening DFS
target = 6
maxDepth = 3
src = 0

if g.IDDFS(src, target, maxDepth):
    print("Target is reachable from source within max depth.")
else:
    print("Target is NOT reachable from source within max depth.")

# Visualize the graph as a tree
g.printTree(0)
```

## Features

- Create and manage graphs
- Add edges between nodes
- Easy-to-use interface

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.