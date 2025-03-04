#analyzer.py
import ast
import memory_profiler
from radon.complexity import cc_visit
from radon.metrics import h_visit
import traceback
import re
import astor
import math
from collections import defaultdict

class CodeInsight:
    def __init__(self, code):
        self.code = code
        try:
            self.tree = ast.parse(code)
            self.parse_success = True
        except SyntaxError:
            self.parse_success = False
    
    def analyze_complexity(self):
        if not self.parse_success:
            return {"Error": "Syntax error in code"}
        
        try:
            complexity = cc_visit(self.code)
            return {func.name: func.complexity for func in complexity}
        except Exception as e:
            return {"Error": f"Failed to analyze complexity: {str(e)}"}

    def analyze_memory(self):
        if not self.parse_success:
            return 0.0
        
        try:
            # Wrap in a try-except to prevent crashes with problematic code
            def safe_exec(code_str):
                try:
                    exec(code_str)
                except Exception:
                    pass  # Silently handle execution errors
            
            # Set a timeout for memory profiling to handle potentially long-running code
            mem_usage = memory_profiler.memory_usage((safe_exec, (self.code,)), timeout=5)
            return max(mem_usage) - min(mem_usage) if mem_usage else 0.0
        except Exception:
            return 0.0

    def analyze_halstead(self):
        if not self.parse_success:
            return {}
        
        try:
            # The h_visit function might return a custom object or a dictionary
            # We need to handle both cases properly
            result = h_visit(self.code)
            
            # If result is not a dictionary, convert it to one
            if hasattr(result, '__dict__'):
                # Convert object attributes to dictionary
                return {key: getattr(result, key) for key in dir(result) 
                       if not key.startswith('__') and not callable(getattr(result, key))}
            elif isinstance(result, dict):
                return result
            else:
                # If it's neither an object with attributes nor a dictionary, return empty dict
                return {}
        except Exception as e:
            print(f"Halstead analysis error: {str(e)}")
            return {}
    
    def analyze_time_complexity(self):
        """Estimate time complexity by analyzing loops, conditionals, and recursive calls."""
        if not self.parse_success:
            return {}
        
        try:
            # Collect all functions with their bodies
            functions = {}
            for node in ast.walk(self.tree):
                if isinstance(node, ast.FunctionDef):
                    functions[node.name] = node
            
            complexities = {}
            
            for func_name, func_node in functions.items():
                # Convert AST to source code for pattern matching
                func_code = astor.to_source(func_node)
                
                # Initialize with O(1) complexity
                complexity = "O(1)"
                
                # Detect different algorithmic patterns
                algorithmic_patterns = {
                    "Dynamic Programming": self._has_dynamic_programming_pattern(func_node, func_code),
                    "Recursion": self._is_recursive(func_name, func_code),
                    "Divide and Conquer": self._has_divide_and_conquer(func_code),
                    "Backtracking": self._has_backtracking_pattern(func_code),
                    "BFS/DFS": self._has_graph_traversal(func_code),
                    "Greedy": self._has_greedy_pattern(func_code),
                    "Nested Loops": self._count_nested_loops(func_node)
                }
                
                # Advanced pattern detection for specific algorithms
                if algorithmic_patterns["Dynamic Programming"]:
                    # Most DP algorithms are O(n²) or O(n*k)
                    if self._has_multiple_state_dimensions(func_code):
                        complexity = "O(n²)" if self._count_nested_loops(func_node) > 1 else "O(n·k)"
                    else:
                        complexity = "O(n·k)"
                
                elif algorithmic_patterns["Backtracking"]:
                    # Backtracking often has exponential complexity
                    complexity = "O(b^d)"  # b = branching factor, d = depth
                
                elif algorithmic_patterns["BFS/DFS"]:
                    # Graph traversal: O(V+E) for adjacency list, O(V²) for adjacency matrix
                    complexity = "O(V+E)" if self._uses_adjacency_list(func_code) else "O(V²)"
                
                elif algorithmic_patterns["Recursion"]:
                    if algorithmic_patterns["Divide and Conquer"]:
                        if self._has_merge_operation(func_code):
                            complexity = "O(n log n)"  # Like merge sort
                        else:
                            complexity = "O(log n)"  # Like binary search
                    else:
                        # Check for memoization which can reduce complexity
                        if self._has_memoization(func_code):
                            complexity = "O(n)"
                        else:
                            # Simple recursion often leads to exponential complexity
                            complexity = "O(2^n)"
                
                elif algorithmic_patterns["Nested Loops"] > 0:
                    # Check for logarithmic patterns in loops
                    if self._has_logarithmic_pattern(func_code):
                        complexity = "O(log n)"
                    elif self._has_nlogn_pattern(func_code):
                        complexity = "O(n log n)"
                    else:
                        # Complexity based on loop nesting
                        loop_depth = algorithmic_patterns["Nested Loops"]
                        if loop_depth == 1:
                            complexity = "O(n)"  # Linear
                        elif loop_depth == 2:
                            complexity = "O(n²)"  # Quadratic
                        elif loop_depth == 3:
                            complexity = "O(n³)"  # Cubic
                        elif loop_depth > 3:
                            complexity = f"O(n^{loop_depth})"  # Higher polynomial
                
                # Handle amortized complexity cases
                if self._has_amortized_operations(func_code):
                    # For example, operations on Python lists that occasionally resize
                    complexity = complexity.replace("O(", "Amortized O(")
                
                # Check for matrix multiplication pattern
                if self._has_matrix_multiplication(func_code):
                    complexity = "O(n³)"  # Standard matrix multiplication
                    if self._has_strassen_algorithm(func_code):
                        complexity = "O(n^2.8)"  # Strassen's algorithm
                
                # Check for prime number algorithms
                if self._is_prime_check_algorithm(func_code):
                    complexity = "O(√n)"
                
                # Check for factorial time algorithms
                if self._has_permutation_generation(func_code):
                    complexity = "O(n!)"
                
                complexities[func_name] = complexity
            
            return complexities
        except Exception as e:
            return {"Error": f"Failed to analyze time complexity: {str(e)}"}
    
    def _is_recursive(self, func_name, func_code):
        """Check if a function calls itself."""
        # Simple pattern matching for function calls
        pattern = r'\b' + re.escape(func_name) + r'\s*\('
        return bool(re.search(pattern, func_code))
    
    def _count_nested_loops(self, node, current_depth=0):
        """Count the maximum nesting depth of loops in the AST."""
        max_depth = current_depth
        
        # Check if current node is a loop
        is_loop = isinstance(node, (ast.For, ast.While))
        current_depth = current_depth + 1 if is_loop else current_depth
        
        # Update max_depth if current_depth is greater
        max_depth = max(max_depth, current_depth)
        
        # Recursively check all child nodes
        for child in ast.iter_child_nodes(node):
            child_depth = self._count_nested_loops(child, current_depth)
            max_depth = max(max_depth, child_depth)
            
        return max_depth
    
    def _has_logarithmic_pattern(self, code):
        """Check for patterns indicating logarithmic complexity."""
        # Patterns indicating logarithmic behavior
        patterns = [
            r'\s*\/=\s*2',                    # division by 2
            r'\s*>>=\s*1',                    # right shift by 1
            r'\s*=\s*\w+\s*\/\s*2',           # assignment with division by 2
            r'\s*=\s*\w+\s*>>\s*1',           # assignment with right shift
            r'mid\s*=\s*\(\s*\w+\s*\+\s*\w+\s*\)\s*\/\/\s*2',  # binary search pattern
            r'binary_search',                 # named binary search
            r'bsearch',                       # shortened binary search name
            r'log\(.*\)',                     # logarithm function
            r'math\.log'                      # math.log function
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_nlogn_pattern(self, code):
        """Check for patterns indicating n*log(n) complexity."""
        # Common sorting algorithms like merge sort, quick sort
        patterns = [
            r'merge[_\s]*sort',
            r'quick[_\s]*sort',
            r'heap[_\s]*sort',
            r'\.sort\(',
            r'sorted\(',
            r'kruskal',                   # Kruskal's MST algorithm
            r'dijkstra',                  # Dijkstra's algorithm with priority queue
            r'priority_queue',            # Priority queue operations
            r'heapq',                     # Python's heapq module
            r'a\s*\*\s*math\.log\(a\)'    # Explicit n*log(n) calculations
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_dynamic_programming_pattern(self, node, code):
        """Detect dynamic programming patterns."""
        # Look for table initialization and filling
        dp_patterns = [
            r'dp\s*=\s*\[\s*\[\s*',       # 2D dp table initialization
            r'memo\s*=\s*\{\}',           # Memoization dict
            r'@lru_cache',                # Python's memoization decorator
            r'@functools\.lru_cache',     # Fully qualified lru_cache
            r'tabulation',                # Keyword in comments or variable names
            r'memoization',               # Keyword in comments or variable names
            r'bottom[_-]up',              # Bottom-up approach
            r'top[_-]down'                # Top-down approach
        ]
        
        for pattern in dp_patterns:
            if re.search(pattern, code):
                return True
                
        # Check for overlapping subproblems pattern
        has_array_access = False
        has_array_update = False
        
        for child_node in ast.walk(node):
            # Check for array access (reading)
            if isinstance(child_node, ast.Subscript) and isinstance(child_node.ctx, ast.Load):
                has_array_access = True
            # Check for array update (writing)
            elif isinstance(child_node, ast.Subscript) and isinstance(child_node.ctx, ast.Store):
                has_array_update = True
                
        # Both reading from and writing to arrays is a sign of DP
        return has_array_access and has_array_update
    
    def _has_multiple_state_dimensions(self, code):
        """Check if the DP state has multiple dimensions (like a 2D table)."""
        patterns = [
            r'dp\s*=\s*\[\s*\[\s*',                      # 2D list initialization
            r'\[\s*0\s*\]\s*\*\s*\w+\s*for\s*.+\]',      # List comprehension with nested structure
            r'dp\[\w+\]\[\w+\]',                         # 2D array access
            r'memo\[\(\w+,\s*\w+\)\]',                   # Tuple key with multiple values
            r'np\.zeros\(\(\w+,\s*\w+\)\)',              # NumPy 2D array
            r'array\(\[\s*\[\s*',                        # 2D array initialization
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_divide_and_conquer(self, code):
        """Check for divide and conquer patterns like in binary search or merge sort."""
        patterns = [
            r'mid\s*=\s*\(\s*\w+\s*\+\s*\w+\s*\)\s*\/\/\s*2',  # calculating midpoint
            r'binary[_\s]*search',
            r'merge[_\s]*sort',
            r'quick[_\s]*sort',
            r'divide[_\s]*and[_\s]*conquer',
            # Recursive calls on smaller parts of array
            r'\(\s*arr\[\s*:\s*mid\s*\]',                      # left half slice
            r'\(\s*arr\[\s*mid\s*:\s*\]',                      # right half slice
            r'\(\s*\w+\s*,\s*\w+\s*,\s*mid\s*\)',              # recursive call with mid
            r'\(\s*mid\s*\+\s*1\s*,\s*\w+\s*\)'                # recursive call after mid
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_merge_operation(self, code):
        """Check for merge operations typical in merge sort or similar algorithms."""
        patterns = [
            r'merge\(',                           # merge function call
            r'while\s+\w+\s*<\s*len\(\s*left\s*\)\s+and\s+\w+\s*<\s*len\(\s*right\s*\)',  # merging two arrays
            r'for\s+\w+\s+in\s+range\(\s*len\(left\)\s*\):',    # iterating over left array
            r'for\s+\w+\s+in\s+range\(\s*len\(right\)\s*\):',   # iterating over right array
            r'result\s*\+=\s*left\[',             # building result array
            r'result\s*\+=\s*right\['             # building result array
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_memoization(self, code):
        """Check if the function uses memoization to avoid redundant calculations."""
        patterns = [
            r'memo\s*=\s*\{\}',                   # memoization dict
            r'cache\s*=\s*\{\}',                  # cache dict
            r'@lru_cache',                        # Python's memoization decorator
            r'@functools\.lru_cache',             # Fully qualified lru_cache
            r'@memoize',                          # Custom memoize decorator
            r'if\s+\w+\s+in\s+memo',              # Checking memo dictionary
            r'memo\[\w+\]\s*=',                   # Storing result in memo
            r'return\s+memo\[\w+\]'               # Returning from memo
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_backtracking_pattern(self, code):
        """Check for backtracking algorithm patterns."""
        patterns = [
            r'backtrack\(',                        # backtrack function
            r'dfs\(',                              # depth-first search (often used in backtracking)
            r'solutions\s*\.\s*append\(.*\[:\]',   # Append a copy of current solution
            r'del\s+\w+\[\s*-\s*1\s*\]',          # Remove last element (backtracking)
            r'pop\(\s*\)',                         # Remove last element with pop
            r'for.*in.*:\s*\n\s*.*append\(.*\)(?:\s*\n\s*.*)+?\s*\n\s*.*pop\(\)', # Loop that appends and pops
            r'if\s+valid\(.*\):',                  # Checking if candidate is valid
            r'yield\s+from',                       # Generator delegation (used in some backtracking)
            # N-Queens problem indicators
            r'queens',
            r'n-queens',
            r'sudoku',
            r'permut\w+',                          # permutation-related
            r'combin\w+'                           # combination-related
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False

    def _has_graph_traversal(self, code):
        """Check for breadth-first or depth-first search patterns."""
        patterns = [
            r'bfs\(',                          # BFS function call
            r'dfs\(',                          # DFS function call
            r'visited\s*=\s*\[\s*\]',          # visited list/set
            r'visited\s*=\s*set\(\s*\)',       # visited set
            r'queue\s*=\s*\[\s*\]',            # queue for BFS
            r'stack\s*=\s*\[\s*\]',            # stack for DFS
            r'from\s+collections\s+import\s+deque', # importing deque
            r'deque\(\s*\[\s*\]\s*\)',         # creating a deque
            r'graph\s*=\s*.*\{\}',             # graph as dictionary
            r'adjacency\s*=',                  # adjacency list/matrix
            r'neighbors\s*=',                  # neighbors list
            r'while\s+\w+:(?:\s*\n\s*.*)+?pop\(\)', # While loop with pop (typical for BFS/DFS)
            r'while\s+len\(\s*\w+\s*\)\s*>\s*0', # Loop until queue/stack is empty
            r'for\s+\w+\s+in\s+graph\[\s*\w+\s*\]' # Iterating over neighbors
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False

    def _has_greedy_pattern(self, code):
        """Check for patterns indicating greedy algorithms."""
        patterns = [
            r'sort\(',                         # Sorting (common in greedy)
            r'\.sort\(',                       # Method-based sorting
            r'sorted\(',                       # Sorted function
            r'heapq\.',                        # Priority queue operations
            r'priority_queue',                 # Priority queue
            r'max\(',                          # Taking maximum
            r'min\(',                          # Taking minimum
            r'greedy',                         # Keyword in comments or names
            r'interval',                       # Interval scheduling problems
            r'activity',                       # Activity selection
            r'coin',                           # Coin change (sometimes greedy)
            r'huffman',                        # Huffman coding
            r'kruskal',                        # Kruskal's algorithm
            r'prim',                           # Prim's algorithm
            r'dijkstra'                        # Dijkstra's algorithm
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _uses_adjacency_list(self, code):
        """Check if code uses adjacency list (more efficient) vs adjacency matrix."""
        patterns = [
            r'graph\s*=\s*\{\}',               # Dictionary initialization
            r'graph\s*=\s*defaultdict\(list\)', # defaultdict for adjacency list
            r'graph\s*=\s*defaultdict\(set\)',  # defaultdict for adjacency list
            r'graph\[\s*\w+\s*\]\.append\(',    # Appending to adjacency list
            r'for\s+\w+\s+in\s+graph\[\s*\w+\s*\]'  # Iterating over adjacent nodes
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_amortized_operations(self, code):
        """Check for operations with amortized complexity."""
        patterns = [
            r'append\(',                       # List append (amortized O(1))
            r'pop\(\s*\)',                     # List pop from end (amortized O(1))
            r'push\(',                         # Stack push
            r'dynamic\s+array',                # Dynamic array
            r'resize\(',                       # Array resizing
            r'rehash\(',                       # Hash table rehashing
            r'rebalance\('                     # Tree rebalancing
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_matrix_multiplication(self, code):
        """Check for matrix multiplication patterns."""
        patterns = [
            r'for\s+i\s+in\s+range\(.*\):\s*\n\s*for\s+j\s+in\s+range\(.*\):\s*\n\s*for\s+k\s+in\s+range\(.*\)', # Triple nested loop
            r'result\[\s*i\s*\]\[\s*j\s*\]\s*\+=\s*.*\[\s*i\s*\]\[\s*k\s*\]\s*\*\s*.*\[\s*k\s*\]\[\s*j\s*\]', # Matrix mult formula
            r'matmul',                         # Matrix multiplication function
            r'np\.dot',                        # NumPy matrix multiplication
            r'@',                              # Python matrix multiplication operator
            r'np\.matmul'                      # NumPy explicit matmul
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_strassen_algorithm(self, code):
        """Check for Strassen's matrix multiplication algorithm."""
        patterns = [
            r'strassen',                       # Strassen algorithm name
            r'for\s+i\s+in\s+range\(.*n\/2',   # Half-sized matrices
            r'break\w+into\w+quadrants',       # Breaking matrix into 4 parts
            r'p1\s*=.*\(.*\+.*\)',             # Strassen's 7 products
            r'p2\s*=',
            r'p3\s*=',
            r'p4\s*=',
            r'p5\s*=',
            r'p6\s*=',
            r'p7\s*='
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _is_prime_check_algorithm(self, code):
        """Check if algorithm is checking for prime numbers."""
        patterns = [
            r'is_prime',                       # Prime checking function
            r'isprime',
            r'prime\(',
            r'sieve',                          # Sieve of Eratosthenes
            r'for\s+i\s+in\s+range\(2,\s*int\(math\.sqrt\(\w+\)\)\s*\+\s*1\)', # Common prime check loop
            r'n\s*%\s*i\s*==\s*0'              # Divisibility check
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_permutation_generation(self, code):
        """Check if algorithm generates permutations (O(n!) complexity)."""
        patterns = [
            r'permutation',                    # Permutation keyword
            r'permute',
            r'itertools\.permutation',         # Python's permutation generator
            r'factorial',                      # Factorial function
            r'math\.factorial',
            r'n!'                              # Factorial notation
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def analyze_space_complexity(self):
        """Estimate space complexity by analyzing variable usage and data structures."""
        if not self.parse_success:
            return {}
        
        try:
            # Collect all functions with their bodies
            functions = {}
            for node in ast.walk(self.tree):
                if isinstance(node, ast.FunctionDef):
                    functions[node.name] = node
            
            space_complexities = {}
            
            for func_name, func_node in functions.items():
                # Convert AST to source code for pattern matching
                func_code = astor.to_source(func_node)
                
                # Initialize with O(1) space complexity
                complexity = "O(1)"
                
                # Check for dynamic programming pattern (usually O(n) or O(n²) space)
                if self._has_dynamic_programming_pattern(func_node, func_code):
                    if self._has_multiple_state_dimensions(func_code):
                        complexity = "O(n²)"
                    else:
                        complexity = "O(n)"
                
                # Check if the function creates arrays/lists that depend on input size
                elif self._has_input_dependent_arrays(func_code):
                    complexity = "O(n)"
                
                # Check for recursive functions without tail recursion
                elif self._is_recursive(func_name, func_code) and not self._has_tail_recursion(func_code):
                    complexity = "O(n)" if complexity == "O(1)" else complexity
                
                # Check for space-intensive data structures (matrices, graphs)
                elif self._has_matrix_or_graph(func_code):
                    complexity = "O(n²)"
                
                # Check for graph algorithms
                elif self._has_graph_traversal(func_code):
                    complexity = "O(V+E)" if self._uses_adjacency_list(func_code) else "O(V²)"
                
                # Check for BFS specifically (usually uses more space than DFS)
                if self._has_bfs_pattern(func_code) and complexity == "O(n)":
                    complexity = "O(w)" # w = maximum width of the tree/graph
                
                # Higher dimensional data
                if self._has_3d_data_structure(func_code):
                    complexity = "O(n³)"
                
                # Special cases for specific algorithms
                if self._has_fibonacci_pattern(func_code) and "memo" not in func_code:
                    complexity = "O(1)" # Iterative Fibonacci uses constant space
                
                # Permutation or combination generation
                if self._has_permutation_generation(func_code):
                    complexity = "O(n!)" if "itertools.permutations" in func_code else "O(n)"
                
                space_complexities[func_name] = complexity
            
            return space_complexities
        except Exception as e:
            return {"Error": f"Failed to analyze space complexity: {str(e)}"}
    
    def _has_input_dependent_arrays(self, code):
        """Check if the function creates arrays or lists with size dependent on input."""
        patterns = [
            r'\[\s*0\s*\]\s*\*\s*\w+',      # [0] * n pattern
            r'\[\s*\w+\s*for\s*\w+\s*in\s*range\(\s*\w+\s*\)\]',  # list comprehension with range
            r'list\(\s*range\(\s*\w+\s*\)\)',  # list from range
            r'\[\s*\]\s*\*\s*\w+',            # [] * n pattern
            r'np\.zeros\(\s*\w+\s*\)',        # numpy zeros array
            r'np\.ones\(\s*\w+\s*\)',         # numpy ones array
            r'np\.empty\(\s*\w+\s*\)',        # numpy empty array
            r'np\.ndarray\(\s*\(\s*\w+\s*,',  # numpy ndarray with dimension
            r'array\(\s*shape=\(\s*\w+\s*,',  # array with shape parameter
            r'torch\.zeros\(\s*\w+\s*,',      # PyTorch tensors
            r'torch\.ones\(\s*\w+\s*,',
            r'torch\.empty\(\s*\w+\s*,'
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _has_tail_recursion(self, code):
        """Check if recursive calls are in tail position (last operation in function)."""
        # This is a simplified check - proper tail recursion analysis would require
        # more sophisticated AST analysis
        patterns = [
            r'return\s+\w+\(\s*.*\)',     # return func(...)
            r'return\s+self\.\w+\(\s*.*\)' # return self.func(...)
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
                
        return False
    
    def _has_matrix_or_graph(self, code):
        """Check if code uses matrix-like structures or graph representations."""
        patterns = [
            r'\[\s*\[\s*',                   # Nested list initialization
            r'array\(\s*\[\s*\[\s*',         # Numpy array initialization
            r'defaultdict\(\s*list\s*\)',    # Graph representation with adjacency list
            r'Graph\(',                      # Graph object creation
            r'Matrix\(',                     # Matrix object creation
            r'np\.zeros\(\s*\(\s*\w+\s*,\s*\w+\s*\)\)', # 2D numpy array
            r'np\.ones\(\s*\(\s*\w+\s*,\s*\w+\s*\)\)',  # 2D numpy array
            r'np\.ndarray\(\s*\(\s*\w+\s*,\s*\w+\s*\)\)', # 2D numpy array
            r'torch\.zeros\(\s*\w+\s*,\s*\w+\s*\)',     # 2D PyTorch tensor
            r'adjacency_matrix',             # Explicit adjacency matrix
            r'adjacency_list'                # Explicit adjacency list
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def get_analysis(self):
        """Perform comprehensive code analysis and return results."""
        result = {}
        
        # Check for code errors
        if not self.parse_success:
            result["Code Errors"] = ["Syntax error in code. Cannot proceed with analysis."]
            return result
        
        # Analyze cyclomatic complexity
        result["Complexity"] = self.analyze_complexity()
        
        # Analyze time complexity
        result["Time Complexity"] = self.analyze_time_complexity()
        
        # Analyze space complexity
        result["Space Complexity"] = self.analyze_space_complexity()
        
        # Analyze memory usage
        result["Memory Usage (MB)"] = self.analyze_memory()
        
        # Analyze Halstead metrics
        result["Halstead Metrics"] = self.analyze_halstead()
        
        # Check for potential code issues
        result["Code Errors"] = self.identify_code_issues()
        
        return result

    def identify_code_issues(self):
        """Identify potential code issues and bad practices."""
        issues = []
        
        if not self.parse_success:
            return ["Syntax error in code"]
            
        try:
            # Check for excessively long functions
            for node in ast.walk(self.tree):
                if isinstance(node, ast.FunctionDef):
                    lines_of_code = len(astor.to_source(node).split('\n'))
                    if lines_of_code > 50:
                        issues.append(f"Function '{node.name}' is too long ({lines_of_code} lines). Consider refactoring.")
            
            # Check for too many arguments
            for node in ast.walk(self.tree):
                if isinstance(node, ast.FunctionDef):
                    args_count = len(node.args.args)
                    if args_count > 5:
                        issues.append(f"Function '{node.name}' has too many arguments ({args_count}). Consider using a class or data structure.")
            
            # Check for deeply nested code
            for node in ast.walk(self.tree):
                if isinstance(node, (ast.For, ast.While, ast.If)):
                    nesting_level = self._get_nesting_level(node)
                    if nesting_level > 3:
                        issues.append(f"Found deeply nested code (level {nesting_level}). Consider refactoring to reduce complexity.")
            
            # Check for magic numbers
            magic_numbers = self._find_magic_numbers()
            if magic_numbers:
                issues.append(f"Found {len(magic_numbers)} magic numbers in the code. Consider using named constants.")
            
            # Check for potential infinite loops
            if self._has_potential_infinite_loop():
                issues.append("Detected potential infinite loop patterns. Ensure proper exit conditions.")
                
            # Check for duplicate code
            if self._has_duplicate_code():
                issues.append("Detected similar code patterns that might be duplicated. Consider refactoring.")
                
            return issues
        except Exception as e:
            return [f"Error identifying code issues: {str(e)}"]
        
    def _get_nesting_level(self, node, current_level=1):
        """Calculate the nesting level of code blocks."""
        max_level = current_level
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If)):
                child_level = self._get_nesting_level(child, current_level + 1)
                max_level = max(max_level, child_level)
        
        return max_level

    def _find_magic_numbers(self):
        """Find magic numbers (literal numbers used in code)."""
        magic_numbers = []
        allowed = [0, 1, -1, 2, 10, 100]  # Common numbers that aren't "magic"
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Num) and node.n not in allowed:
                # Exclude numbers in array/list index operations
                if not self._is_in_subscript(node):
                    magic_numbers.append(node.n)
        
        return magic_numbers

    def _is_in_subscript(self, node):
        """Check if a number is used as an index in a subscript."""
        # Get the parent of the node
        for parent in ast.walk(self.tree):
            for child in ast.iter_child_nodes(parent):
                if child == node and isinstance(parent, ast.Subscript):
                    return True
        return False

    def _has_potential_infinite_loop(self):
        """Check for patterns that might indicate infinite loops."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.While):
                # Check if the condition is a constant True
                if isinstance(node.test, ast.NameConstant) and node.test.value is True:
                    return True
                
                # Check for while True with no break statements
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    has_break = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Break):
                            has_break = True
                            break
                    if not has_break:
                        return True
        return False

    def _has_duplicate_code(self):
        """Basic check for potential code duplication."""
        # This is a simplified check - a real implementation would need
        # more sophisticated analysis (like AST comparison or text similarity)
        function_bodies = {}
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_body = astor.to_source(node)
                for existing_func, existing_body in function_bodies.items():
                    # Very simple check - if functions have similar sizes and significant content overlap
                    if (abs(len(func_body) - len(existing_body)) < len(func_body) * 0.2 and
                        len(func_body) > 100):  # Only consider substantial functions
                        return True
                function_bodies[node.name] = func_body
        
        return False

    def _has_bfs_pattern(self, code):
        """Check for breadth-first search patterns."""
        patterns = [
            r'queue\s*=\s*\[\s*\]',            # queue initialization
            r'queue\s*=\s*deque\(\s*\)',       # deque as queue
            r'queue\.append\(',                # queue operations
            r'queue\.popleft\(',
            r'queue\.pop\(0\)'                 # popping from beginning
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False

    def _has_3d_data_structure(self, code):
        """Check if code uses 3D data structures."""
        patterns = [
            r'\[\s*\[\s*\[\s*',                # 3D list initialization
            r'np\.zeros\(\s*\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)\)', # 3D numpy array
            r'np\.ones\(\s*\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)\)',  # 3D numpy array
            r'array\(\s*shape=\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)\)' # 3D array with shape
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False

    def _has_fibonacci_pattern(self, code):
        """Check for Fibonacci sequence calculation patterns."""
        patterns = [
            r'fib',                           # fibonacci name variants
            r'fibonacci',
            r'a, b = 0, 1',                   # typical initialization
            r'a, b = 1, 1',
            r'\w+\s*=\s*\w+\s*\+\s*\w+'       # summation pattern
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
# Main function to analyze code from a file or string
def analyze(input_source):
    """
    Analyze Python code from a file path or code string.
    
    Args:
        input_source (str): Either a file path or a Python code string
    
    Returns:
        dict: Analysis results
    """
    # Check if input is a file path
    try:
        if input_source.endswith('.py'):
            try:
                with open(input_source, 'r') as file:
                    code = file.read()
            except Exception as e:
                return {"Error": f"Failed to read file: {str(e)}"}
        else:
            # Treat as a code string
            code = input_source
    except Exception as e:
        return {"Error": f"Invalid input: {str(e)}"}
    
    # Create analyzer and return results
    analyzer = CodeInsight(code)
    return analyzer.get_analysis()