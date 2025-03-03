import sys
import time
import logging
import json
import csv
import argparse
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from rich.console import Console
from rich.logging import RichHandler

# Initialize console for rich text formatting
console = Console()

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(console=console, show_path=False)]
)

logger = logging.getLogger("logmate")

class LogMate:
    def __init__(self, config_file="logmate_config.json"):
        self.file_logging = None
        self.log_handler = None
        self.config = self.load_config(config_file)

    def info(self, message, **kwargs):
        log_message = self._format_log("INFO", message, kwargs)
        logger.info(log_message)

    def warning(self, message, **kwargs):
        log_message = self._format_log("WARNING", message, kwargs)
        logger.warning(log_message)

    def error(self, message, **kwargs):
        log_message = self._format_log("ERROR", message, kwargs)
        logger.error(log_message)

    def success(self, message, **kwargs):
        log_message = self._format_log("SUCCESS", message, kwargs)
        console.print(f"[bold green]✔ {message}[/]")

    def to_file(self, filename=None, max_size=5 * 1024 * 1024, backup_count=3):
        """Enable logging to a file with rotation."""
        filename = filename or self.config.get("log_file", "logmate.log")
        if self.file_logging == filename:
            return
        
        self.file_logging = filename
        for handler in logger.handlers[:]:
            if isinstance(handler, RotatingFileHandler):
                logger.removeHandler(handler)
                handler.close()

        self.log_handler = RotatingFileHandler(filename, maxBytes=max_size, backupCount=backup_count)
        logger.addHandler(self.log_handler)

    def extract_logs(self, filename, level=None, since_hours=None, keywords=None, export_file=None, export_csv=None):
        """Extract log data from a file with optional filters and export capability."""
        logs = []
        try:
            with open(filename, "r") as f:
                log_buffer = ""
                for line in f:
                    line = line.strip()
                    if line.startswith("{"):
                        log_buffer = line
                    elif line.endswith("}"):
                        log_buffer += " " + line
                        try:
                            log_entry = json.loads(log_buffer)
                            if level and log_entry.get("level") != level:
                                continue
                            if since_hours:
                                log_time = datetime.fromisoformat(log_entry["timestamp"])
                                if log_time < datetime.utcnow() - timedelta(hours=since_hours):
                                    continue
                            if keywords:
                                if not any(keyword.lower() in log_entry.get("message", "").lower() for keyword in keywords):
                                    continue
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            console.print(f"[bold red]Skipping malformed log entry: {log_buffer}[/]")
                    else:
                        log_buffer += " " + line
        except FileNotFoundError:
            console.print("[bold red]Log file not found![/]")

        if export_file:
            with open(export_file, "w") as f:
                json.dump(logs, f, indent=2)
            console.print(f"[bold green]Logs exported to {export_file} (JSON)[/]")

        if export_csv:
            with open(export_csv, "w", newline="") as f:
                fieldnames = set(["timestamp", "level", "message"])
                for log_entry in logs:
                    fieldnames.update(log_entry.keys())
                
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(logs)
            console.print(f"[bold green]Logs exported to {export_csv} (CSV)[/]")

        return logs

    def _format_log(self, level, message, kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry, indent=2)

    def timer(self, func):
        """Decorator to measure execution time of a function."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.info(f"Function `{func.__name__}` executed in {elapsed_time:.4f} seconds.")
            return result
        return wrapper

    def load_config(self, config_file):
        """Load configuration from a JSON file."""
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

# Create a global instance
log = LogMate()

# CLI Argument Parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LogMate - Smart Log Management Tool")
    parser.add_argument("--level", help="Filter logs by level (INFO, WARNING, ERROR)")
    parser.add_argument("--keywords", help="Comma-separated list of keywords to filter logs")
    parser.add_argument("--since_hours", type=int, help="Filter logs from the last N hours")
    parser.add_argument("--export_json", help="Export filtered logs to JSON file")
    parser.add_argument("--export_csv", help="Export filtered logs to CSV file")
    args = parser.parse_args()
    
    log.to_file()
    
    extracted_logs = log.extract_logs(
        "logmate.log",
        level=args.level,
        since_hours=args.since_hours,
        keywords=args.keywords.split(",") if args.keywords else None,
        export_file=args.export_json,
        export_csv=args.export_csv
    )
    
    console.print("\nExtracted Logs:")
    for entry in extracted_logs:
        console.print(entry)