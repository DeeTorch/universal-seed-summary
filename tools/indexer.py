#!/usr/bin/env python3
"""
USS Summary Indexer
Version 1.3

Builds a searchable index of USS summary archives.
Enables fast lookup by project, date, mode, archetype, or content.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional
import argparse


class USSIndexer:
    """Index USS summary files for searching and organization"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.index = []
        self.stats = {
            "total_files": 0,
            "indexed": 0,
            "errors": 0,
            "modes": {},
            "archetypes": {},
            "projects": set()
        }

    def scan_directory(self, directory: Path, recursive: bool = True) -> None:
        """Scan directory for USS summary files"""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        pattern = "**/*.md" if recursive else "*.md"
        md_files = list(directory.glob(pattern))

        self.stats["total_files"] = len(md_files)

        if self.verbose:
            print(f"Found {len(md_files)} markdown files")

        for file_path in md_files:
            try:
                self._index_file(file_path)
                self.stats["indexed"] += 1
            except (UnicodeDecodeError, OSError, ValueError) as e:
                self.stats["errors"] += 1
                print(f"Error indexing {file_path}: {e}", file=sys.stderr)

    def _index_file(self, file_path: Path) -> None:
        """Extract metadata from a single USS file"""
        content = file_path.read_text(encoding="utf-8")

        # Check if it's a USS file (has frontmatter with mode)
        if not content.startswith("---"):
            return

        metadata = self._extract_metadata(content, file_path)
        if metadata:
            self.index.append(metadata)

            # Update stats
            mode = metadata.get("mode", "unknown")
            archetype = metadata.get("thread_archetype", "unknown")
            project = metadata.get("project", "unknown")

            self.stats["modes"][mode] = self.stats["modes"].get(mode, 0) + 1
            self.stats["archetypes"][archetype] = self.stats["archetypes"].get(archetype, 0) + 1
            if project != "unknown":
                self.stats["projects"].add(project)

    def _extract_metadata(self, content: str, file_path: Path) -> Optional[Dict]:
        """Extract metadata from USS summary"""
        metadata = {
            "filename": file_path.name,
            "filepath": str(file_path.absolute()),
            "relative_path": str(file_path),
            "size_bytes": len(content.encode('utf-8')),
            "word_count": len(content.split())
        }

        # Extract frontmatter
        frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # Parse frontmatter fields
            for line in frontmatter.split("\n"):
                # amazonq-ignore-next-line
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

        # Extract header fields
        header_match = re.search(
            r"### HEADER \(THREAD LOCK & AUDIT\)(.*?)(?=###|$)",
            content,
            re.DOTALL
        )

        if header_match:
            header_content = header_match.group(1)

            # Thread_Archetype
            archetype_match = re.search(r"\*\*Thread_Archetype\*\*:\s*(.+)", header_content)
            if archetype_match:
                metadata["thread_archetype"] = archetype_match.group(1).strip()

            # Ignition_Vector
            ignition_match = re.search(r"\*\*Ignition_Vector\*\*:\s*(.+?)(?=\n\*\*|$)", header_content, re.DOTALL)
            if ignition_match:
                metadata["ignition_vector"] = ignition_match.group(1).strip()[:200]  # First 200 chars

            # Focus_Domains
            domains_match = re.search(r"\*\*Focus_Domains\*\*:\s*(.+)", header_content)
            if domains_match:
                metadata["focus_domains"] = domains_match.group(1).strip()

            # Thread_Depth
            depth_match = re.search(r"\*\*Thread_Depth\*\*:\s*(\d+)", header_content)
            if depth_match:
                metadata["thread_depth"] = int(depth_match.group(1))

            # Completion_State
            completion_match = re.search(r"\*\*Completion_State\*\*:\s*(.+)", header_content)
            if completion_match:
                metadata["completion_state"] = completion_match.group(1).strip()

            # Momentum_Indicator
            momentum_match = re.search(r"\*\*Momentum_Indicator\*\*:\s*(.+)", header_content)
            if momentum_match:
                metadata["momentum_indicator"] = momentum_match.group(1).strip()

        # Extract project from filename or frontmatter
        if "project" not in metadata:
            # Try to extract from filename pattern: {project}_{archetype}_{date}_{mode}.md
            name_parts = file_path.stem.split("_")
            if len(name_parts) >= 2:
                metadata["project"] = name_parts[0]

        # Only return if we found at least mode (valid USS file)
        if "mode" in metadata:
            return metadata
        return None

    def search(self, query: str = None, mode: str = None, 
               archetype: str = None, project: str = None) -> List[Dict]:
        """Search indexed summaries"""
        query_lower = query.lower() if query else None
        
        results = [
            r for r in self.index
            if (not mode or r.get("mode") == mode)
            and (not archetype or archetype.lower() in r.get("thread_archetype", "").lower())
            and (not project or project.lower() in r.get("project", "").lower())
            and (not query_lower or 
                 query_lower in r.get("ignition_vector", "").lower() or
                 query_lower in r.get("focus_domains", "").lower() or
                 query_lower in r.get("filename", "").lower())
        ]

        return results

    def export_index(self, output_path: Path) -> None:
        """Export index to JSON file"""
        index_data = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "total_files": self.stats["total_files"],
                "indexed": self.stats["indexed"],
                "errors": self.stats["errors"],
                "modes": self.stats["modes"],
                "archetypes": self.stats["archetypes"],
                "projects": list(self.stats["projects"])
            },
            "summaries": self.index
        }

        output_path.write_text(
            json.dumps(index_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        if self.verbose:
            print(f"Index exported to: {output_path}")

    def print_stats(self) -> None:
        """Print indexing statistics"""
        print("\nIndexing Statistics")
        print("=" * 60)
        print(f"Total files scanned: {self.stats['total_files']}")
        print(f"Successfully indexed: {self.stats['indexed']}")
        print(f"Errors: {self.stats['errors']}")

        if self.stats["modes"]:
            print("\nModes:")
            for mode, count in sorted(self.stats["modes"].items()):
                print(f"  {mode}: {count}")

        if self.stats["archetypes"]:
            print("\nArchetypes:")
            for archetype, count in sorted(self.stats["archetypes"].items(), key=lambda x: x[1], reverse=True):
                print(f"  {archetype}: {count}")

        if self.stats["projects"]:
            print(f"\nProjects: {len(self.stats['projects'])}")
            for project in sorted(self.stats["projects"]):
                print(f"  - {project}")


def main():
    parser = argparse.ArgumentParser(
        description="Index USS summary files for search and organization"
    )
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Directory to scan for USS summaries (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("uss-index.json"),
        help="Output index file (default: uss-index.json)"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't scan subdirectories"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Search indexed summaries"
    )
    parser.add_argument(
        "--mode",
        choices=["checkpoint", "re_entry", "archive"],
        help="Filter by mode"
    )
    parser.add_argument(
        "--archetype",
        type=str,
        help="Filter by thread archetype"
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Filter by project name"
    )

    args = parser.parse_args()

    indexer = USSIndexer(verbose=args.verbose)

    print(f"Scanning: {args.directory}")
    try:
        indexer.scan_directory(args.directory, recursive=not args.no_recursive)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Export index
    try:
        indexer.export_index(args.output)
    except (PermissionError, OSError) as e:
        print(f"Error exporting index: {e}", file=sys.stderr)
        sys.exit(1)

    # Print stats
    indexer.print_stats()

    # Perform search if requested
    if args.search or args.mode or args.archetype or args.project:
        print("\n" + "=" * 60)
        print("Search Results")
        print("=" * 60)

        results = indexer.search(
            query=args.search,
            mode=args.mode,
            archetype=args.archetype,
            project=args.project
        )

        if not results:
            print("No matches found.")
        else:
            print(f"Found {len(results)} matches:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['filename']}")
                print(f"   Mode: {result.get('mode', 'unknown')}")
                print(f"   Archetype: {result.get('thread_archetype', 'unknown')}")
                print(f"   Project: {result.get('project', 'unknown')}")
                if 'ignition_vector' in result:
                    print(f"   Summary: {result['ignition_vector'][:100]}...")
                print()

    print(f"\n[PASS] Index saved to: {args.output}")


if __name__ == "__main__":
    main()