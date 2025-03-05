import unittest
from ligraph.graph import Graph

class TestGraph(unittest.TestCase):
    def setUp(self):
        # Create a sample graph for testing
        self.g = Graph()
        
        # Create a simple undirected graph
        #    A
        #   / \
        #  B   C
        # / \
        #D   E
        self.g.add_edge('A', 'B')
        self.g.add_edge('A', 'C')
        self.g.add_edge('B', 'D')
        self.g.add_edge('B', 'E')
        
        # Create a numeric graph for testing iterative deepening
        self.num_graph = Graph()
        self.num_graph.add_edge(0, 1)
        self.num_graph.add_edge(0, 2)
        self.num_graph.add_edge(1, 3)
        self.num_graph.add_edge(1, 4)
        self.num_graph.add_edge(2, 5)
        self.num_graph.add_edge(2, 6)

    def test_initialization(self):
        """Test that graph initializes correctly with and without vertices"""
        g1 = Graph()
        self.assertEqual(g1.adjacency_list, {})
        
        g2 = Graph(5)
        self.assertEqual(g2.vertices, 5)
        self.assertEqual(g2.adjacency_list, {})

    def test_add_edge(self):
        """Test adding edges to the graph"""
        g = Graph()
        g.add_edge('X', 'Y')
        
        # Check adjacency list
        self.assertIn('Y', g.adjacency_list['X'])
        self.assertIn('X', g.adjacency_list['Y'])
        
        # Check edges set
        self.assertIn(('X', 'Y'), g.edges)
        self.assertIn(('Y', 'X'), g.edges)

    def test_add_edge_compatibility(self):
        """Test the compatibility method addEdge"""
        g = Graph()
        g.addEdge('P', 'Q')
        
        self.assertIn('Q', g.adjacency_list['P'])
        self.assertIn('P', g.adjacency_list['Q'])

    def test_dfs(self):
        """Test depth-first search traversal"""
        # Starting from A should visit all nodes
        result = self.g.dfs('A')
        self.assertEqual(set(result), {'A', 'B', 'C', 'D', 'E'})
        
        # Starting from B should only visit B, D, and E
        result = self.g.dfs('B')
        self.assertEqual(set(result), {'B', 'D', 'E', 'A', 'C'})
        
        # Order matters in DFS
        result = self.g.dfs('A')
        self.assertEqual(result[0], 'A')  # A should be first

    def test_depth_limited_search(self):
        """Test depth limited search"""
        # Should find target at depth 0
        self.assertTrue(self.g.depth_limited_search('A', 'A', 0))
        
        # Should find B at depth 1 from A
        self.assertTrue(self.g.depth_limited_search('A', 'B', 1))
        
        # Should not find D at depth 1 from A
        self.assertFalse(self.g.depth_limited_search('A', 'D', 1))
        
        # Should find D at depth 2 from A
        self.assertTrue(self.g.depth_limited_search('A', 'D', 2))

    def test_iterative_deepening_search(self):
        """Test iterative deepening search"""
        # Should find all nodes from A with sufficient depth
        self.assertTrue(self.num_graph.iterative_deepening_search(0, 6, 2))
        
        # Should not find node 6 from 0 with depth 1
        self.assertFalse(self.num_graph.iterative_deepening_search(0, 6, 1))
        
        # Should find node 3 from 0 with depth 2
        self.assertTrue(self.num_graph.iterative_deepening_search(0, 3, 2))

    def test_print_functions(self):
        """Test that print functions don't raise exceptions"""
        # This just verifies the methods run without errors
        try:
            self.num_graph.print_tree(0)
            self.num_graph.printTree(0)
        except Exception as e:
            self.fail(f"print_tree/printTree raised exception: {e}")
            
    def test_bfs(self):
        """Test breadth-first search traversal"""
        # Starting from A should visit all nodes in BFS order
        result = self.g.bfs('A')
        self.assertEqual(set(result), {'A', 'B', 'C', 'D', 'E'})
        
        # A should be first
        self.assertEqual(result[0], 'A')
        
        # B and C should come before D and E in BFS order
        b_index = result.index('B')
        c_index = result.index('C')
        d_index = result.index('D')
        e_index = result.index('E')
        
        self.assertTrue(b_index < d_index)
        self.assertTrue(b_index < e_index)

    def test_shortest_path(self):
        """Test Dijkstra's shortest path algorithm"""
        # Path from A to E should be [A, B, E]
        distance, path = self.g.shortest_path('A', 'E')
        self.assertEqual(path, ['A', 'B', 'E'])
        self.assertEqual(distance, 2)
        
        # Path from D to C should be [D, B, A, C]
        distance, path = self.g.shortest_path('D', 'C')
        self.assertEqual(path, ['D', 'B', 'A', 'C'])
        self.assertEqual(distance, 3)
        
        # No path to Z
        distance, path = self.g.shortest_path('A', 'Z')
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))

    def test_minimum_spanning_tree(self):
        """Test minimum spanning tree algorithm"""
        # For our simple graph, the MST should have 4 edges
        mst = self.g.minimum_spanning_tree()
        self.assertEqual(len(mst), 4)
        
        # Check that the edges connect all nodes
        nodes = set()
        for edge in mst:
            nodes.add(edge[0])
            nodes.add(edge[1])
        self.assertEqual(nodes, {'A', 'B', 'C', 'D', 'E'})

if __name__ == '__main__':
    unittest.main()