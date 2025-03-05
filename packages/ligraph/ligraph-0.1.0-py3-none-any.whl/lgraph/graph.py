from collections import defaultdict
from queue import Queue
import heapq

class Graph:
    def __init__(self, vertices=None):
        """
        Initialize a graph with optional number of vertices
        
        Args:
            vertices: Number of vertices in the graph (optional)
        """
        self.vertices = vertices
        self.adjacency_list = {}
        self.edges = set()  # To track edges for testing
        self.graph = defaultdict(list)  # For compatibility with older code
    
    def add_edge(self, node1, node2):
        """
        Add an edge between two nodes in an undirected graph
        
        Args:
            node1: First node
            node2: Second node
        """
        if node1 not in self.adjacency_list:
            self.adjacency_list[node1] = []
        if node2 not in self.adjacency_list:
            self.adjacency_list[node2] = []
        
        self.adjacency_list[node1].append(node2)
        self.adjacency_list[node2].append(node1)  # For undirected graph
        
        # Add to edges set (for testing)
        self.edges.add((node1, node2))
        self.edges.add((node2, node1))
        
        # Update graph attribute for compatibility
        self.graph[node1].append(node2)
        self.graph[node2].append(node1)  # For undirected graph
    
    def addEdge(self, u, v):
        """
        Alternative method name for add_edge (for compatibility)
        """
        self.add_edge(u, v)
    
    def dfs(self, start_node, visited=None):
        """
        Depth-first search traversal
        
        Args:
            start_node: Starting node for traversal
            visited: Set of visited nodes (used in recursion)
            
        Returns:
            List of nodes in DFS order
        """
        if visited is None:
            visited = set()
        
        visited.add(start_node)
        result = [start_node]
        
        for neighbor in self.adjacency_list.get(start_node, []):
            if neighbor not in visited:
                result.extend(self.dfs(neighbor, visited))
                
        return result
    

    
    def depth_limited_search(self, src, target, max_depth):
        """
        Depth-limited search from source to target
        
        Args:
            src: Source node
            target: Target node
            max_depth: Maximum depth to search
            
        Returns:
            True if path exists within depth limit, False otherwise
        """
        if src == target:
            return True
        if max_depth <= 0:
            return False
            
        for neighbor in self.adjacency_list.get(src, []):
            if self.depth_limited_search(neighbor, target, max_depth - 1):
                return True
                
        return False
    
    def iterative_deepening_search(self, src, target, max_depth):
        """
        Iterative deepening search from source to target
        
        Args:
            src: Source node
            target: Target node
            max_depth: Maximum depth to search
            
        Returns:
            True if path exists within depth limit, False otherwise
        """
        for depth in range(max_depth + 1):
            if self.depth_limited_search(src, target, depth):
                return True
        return False

    def IDDFS(self, src, target, max_depth):
        """
        Alias for iterative_deepening_search (for compatibility)
        
        Args:
            src: Source node
            target: Target node
            max_depth: Maximum depth to search
            
        Returns:
            True if path exists within depth limit, False otherwise
        """
        return self.iterative_deepening_search(src, target, max_depth)
        
    def print_tree(self, root=0):
        """
        Print a tree representation of the graph starting from the root node
        
        Args:
            root: The starting node (root of the tree)
        """
        levels = {}  # Stores node levels for formatting
        q = Queue()
        q.put((root, 0))  # (node, level)
        visited = set([root])  # To avoid cycles
        max_level = 0

        while not q.empty():
            node, level = q.get()
            if level not in levels:
                levels[level] = []
            levels[level].append(str(node))
            max_level = max(max_level, level)
            
            for child in self.adjacency_list.get(node, []):
                if child not in visited:  # Avoid cycles
                    visited.add(child)
                    q.put((child, level + 1))

        # Print the tree in a structured way
        if not levels:
            print("Empty tree or invalid root node")
            return
            
        for lvl in range(max_level + 1):
            if lvl in levels:
                print("   " * (max_level - lvl) + "   ".join(levels[lvl]))
                if lvl < max_level and lvl + 1 in levels:
                    edges = "   " * (max_level - lvl - 1)
                    edges += " / \\" * (len(levels[lvl]) // 2)
                    if len(levels[lvl]) % 2 != 0:
                        edges += " /"
                    print(edges)
    
    # Alias for print_tree to maintain compatibility
    def printTree(self, root=0):
        """
        Alternative method name for print_tree (for compatibility)
        """
        self.print_tree(root)
        
    def bfs(self, start_node):
        """
        Breadth-first search traversal
        
        Args:
            start_node: Starting node for traversal
            
        Returns:
            List of nodes in BFS order
        """
        if start_node not in self.adjacency_list:
            return []
            
        visited = set([start_node])
        queue = Queue()
        queue.put(start_node)
        result = []
        
        while not queue.empty():
            current = queue.get()
            result.append(current)
            
            for neighbor in self.adjacency_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.put(neighbor)
                    
        return result

    def shortest_path(self, start_node, end_node, weight_func=None):
        """
        Find shortest path between start_node and end_node using Dijkstra's algorithm
        
        Args:
            start_node: Starting node
            end_node: Target node
            weight_func: Optional function to calculate weight between nodes (default: all edges = 1)
            
        Returns:
            Tuple of (distance, path) or (float('inf'), []) if no path exists
        """
        if start_node not in self.adjacency_list or end_node not in self.adjacency_list:
            return float('inf'), []
            
        # Default weight function (all edges have weight 1)
        if weight_func is None:
            weight_func = lambda u, v: 1
        
        # Priority queue for Dijkstra's algorithm
        distances = {node: float('inf') for node in self.adjacency_list}
        distances[start_node] = 0
        priority_queue = [(0, start_node)]
        previous = {node: None for node in self.adjacency_list}
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # If we reached the target node
            if current_node == end_node:
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = previous[current_node]
                return current_distance, list(reversed(path))
                
            # If we've found a longer path, skip
            if current_distance > distances[current_node]:
                continue
                
            # Check all neighbors
            for neighbor in self.adjacency_list[current_node]:
                weight = weight_func(current_node, neighbor)
                distance = current_distance + weight
                
                # If we found a shorter path
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return float('inf'), []  # No path found

    def find(self, parent, i):
        """Helper function for minimum_spanning_tree"""
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]
        
    def union(self, parent, rank, x, y):
        """Helper function for minimum_spanning_tree"""
        root_x = self.find(parent, x)
        root_y = self.find(parent, y)
        
        if root_x == root_y:
            return
            
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
            
    def minimum_spanning_tree(self, weight_func=None):
        """
        Find the minimum spanning tree of the graph using Kruskal's algorithm
        
        Args:
            weight_func: Optional function to calculate weight between nodes (default: all edges = 1)
            
        Returns:
            List of edges in the MST as tuples (node1, node2, weight)
        """
        if weight_func is None:
            weight_func = lambda u, v: 1
            
        # Create a list of all edges
        edges = []
        for node in self.adjacency_list:
            for neighbor in self.adjacency_list[node]:
                # Avoid duplicates in undirected graph (only include one direction)
                if (neighbor, node) not in [(e[0], e[1]) for e in edges]:
                    edges.append((node, neighbor, weight_func(node, neighbor)))
        
        # Sort edges by weight
        edges.sort(key=lambda x: x[2])
        
        # Initialize parent and rank for Union-Find
        nodes = list(self.adjacency_list.keys())
        parent = {node: node for node in nodes}
        rank = {node: 0 for node in nodes}
        
        # Result MST
        mst = []
        
        # Process edges
        for edge in edges:
            u, v, weight = edge
            root_u = self.find(parent, u)
            root_v = self.find(parent, v)
            
            # If including this edge doesn't create a cycle
            if root_u != root_v:
                mst.append(edge)
                self.union(parent, rank, root_u, root_v)
        
        return mst
    
    
def help():
    print(
            """
from collections import defaultdict

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def DLS(self, src, target, maxDepth):
        if src == target:
            return True
        if maxDepth <= 0:
            return False
        for i in self.graph[src]:
            if self.DLS(i, target, maxDepth - 1):
                return True
        return False

    def IDDFS(self, src, target, maxDepth):
        for i in range(maxDepth + 1):
            if self.DLS(src, target, i):
                return True
        return False


# Create a graph and test the IDDFS implementation
g = Graph(7)
g.addEdge(0, 1)
g.addEdge(0, 2)
g.addEdge(1, 3)
g.addEdge(1, 4)
g.addEdge(2, 5)
g.addEdge(2, 6)

target = 6
maxDepth = 3
src = 0

if g.IDDFS(src, target, maxDepth):
    print("Target is reachable from source within max depth.")
else:
    print("Target is NOT reachable from source within max depth.")

"""
        )