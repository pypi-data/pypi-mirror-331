# 🔍 CodeInsight

<div align="center">

[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/codeinsight/)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

**A comprehensive toolkit for analyzing Python code complexity, quality, and performance metrics**

</div>

## ✨ Overview

CodeInsight helps developers identify bottlenecks, complexity issues, and potential bugs in Python code. By providing detailed metrics and visualizations, it empowers teams to write cleaner, more maintainable, and more efficient code.

## 🚀 Installation

```bash
pip install codeinsight
```

## 🏁 Quick Start

### Command Line Usage

```bash
# Basic analysis of a file
codeinsight example.py

# Analyze a directory with detailed reporting
codeinsight ./src --verbose
```

### As a Python Library

```python
# Import the analyze function
from codeinsight import analyze

# Analyze a file
result = analyze("example.py")
print(result)

# Or use the CodeInsight class directly for more control
from codeinsight import CodeInsight

with open("example.py", "r") as f:
    code = f.read()

analyzer = CodeInsight(code)
result = analyzer.get_analysis()
print(result)
```

## 🛠️ Features

| Feature | Description |
|---------|-------------|
| **Complexity Analysis** | Calculate cyclomatic complexity, cognitive complexity, and Halstead metrics |
| **Performance Metrics** | Estimate time and space complexity, track memory usage |
| **Code Quality** | Detect code smells, anti-patterns, and maintainability issues |

### Supported Analysis Types

- **Structural Analysis**: AST-based parsing for deep code understanding
- **Complexity Metrics**: Cyclomatic, cognitive, and Halstead complexity
- **Performance Profiling**: Execution time and memory usage estimation
- **Pattern Detection**: Identify common anti-patterns and code smells
- **Documentation Coverage**: Measure docstring completeness and quality

## 🔧 Requirements

- Python 3.6+
- click
- rich
- memory_profiler
- radon
- astor

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💖 Acknowledgements

- The [Radon](https://github.com/rubik/radon) project for complexity metrics
- [AST](https://docs.python.org/3/library/ast.html) module from the Python standard library
- All our [contributors](https://github.com/Azad11014/codeinsight/graphs/contributors)

