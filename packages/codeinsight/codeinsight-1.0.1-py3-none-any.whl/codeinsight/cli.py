# File: codeanalyzer/cli.py
import click
from .analyzer import CodeInsight
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text
import time

@click.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed analysis")
def main(filepath, verbose):
    """Analyze code file and display metrics in a user-friendly format."""
    console = Console()
    
    try:
        file_size = os.path.getsize(filepath) / 1024  # Size in KB
        
        with Progress() as progress:
            task = progress.add_task("[green]Reading file...", total=100)
            progress.update(task, advance=30)
            
            with open(filepath, "r") as f:
                code = f.read()
                
            progress.update(task, advance=20, description="[yellow]Parsing code...")
            analyzer = CodeInsight(code)
            
            progress.update(task, advance=30, description="[blue]Analyzing...")
            time.sleep(0.5)  # Small delay for better UX on small files
            result = analyzer.get_analysis()
            
            progress.update(task, advance=20, description="[green]Finalizing...")
            time.sleep(0.3)  # Small delay for better UX
        
        console.print(f"\n[bold green]✓[/] Successfully analyzed [bold]{filepath}[/] ({file_size:.1f} KB)")
        
        # Check for code errors first
        code_errors = result.get("Code Errors", [])
        if code_errors:
            error_panel = Panel(
                "\n".join([f"• {error}" for error in code_errors]),
                title="[bold red]Potential Code Issues",
                border_style="red"
            )
            console.print(error_panel)
        
        # Display complexity metrics
        table = Table(title="Code Analysis Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Format cyclomatic complexity
        complexity_data = result["Complexity"]
        if complexity_data and not isinstance(complexity_data, dict) or (isinstance(complexity_data, dict) and "Error" not in complexity_data):
            if isinstance(complexity_data, dict):
                avg_complexity = sum(complexity_data.values()) / len(complexity_data) if complexity_data else 0
                max_complexity = max(complexity_data.values()) if complexity_data else 0
                table.add_row("Average Cyclomatic Complexity", f"{avg_complexity:.2f}")
                table.add_row("Maximum Cyclomatic Complexity", f"{max_complexity:.2f}")
                
                if verbose:
                    for func, complexity in complexity_data.items():
                        complexity_rating = get_complexity_rating(complexity)
                        table.add_row(f"  {func}", f"{complexity:.2f} ({complexity_rating})")
            else:
                table.add_row("Cyclomatic Complexity", str(complexity_data))
        else:
            table.add_row("Cyclomatic Complexity", "No functions found or error occurred")
        
        # Format Time Complexity
        time_complexity = result.get("Time Complexity", {})
        if time_complexity and isinstance(time_complexity, dict) and "Error" not in time_complexity:
            table.add_row("Time Complexity", "[bold]By Function[/]")
            
            # Sort functions by complexity severity
            complexity_order = {
                "O(1)": 1,
                "Amortized O(1)": 1.5,
                "O(log n)": 2,
                "O(n)": 3,
                "O(n log n)": 4,
                "O(n·k)": 4.5,
                "O(n²)": 5,
                "O(n³)": 6,
                "O(n^k)": 6.5,
                "O(2^n)": 7,
                "O(b^d)": 7.5,
                "O(n!)": 8,
                "O(V+E)": 3.5,
                "O(V²)": 5,
                "O(√n)": 2.5,
                "O(n^2.8)": 5.8
            }
            
            sorted_funcs = sorted(
                time_complexity.items(), 
                key=lambda x: complexity_order.get(x[1], 99)
            )
            
            for func, complexity in sorted_funcs:
                complexity_color = get_complexity_color(complexity)
                table.add_row(f"  {func}", f"[{complexity_color}]{complexity}[/]")
        else:
            table.add_row("Time Complexity", "Could not determine")
        
        # Format Space Complexity
        space_complexity = result.get("Space Complexity", {})
        if space_complexity and isinstance(space_complexity, dict) and "Error" not in space_complexity:
            table.add_row("Space Complexity", "[bold]By Function[/]")
            
            # Sort by complexity order
            sorted_funcs = sorted(
                space_complexity.items(),
                key=lambda x: complexity_order.get(x[1], 99)
            )
            
            for func, complexity in sorted_funcs:
                complexity_color = get_complexity_color(complexity)
                table.add_row(f"  {func}", f"[{complexity_color}]{complexity}[/]")
        else:
            table.add_row("Space Complexity", "Could not determine")
        
        # Format memory usage
        memory_usage = result["Memory Usage (MB)"]
        table.add_row("Memory Usage", f"{memory_usage:.4f} MB")
        
        # Format Halstead metrics
        halstead = result["Halstead Metrics"]
        if halstead:
            if verbose:
                for metric, value in halstead.items():
                    if isinstance(value, float):
                        table.add_row(f"Halstead {metric}", f"{value:.2f}")
                    else:
                        table.add_row(f"Halstead {metric}", f"{value}")
            else:
                # Fixed: Check if the halstead result is in the expected dictionary format
                if isinstance(halstead, dict):
                    # Access dictionary items safely using dict.get() method with default values
                    h_effort = halstead.get('effort', 0)
                    h_difficulty = halstead.get('difficulty', 0)
                    table.add_row("Maintainability", get_maintainability_rating(h_effort))
                    table.add_row("Code Difficulty", f"{h_difficulty:.2f}")
                else:
                    # Handle case where halstead is not a dictionary
                    table.add_row("Maintainability", "Cannot determine")
                    table.add_row("Code Difficulty", "Cannot determine")
        else:
            table.add_row("Maintainability", "Cannot determine")
            table.add_row("Code Difficulty", "N/A")
        
        console.print(table)
        
        # Provide recommendations
        recommendations = []
        
        # Check cyclomatic complexity
        if isinstance(complexity_data, dict) and complexity_data:
            high_complexity = [f for f, c in complexity_data.items() if c > 10]
            if high_complexity:
                complexity_rec = f"Consider refactoring these complex functions:\n"
                for func in high_complexity:
                    complexity_rec += f"  • {func} (complexity: {complexity_data[func]:.2f})\n"
                recommendations.append(complexity_rec)
        
        # Check time complexity
        if isinstance(time_complexity, dict) and time_complexity:
            inefficient_funcs = [f for f, c in time_complexity.items() 
                               if c in ["O(n²)", "O(n³)", "O(2^n)", "O(n!)"]]
            if inefficient_funcs:
                time_rec = f"Consider optimizing these inefficient functions:\n"
                for func in inefficient_funcs:
                    time_rec += f"  • {func} ({time_complexity[func]})\n"
                recommendations.append(time_rec)
        
        # Display recommendations if any
        if recommendations:
            rec_panel = Panel(
                "\n".join(recommendations),
                title="[bold yellow]⚠️ Recommendations",
                border_style="yellow"
            )
            console.print(rec_panel)
        
        # Add feedback footer
        console.print("\n[italic]For feedback or issues, please contact: Azad [/][link=mailto:azad1.dev0@gmail.com] <azad1.dev0@gmail.com>[/link] [italic]| GitHub: [/][link=https://github.com/Azad11014]Azad11014[/link]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        console.print("[red]Stack trace:[/]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)

def get_complexity_rating(complexity):
    if complexity <= 5:
        return "Good"
    elif complexity <= 10:
        return "Moderate"
    elif complexity <= 20:
        return "Complex"
    else:
        return "Very Complex"

def get_maintainability_rating(effort):
    if effort < 10000:
        return "Easy to maintain"
    elif effort < 100000:
        return "Moderately maintainable"
    elif effort < 1000000:
        return "Difficult to maintain"
    else:
        return "Very difficult to maintain"

def get_complexity_color(complexity):
    complexity_colors = {
        "O(1)": "green",
        "Amortized O(1)": "green",
        "O(log n)": "green",
        "O(√n)": "green",
        "O(n)": "green",
        "O(n log n)": "yellow",
        "O(n·k)": "yellow",
        "O(V+E)": "yellow",
        "O(n²)": "yellow",
        "O(V²)": "yellow",
        "O(n^2.8)": "red",
        "O(n³)": "red",
        "O(n^k)": "red",
        "O(2^n)": "red bold",
        "O(b^d)": "red bold",
        "O(n!)": "red bold"
    }
    return complexity_colors.get(complexity, "white")
if __name__ == "__main__":
    main()