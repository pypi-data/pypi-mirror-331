# File: codeanalyzer/__init__.py
from .analyzer import CodeAnalyzer

def analyze(file_path):
    """
    Analyze code file and return metrics.
    
    Args:
        file_path (str): Path to the file to analyze
        
    Returns:
        dict: Analysis results including complexity, time complexity, space complexity,
              memory usage, and potential code issues
    """
    try:
        with open(file_path, "r") as f:
            code = f.read()
        
        analyzer = CodeAnalyzer(code)
        result = analyzer.get_analysis()
        return result
    except Exception as e:
        return {"Error": f"Failed to analyze file: {str(e)}"}

# Expose the CodeAnalyzer class as well for more advanced usage
__all__ = ['analyze', 'CodeAnalyzer']