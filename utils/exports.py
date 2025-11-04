import csv
from datetime import datetime
from pathlib import Path

def export_to_csv(data: list, columns: list, filename: str):
    """Export data to CSV file."""
    filepath = Path(filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(columns)
        
        # Write data
        for item in data:
            if isinstance(item, dict):
                row = [item.get(col, '') for col in columns]
            else:
                row = [getattr(item, col, '') for col in columns]
            writer.writerow(row)


def generate_report(data: dict, filename: str):
    """Generate a simple text report."""
    filepath = Path(filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        for section, content in data.items():
            f.write(f"{section}\n")
            f.write("-"*60 + "\n")
            if isinstance(content, dict):
                for key, value in content.items():
                    f.write(f"{key}: {value}\n")
            else:
                f.write(str(content))
            f.write("\n\n")