from setuptools import setup, find_packages

setup(
    name="codeinsight",
    version="1.0.1",
    packages=find_packages(),
    author="Azad",
    author_email="azad1.dev0@gmail.com",
    description="Live time complexity and memory usage analysis for Python code",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Azad11014/codeanalyzer",
    project_urls={
        "Documentation": "https://github.com/Azad11014/codeinsight",
    },
    keywords="code analysis, complexity, performance, metrics, quality",
    python_requires=">=3.6",
    install_requires=[
        "radon",           
        "memory_profiler", 
        "astor",           
        "numpy",
        "rich",
        "click",       
    ],

    entry_points={
        'console_scripts': [
            'codeinsight=codeinsight.cli:main',
        ],
    },
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)