#!/usr/bin/env python3
"""
Google Drive Public Directory Indexer
Recursively indexes files and subdirectories from a public Google Drive folder.
"""

import argparse
import csv
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


def extract_folder_id(url_or_id: str) -> str:
    """Extract Google Drive folder ID from various URL patterns or raw ID."""
    url_or_id = url_or_id.strip()
    match = re.search(r'folders/([a-zA-Z0-9_-]+)', url_or_id)
    if match:
        return match.group(1)
    match = re.search(r'id=([a-zA-Z0-9_-]+)', url_or_id)
    if match:
        return match.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{10,}$', url_or_id):
        return url_or_id
    raise ValueError(f"Could not extract a valid Google Drive folder ID from: {url_or_id}")


def format_size(size_bytes: Optional[int]) -> str:
    """Format bytes into human-readable size string."""
    if size_bytes is None:
        return "N/A"
    try:
        size = float(size_bytes)
    except (ValueError, TypeError):
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0 or unit == 'TB':
            return f"{size:.2f} {unit}" if unit != 'B' else f"{int(size)} B"
        size /= 1024.0
    return f"{size:.2f} TB"


class DriveApiIndexer:
    """Indexes Google Drive public folders using the Google Drive API v3 and an API Key."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/drive/v3/files"

    def fetch_items_in_parent(self, parent_id: str) -> List[Dict[str, Any]]:
        """Fetch all non-trashed children belonging to a specific parent folder."""
        items = []
        page_token = None

        while True:
            params = {
                'q': f"'{parent_id}' in parents and trashed = false",
                'key': self.api_key,
                'fields': 'nextPageToken, files(id, name, mimeType, size, modifiedTime, md5Checksum)',
                'pageSize': 1000,
                'supportsAllDrives': 'true',
                'includeItemsFromAllDrives': 'true',
            }
            if page_token:
                params['pageToken'] = page_token

            query_string = urllib.parse.urlencode(params)
            req_url = f"{self.base_url}?{query_string}"

            req = urllib.request.Request(req_url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    items.extend(data.get('files', []))
                    page_token = data.get('nextPageToken')
                    if not page_token:
                        break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8', errors='replace')
                print(f"[Error] HTTP {e.code} querying parent {parent_id}: {err_body}", file=sys.stderr)
                break
            except Exception as e:
                print(f"[Error] Failed to fetch items for {parent_id}: {e}", file=sys.stderr)
                break

        return items

    def index_recursive(self, folder_id: str, current_path: str = "") -> List[Dict[str, Any]]:
        """Recursively traverses folders and builds a flat list of indexed entries with full paths."""
        results = []
        items = self.fetch_items_in_parent(folder_id)

        for item in items:
            item_name = item.get('name', 'unnamed')
            item_id = item.get('id', '')
            mime_type = item.get('mimeType', '')
            is_folder = mime_type == 'application/vnd.google-apps.folder'
            rel_path = os.path.join(current_path, item_name) if current_path else item_name

            raw_size = item.get('size')
            size_int = int(raw_size) if raw_size is not None else None

            entry = {
                'id': item_id,
                'name': item_name,
                'path': rel_path,
                'is_directory': is_folder,
                'mime_type': mime_type,
                'size_bytes': size_int,
                'size_formatted': format_size(size_int),
                'modified_time': item.get('modifiedTime'),
                'md5_checksum': item.get('md5Checksum'),
                'direct_download_url': f"https://drive.google.com/uc?id={item_id}&export=download" if not is_folder else None
            }
            results.append(entry)

            if is_folder:
                print(f"  [Scanning Folder] {rel_path}/ ...", file=sys.stderr)
                sub_results = self.index_recursive(item_id, rel_path)
                results.extend(sub_results)
            else:
                print(f"  [Found File] {rel_path} ({entry['size_formatted']})", file=sys.stderr)

        return results


def export_json(results: List[Dict[str, Any]], output_path: str):
    """Export index as JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[Done] Exported {len(results)} items to JSON: {output_path}")


def export_csv(results: List[Dict[str, Any]], output_path: str):
    """Export index as CSV."""
    if not results:
        print("[Warning] No items to export to CSV.", file=sys.stderr)
        return
    fieldnames = ['path', 'name', 'is_directory', 'size_bytes', 'size_formatted', 'mime_type', 'id', 'modified_time', 'md5_checksum', 'direct_download_url']
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in results:
            writer.writerow(item)
    print(f"[Done] Exported {len(results)} items to CSV: {output_path}")


def export_txt(results: List[Dict[str, Any]], output_path: str, files_only: bool = False):
    """Export index as a plain text list of paths."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in results:
            if files_only and item.get('is_directory'):
                continue
            suffix = "/" if item.get('is_directory') else ""
            f.write(f"{item['path']}{suffix}\n")
    print(f"[Done] Exported path list to TXT: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Recursively index a public Google Drive directory.")
    parser.add_argument("url_or_id", help="Google Drive public folder URL or folder ID")
    parser.add_argument("--api-key", "-k", default=os.environ.get("GDRIVE_API_KEY"), help="Google Drive API v3 Key (or set GDRIVE_API_KEY env var)")
    parser.add_argument("--output", "-o", default="gdrive_index.json", help="Output file path (default: gdrive_index.json)")
    parser.add_argument("--format", "-f", choices=["json", "csv", "txt"], default="json", help="Output format (json, csv, txt)")
    parser.add_argument("--files-only", action="store_true", help="Exclude directories from txt export")

    args = parser.parse_args()

    try:
        folder_id = extract_folder_id(args.url_or_id)
    except ValueError as e:
        print(f"[Error] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Target Folder ID: {folder_id}")

    if not args.api_key:
        print("\n[Notice] No Google Drive API key provided.", file=sys.stderr)
        print("To index public Google Drive folders efficiently and recursively, a Google Drive API Key is required.", file=sys.stderr)
        print("You can get a free API Key from Google Cloud Console (APIs & Services -> Credentials -> Create API Key).", file=sys.stderr)
        print("Pass it via `--api-key YOUR_KEY` or set `export GDRIVE_API_KEY=YOUR_KEY`.\n", file=sys.stderr)
        sys.exit(1)

    indexer = DriveApiIndexer(api_key=args.api_key)
    print(f"Starting recursive scan for folder {folder_id}...")
    results = indexer.index_recursive(folder_id)
    print(f"\nScan complete! Found {len(results)} total items.")

    out_format = args.format.lower()
    if out_format == "json" or args.output.endswith(".json"):
        export_json(results, args.output)
    elif out_format == "csv" or args.output.endswith(".csv"):
        export_csv(results, args.output)
    elif out_format == "txt" or args.output.endswith(".txt"):
        export_txt(results, args.output, files_only=args.files_only)
    else:
        export_json(results, args.output)


if __name__ == "__main__":
    main()
