import os
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def save_json_report(report_data: dict) -> str:
    """Saves the JSON report to the evaluation/results directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation/results/report_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(report_data, f, indent=4)
        
    return filename

import re

def inject_dashboard(report_data: dict, template_path: str = "dashboard/index.html"):
    """Injects the JSON report data into the HTML dashboard."""
    if not os.path.exists(template_path):
        print(f"[!] Dashboard template not found at {template_path}")
        return
        
    with open(template_path, "r") as f:
        html = f.read()
        
    # Use regex to find and replace the reportData variable, in case it was already replaced.
    json_str = json.dumps(report_data)
    
    # This matches 'const reportData = null; // __INJECT_JSON_HERE__' or 'const reportData = {...};'
    pattern = r'const reportData = .*?;(?: // __INJECT_JSON_HERE__)?'
    replacement = f'const reportData = {json_str};'
    
    injected_html = re.sub(pattern, lambda m: replacement, html, count=1)
    
    with open(template_path, "w") as f:
        f.write(injected_html)

def generate_terminal_report(report_data: dict):
    """Uses Rich to print a beautiful terminal report."""
    
    agent = report_data["agent"]
    total = report_data["summary"]["total_tests"]
    passed = report_data["summary"]["passed"]
    failed = report_data["summary"]["failed"]
    
    scores = report_data["scores"]
    cost = report_data["cost"]
    
    def get_color_and_icon(score):
        if score >= 80: return "green", "✓"
        if score >= 50: return "yellow", "⚠"
        return "red", "✗"

    # Print Header
    header = f"[bold white]Agent:[/bold white]   {agent}\n[bold white]Tests:[/bold white]   {total} total | [green]{passed} passed[/green] | [red]{failed} failed[/red]"
    console.print(Panel(header, title="[bold cyan]AI AGENT TESTING FRAMEWORK v1.0[/bold cyan]", expand=False))
    
    # SCORES
    score_table = Table(show_header=False, box=None)
    
    for name, key in [("Safety Score", "safety"), ("Accuracy Score", "accuracy"), ("Robustness", "robustness"), ("Overall Score", "overall")]:
        s = scores[key]
        color, icon = get_color_and_icon(s)
        bar = "█" * int(s / 10) + "░" * (10 - int(s / 10))
        score_table.add_row(name, f"[{color}]{bar}[/{color}]", f"[{color}]{s}%[/{color}]", f"[{color}]{icon}[/{color}]")
        
    console.print(Panel(score_table, title="[bold]SCORES[/bold]", expand=False))
    
    # COST TRACKING
    cost_text = f"Total Cost: ${cost['total_cost']:.6f}\nAvg per query: ${cost['mean_cost_per_query']:.6f}"
    console.print(Panel(cost_text, title="[bold]COST TRACKING[/bold]", expand=False))
    
    # FAILURES
    if failed > 0:
        fail_table = Table(show_header=False, box=None)
        for res in report_data["results"]:
            if not res["passed"]:
                # Grab a brief reason if available from LLM judge
                reason = res["eval_metrics"].get("llm_judge", {}).get("reasoning", "Failed evaluation")
                # Truncate reason
                if len(reason) > 50:
                    reason = reason[:47] + "..."
                fail_table.add_row(f"[red]✗[/red]", res["id"], f"[dim]{reason}[/dim]")
        console.print(Panel(fail_table, title="[bold red]FAILURES[/bold red]", expand=False))
    else:
        console.print(Panel("[green]All tests passed! No failures.[/green]", title="[bold green]FAILURES[/bold green]", expand=False))
