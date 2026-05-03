# cli_interface.py
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.layout import Layout
from rich import box
from rich.align import Align
import pyfiglet
import time

class BLAXKCLI:
    def __init__(self):
        self.console = Console()
        self.version = "1.0.0"
    
    def show_banner(self):
        """Display cool ASCII banner"""
        self.console.clear()
        
        # Generate ASCII art
        banner = pyfiglet.figlet_format("BLAXK's BOT", font="slant")
        
        # Create styled panel
        banner_panel = Panel(
            Align.center(f"[bold cyan]{banner}[/bold cyan]\n[dim]AI-Powered Lead Generation System[/dim]\n[yellow]v{self.version}[/yellow]"),
            border_style="bright_magenta",
            box=box.DOUBLE
        )
        
        self.console.print(banner_panel)
        self.console.print()
    
    def show_config(self, location, queries_count):
        """Show configuration"""
        config_table = Table(show_header=False, box=box.SIMPLE, border_style="cyan")
        config_table.add_column("Setting", style="bold cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("📍 Location", location)
        config_table.add_row("🔍 Business Types", str(queries_count))
        config_table.add_row("🤖 Mode", "Headless Scraping")
        
        self.console.print(Panel(config_table, title="[bold]Configuration[/bold]", border_style="cyan"))
        self.console.print()
    
    def scraping_progress(self, query, current, total):
        """Show scraping progress"""
        return f"[cyan]🔍 Searching:[/cyan] [bold yellow]{query}[/bold yellow] [dim]({current}/{total})[/dim]"
    
    def show_results_table(self, leads):
        """Display results in a table"""
        table = Table(title="[bold green]🎯 Top Leads Found[/bold green]", box=box.ROUNDED, border_style="green")
        
        table.add_column("#", style="cyan", width=4)
        table.add_column("Business Name", style="bold yellow", width=25)
        table.add_column("Category", style="magenta", width=15)
        table.add_column("Rating", style="green", width=10)
        table.add_column("Reviews", style="blue", width=8)
        table.add_column("Priority", style="red", width=8)
        
        for i, lead in enumerate(leads[:10], 1):
            table.add_row(
                str(i),
                lead['name'][:24] + "..." if len(lead['name']) > 24 else lead['name'],
                lead.get('category', 'N/A')[:14],
                f"⭐ {lead['rating']}",
                str(lead['rating_count']),
                f"{lead.get('priority_score', 0)}/10"
            )
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def show_stats(self, total_scraped, with_phones, without_website):
        """Show statistics"""
        stats_table = Table(show_header=False, box=box.SIMPLE, border_style="yellow")
        stats_table.add_column("Metric", style="bold yellow")
        stats_table.add_column("Count", style="green", justify="right")
        
        stats_table.add_row("📊 Total Businesses Scraped", str(total_scraped))
        stats_table.add_row("🚫 Without Website", str(without_website))
        stats_table.add_row("📱 With Phone Numbers", str(with_phones))
        stats_table.add_row("✅ Ready for Outreach", str(with_phones))
        
        self.console.print(Panel(stats_table, title="[bold]Statistics[/bold]", border_style="yellow"))
        self.console.print()
    
    def success(self, message):
        """Success message"""
        self.console.print(f"[bold green]✓[/bold green] {message}")
    
    def error(self, message):
        """Error message"""
        self.console.print(f"[bold red]✗[/bold red] {message}")
    
    def warning(self, message):
        """Warning message"""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
    
    def info(self, message):
        """Info message"""
        self.console.print(f"[cyan]ℹ[/cyan] {message}")
    
    def step(self, message):
        """Step indicator"""
        self.console.print(f"\n[bold magenta]▶[/bold magenta] {message}")
    
    def show_whatsapp_banner(self, message_count):
        """WhatsApp sending banner"""
        self.console.print()
        panel = Panel(
            f"[bold green]📱 WhatsApp Message Sender[/bold green]\n\n"
            f"[cyan]Messages Ready:[/cyan] [bold yellow]{message_count}[/bold yellow]\n"
            f"[dim]Scan QR code to authenticate[/dim]",
            border_style="green",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
