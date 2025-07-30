from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def print_header():
    """Print application header with logo"""
    header_text = Text()
    header_text.append("🔍 ", style="bold yellow")
    header_text.append("HERACROSS", style="bold cyan")
    header_text.append(" - System Information Tool", style="bold white")
    
    panel = Panel(
        Align.center(header_text),
        style="bold blue",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def print_section_header(title):
    """Print a styled section header"""
    console.print(Rule(f"[bold cyan]{title}[/bold cyan]", style="cyan"))
    console.print()

def print_section(title, data, indent=0):
    """Print data sections with proper Rich formatting"""
    if not data:
        return
    
    # Handle different data types
    if isinstance(data, dict):
        print_dict_section(title, data, indent)
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        print_list_section(title, data, indent)
    else:
        print_simple_section(title, data, indent)

def print_dict_section(title, data, indent=0):
    """Print dictionary data as a table"""
    if not data:
        return
    
    # Create table with title
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        title_style="bold cyan",
        border_style="blue",
        header_style="bold magenta",
        show_header=True,
        expand=True
    )
    
    table.add_column("Property", style="cyan", no_wrap=True, width=25)
    table.add_column("Value", style="green", overflow="fold")
    
    for key, value in data.items():
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                # Handle nested list of dicts separately
                continue
            else:
                # Handle simple lists
                value_str = ", ".join(str(item) for item in value[:5])  
                if len(value) > 5:
                    value_str += f" ... (+{len(value) - 5} more)"
        elif isinstance(value, dict):
            # Handle nested dicts separately
            continue
        else:
            value_str = str(value)
        
        # Color coding for specific values
        if key.lower() in ["status", "state"]:
            if "up" in value_str.lower() or "active" in value_str.lower():
                value_str = f"[green]{value_str}[/green]"
            elif "down" in value_str.lower() or "inactive" in value_str.lower():
                value_str = f"[red]{value_str}[/red]"
        elif key.lower() in ["error", "warning"]:
            value_str = f"[red]{value_str}[/red]"
        elif key.lower() in ["temperature"] and "°C" in value_str:
            try:
                temp = float(value_str.replace("°C", ""))
                if temp > 80:
                    value_str = f"[red]{value_str}[/red]"
                elif temp > 60:
                    value_str = f"[yellow]{value_str}[/yellow]"
                else:
                    value_str = f"[green]{value_str}[/green]"
            except:
                pass
        
        table.add_row(key, value_str)
    
    console.print(table)
    
    # Handle nested structures
    for key, value in data.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            print_list_section(key, value, indent + 1)
        elif isinstance(value, dict):
            print_dict_section(key, value, indent + 1)
    
    console.print()

def print_list_section(title, data_list, indent=0):
    """Print list of dictionaries with improved formatting"""
    if not data_list:
        return
    
    # Create a panel for the section
    section_title = f"[bold cyan]{title}[/bold cyan]"
    
    if len(data_list) == 1:
        # Single item - use a simple table
        item = data_list[0]
        table = Table(
            title=section_title,
            border_style="blue",
            header_style="bold magenta",
            show_header=True,
            expand=True
        )
        
        table.add_column("Property", style="cyan", no_wrap=True, width=25)
        table.add_column("Value", style="green", overflow="fold")
        
        for key, value in item.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value[:3])
                if len(value) > 3:
                    value_str += f" ... (+{len(value) - 3} more)"
            else:
                value_str = str(value)
            
            table.add_row(key, value_str)
        
        console.print(table)
    
    else:
        # Multiple items - use a more compact format
        console.print(Panel(section_title, style="bold cyan"))
        
        for i, item in enumerate(data_list[:10], 1):  # Limit to 10 items
            # Create a compact table for each item
            item_table = Table(
                title=f"Item {i}",
                border_style="dim blue",
                show_header=False,
                box=None,
                padding=(0, 1),
                expand=True
            )
            
            item_table.add_column("Property", style="dim cyan", width=20)
            item_table.add_column("Value", style="white")
            
            # Show only the most important fields for list items
            important_fields = ["Device", "Name", "Product", "Model", "Interface", "Description", "Type", "Vendor"]
            
            for key, value in item.items():
                if key in important_fields or len(item) <= 4:
                    if isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value[:2])
                    else:
                        value_str = str(value)[:50]  
                    
                    item_table.add_row(key, value_str)
            
            console.print(item_table)
            
            if i < len(data_list) and i < 10:
                console.print()
        
        if len(data_list) > 10:
            console.print(f"[dim]... and {len(data_list) - 10} more items[/dim]")
    
    console.print()

def print_simple_section(title, data, indent=0):
    """Print simple data types"""
    console.print(f"[bold cyan]{title}:[/bold cyan] [green]{data}[/green]")
    console.print()

def print_summary_stats(stats):
    """Print summary statistics in a nice format"""
    if not stats:
        return
    
    columns = []
    for key, value in stats.items():
        stat_panel = Panel(
            Align.center(f"[bold green]{value}[/bold green]\n[dim]{key}[/dim]"),
            border_style="green",
            padding=(1, 2)
        )
        columns.append(stat_panel)
    
    console.print(Columns(columns, equal=True, expand=True))
    console.print()

def print_progress_bar(description="Loading system information..."):
    """Show a progress bar for loading"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=None)
        time.sleep(1)  # Simulate loading time

def print_error(message):
    """Print error message in a styled format"""
    console.print(Panel(
        f"[bold red]Error:[/bold red] {message}",
        border_style="red",
        padding=(1, 2)
    ))

def print_warning(message):
    """Print warning message in a styled format"""
    console.print(Panel(
        f"[bold yellow]Warning:[/bold yellow] {message}",
        border_style="yellow",
        padding=(1, 2)
    ))

def print_success(message):
    """Print success message in a styled format"""
    console.print(Panel(
        f"[bold green]Success:[/bold green] {message}",
        border_style="green",
        padding=(1, 2)
    ))

def print_footer():
    """Print application footer"""
    console.print()
    console.print(Rule(style="dim blue"))
    footer_text = Text()
    footer_text.append("Generated by ", style="dim")
    footer_text.append("Heracross", style="bold cyan")
    footer_text.append(" - System Information Tool", style="dim")
    console.print(Align.center(footer_text))

def clear_screen():
    """Clear the console screen"""
    console.clear()

def get_console():
    """Return the console instance for external use"""
    return console