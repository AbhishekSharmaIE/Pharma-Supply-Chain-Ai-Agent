"""
In production, this Python script is replaced by a Power Automate flow with an
HTTP connector. The flow triggers on SharePoint/OneDrive file uploads, posts to
the FastAPI endpoint, and routes human-review orders to a Teams adaptive card
approval workflow.
"""

import argparse
import json
import shutil
import time
from collections import Counter
from pathlib import Path

import requests
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

API_URL = "http://localhost:8000/orders/upload-csv"


class CsvHandler(FileSystemEventHandler):
    def __init__(self, watch_folder: Path, processed_folder: Path) -> None:
        self.watch_folder = watch_folder
        self.processed_folder = processed_folder

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if file_path.suffix.lower() != ".csv":
            return
        self.process_file(file_path)

    def process_file(self, file_path: Path) -> None:
        print(f"🔄 New file detected: {file_path.name}")
        try:
            with file_path.open("rb") as file_obj:
                response = requests.post(API_URL, files={"file": (file_path.name, file_obj, "text/csv")}, timeout=120)
            response.raise_for_status()
            payload = response.json()
            print_summary(payload)
        except requests.RequestException as exc:
            print(f"❌ Failed to process {file_path.name}: {exc}")
            return
        except json.JSONDecodeError:
            print(f"❌ API returned non-JSON response for {file_path.name}")
            return

        destination = self.processed_folder / file_path.name
        shutil.move(str(file_path), str(destination))
        print(f"✅ Moved to: {destination}")


def print_summary(payload: dict) -> None:
    decisions = payload.get("decisions", [])
    counts = Counter(item.get("priority_level", "UNKNOWN") for item in decisions)
    review_orders = [item.get("order_id") for item in decisions if item.get("requires_human_review")]

    print("Batch Response Summary")
    print(f"- Batch ID: {payload.get('batch_id')}")
    print(f"- Total orders processed: {payload.get('total_orders')}")
    print(
        "- Priority breakdown: "
        f"CRITICAL={counts.get('CRITICAL', 0)}, "
        f"HIGH={counts.get('HIGH', 0)}, "
        f"MEDIUM={counts.get('MEDIUM', 0)}, "
        f"LOW={counts.get('LOW', 0)}"
    )
    print(f"- Orders requiring human review: {review_orders or 'None'}")


def run_watcher(watch_folder: Path, processed_folder: Path) -> None:
    watch_folder.mkdir(parents=True, exist_ok=True)
    processed_folder.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(CsvHandler(watch_folder, processed_folder), str(watch_folder), recursive=False)
    observer.start()
    print(f"👀 Watching folder: {watch_folder}")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping watcher...")
    finally:
        observer.stop()
        observer.join()


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate Power Automate batch trigger.")
    parser.add_argument("--demo", action="store_true", help="Copy sample CSV into watch folder.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    watch_folder = script_dir / "watch_folder"
    processed_folder = watch_folder / "processed"

    if args.demo:
        source = script_dir.parent / "backend" / "data" / "sample_orders.csv"
        watch_folder.mkdir(parents=True, exist_ok=True)
        demo_target = watch_folder / f"demo_{int(time.time())}.csv"
        shutil.copy2(source, demo_target)
        print(f"📦 Demo file copied to: {demo_target}")

    run_watcher(watch_folder, processed_folder)


if __name__ == "__main__":
    main()
