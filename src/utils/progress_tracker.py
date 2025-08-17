"""
Progress tracking utilities for Universal Product Scraper.

Provides visual progress indicators for scraping operations using rich library.
"""

from typing import Optional, Any
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import time
from datetime import datetime


class ScrapingProgressTracker:
    """Manages progress display for scraping operations."""
    
    def __init__(self, total_products: int, mode: str = "HEADLESS"):
        """
        Initialize progress tracker.
        
        Args:
            total_products: Total number of products to process
            mode: Scraping mode (HEADLESS/VISIBLE)
        """
        self.console = Console()
        self.total_products = total_products
        self.mode = mode
        self.current_product = 0
        self.current_product_name = ""
        self.vendors_found = 0
        self.total_vendors_processed = 0
        self.start_time = time.time()
        
        # Create a single progress bar that we'll reuse
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
        
        # Task IDs
        self.batch_task = None
        self.vendor_task = None
        
    def start(self):
        """Start progress tracking."""
        self.batch_task = self.progress.add_task(
            f"[bold blue]Processing {self.total_products} products...",
            total=self.total_products
        )
        self.progress.start()
        
    def start_product(self, product_index: int, product_name: str, price: float):
        """
        Start processing a new product.
        
        Args:
            product_index: Current product index (1-based)
            product_name: Name of the product
            price: Original price
        """
        self.current_product = product_index
        self.current_product_name = product_name
        
        # Update batch progress
        self.progress.update(
            self.batch_task,
            description=f"[bold blue]Product {product_index}/{self.total_products}: {product_name[:50]}...",
            completed=product_index - 1
        )
        
        # Clear previous vendor progress if exists
        if self.vendor_task is not None:
            self.progress.remove_task(self.vendor_task)
            self.vendor_task = None
            
        self.console.print(f"\n[bold cyan]📋 Processing: {product_name}")
        self.console.print(f"[dim]💰 Original Price: ₪{price}")
        
    def start_vendor_extraction(self, total_vendors: int):
        """
        Start vendor extraction for current product.
        
        Args:
            total_vendors: Total number of vendors to extract
        """
        self.vendors_found = total_vendors
        
        if total_vendors > 0:
            # Add vendor task to the same progress bar
            self.vendor_task = self.progress.add_task(
                f"[cyan]Extracting {total_vendors} vendors...",
                total=total_vendors
            )
            
    def update_vendor_progress(self, vendor_index: int, vendor_name: str, price: Optional[float] = None):
        """
        Update vendor extraction progress.
        
        Args:
            vendor_index: Current vendor index (1-based)
            vendor_name: Name of the vendor
            price: Vendor price if extracted
        """
        if self.vendor_task is not None:
            status = f"[cyan]Vendor {vendor_index}/{self.vendors_found}: {vendor_name}"
            if price:
                status += f" - ₪{price}"
                
            self.progress.update(
                self.vendor_task,
                description=status,
                completed=vendor_index
            )
            
        self.total_vendors_processed += 1
        
    def complete_vendor_extraction(self, vendors_extracted: int):
        """
        Complete vendor extraction for current product.
        
        Args:
            vendors_extracted: Number of vendors successfully extracted
        """
        if self.vendor_task is not None:
            self.progress.update(self.vendor_task, completed=self.vendors_found)
            self.progress.remove_task(self.vendor_task)
            self.vendor_task = None
            
        # Show summary
        success_rate = (vendors_extracted / self.vendors_found * 100) if self.vendors_found > 0 else 0
        status_color = "green" if success_rate >= 80 else "yellow" if success_rate >= 50 else "red"
        
        self.console.print(
            f"[{status_color}]✅ Extracted {vendors_extracted}/{self.vendors_found} vendors "
            f"({success_rate:.1f}% success rate)"
        )
        
    def complete_product(self, product_index: int, processing_time: float, vendors_found: int):
        """
        Complete processing of a product.
        
        Args:
            product_index: Product index that was completed
            processing_time: Time taken to process this product
            vendors_found: Number of vendors found
        """
        # Update batch progress
        self.progress.update(
            self.batch_task,
            completed=product_index
        )
        
        # Calculate statistics
        elapsed = time.time() - self.start_time
        avg_time_per_product = elapsed / product_index
        remaining_products = self.total_products - product_index
        eta_seconds = avg_time_per_product * remaining_products
        
        # Display product completion summary
        self.console.print(
            f"[green]✓ Completed:[/green] {self.current_product_name[:50]} | "
            f"[yellow]{vendors_found} vendors[/yellow] | "
            f"[dim]{processing_time:.1f}s[/dim]"
        )
        
        if remaining_products > 0:
            self.console.print(
                f"[dim]ETA: {self._format_time(eta_seconds)} | "
                f"Avg: {avg_time_per_product:.1f}s/product[/dim]\n"
            )
            
    def show_error(self, message: str, error_type: str = "ERROR"):
        """
        Display an error message.
        
        Args:
            message: Error message to display
            error_type: Type of error (ERROR, WARNING, INFO)
        """
        color = "red" if error_type == "ERROR" else "yellow" if error_type == "WARNING" else "blue"
        self.console.print(f"[{color}]⚠️ {error_type}: {message}[/{color}]")
        
    def show_phase(self, phase_name: str, status: str = "STARTING"):
        """
        Display current processing phase.
        
        Args:
            phase_name: Name of the phase
            status: Status of the phase
        """
        if status == "STARTING":
            self.console.print(f"\n[bold magenta]🔍 {phase_name}...[/bold magenta]")
        elif status == "COMPLETED":
            self.console.print(f"[green]✅ {phase_name} completed[/green]")
        else:
            self.console.print(f"[yellow]⏳ {phase_name}: {status}[/yellow]")
            
    def complete(self):
        """Complete all progress tracking and show final summary."""
        # Complete batch progress
        if self.batch_task is not None:
            self.progress.update(self.batch_task, completed=self.total_products)
            self.progress.stop()
            
        # Calculate final statistics
        total_time = time.time() - self.start_time
        avg_time = total_time / self.total_products if self.total_products > 0 else 0
        
        # Create summary table
        table = Table(title="🎯 Scraping Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Total Products", str(self.total_products))
        table.add_row("Total Vendors", str(self.total_vendors_processed))
        table.add_row("Average Vendors/Product", f"{self.total_vendors_processed/self.total_products:.1f}")
        table.add_row("Total Time", self._format_time(total_time))
        table.add_row("Average Time/Product", f"{avg_time:.1f}s")
        table.add_row("Mode", self.mode)
        
        # Display summary
        self.console.print("\n")
        self.console.print(Panel(table, expand=False))
        
    def _format_time(self, seconds: float) -> str:
        """
        Format seconds into human-readable time.
        
        Args:
            seconds: Number of seconds
            
        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class SpinnerStatus:
    """Simple spinner for operations without progress bars."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize spinner status."""
        self.console = console or Console()
        self.status = None
        
    def start(self, message: str):
        """Start spinner with message."""
        self.status = self.console.status(message)
        self.status.start()
        
    def update(self, message: str):
        """Update spinner message."""
        if self.status:
            self.status.update(message)
            
    def stop(self, final_message: Optional[str] = None):
        """Stop spinner."""
        if self.status:
            self.status.stop()
            if final_message:
                self.console.print(final_message)