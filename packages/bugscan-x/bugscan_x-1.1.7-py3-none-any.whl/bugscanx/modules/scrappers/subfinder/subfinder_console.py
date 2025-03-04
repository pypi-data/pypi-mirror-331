from threading import RLock
from rich import print

class Logger:
    def __init__(self):
        self._lock = RLock()

    def clear_line(self):
        with self._lock:
            print("\033[2K\r", end='', flush=True)

    def replace(self, message):
        with self._lock:
            print(f"{message}", end='', flush=True)

class SubFinderConsole:
    def __init__(self):
        self.total_subdomains = 0
        self.domain_stats = {}
        self.logger = Logger()
    
    def start_domain_scan(self, domain):
        self.logger.clear_line()
        print(f"[cyan]→[/cyan] Scanning {domain}...")
    
    def update_domain_stats(self, domain, count):
        self.domain_stats[domain] = count
        self.total_subdomains += count
    
    def print_domain_complete(self, domain, subdomains_count):
        self.logger.clear_line()
        print(f"[green]✓[/green] {domain}: {subdomains_count} subdomains found")
    
    def print_final_summary(self, output_file):
        print(f"\n[green]✓[/green] Total: [bold]{self.total_subdomains}[/bold] subdomains found")
        print(f"[green]✓[/green] Results saved to {output_file}")
        
    def print_error(self, message):
        print(f"[bold red]✗ ERROR: {message}[/bold red]")

    def show_progress(self, current, total):
        progress_message = f"Progress: [{current}/{total}]\r"
        self.logger.replace(progress_message)
