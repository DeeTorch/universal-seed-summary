#!/usr/bin/env python3
"""
USS Format Converter
Version 1.3

Converts USS summaries between formats:
- Markdown (native format)
- JSON (structured data)
- YAML (human-readable structured)

MUSS Support:
- --upgrade: USS v1.3 -> MUSS v1.0
- --downgrade: MUSS v1.0 -> USS v1.3
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
from datetime import datetime


class USSConverter:
    """Convert USS summaries between formats"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def convert(self, input_path: Path, output_format: str) -> str:
        """Convert USS file to specified format"""
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        content = input_path.read_text(encoding="utf-8")
        input_format = self._detect_format(content, input_path)

        if self.verbose:
            print(f"Detected input format: {input_format}")

        # Parse input
        if input_format == "markdown":
            data = self._parse_markdown(content)
        elif input_format == "json":
            data = self._parse_json(content)
        elif input_format == "yaml":
            data = self._parse_yaml(content)
        else:
            raise ValueError(f"Unknown input format: {input_format}")

        # Convert to output format
        if output_format == "json":
            return self._to_json(data)
        elif output_format == "yaml":
            return self._to_yaml(data)
        elif output_format == "markdown":
            return self._to_markdown(data)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

    def _detect_format(self, content: str, file_path: Path) -> str:
        """Detect file format"""
        suffix = file_path.suffix.lower()

        if suffix == ".md":
            return "markdown"
        elif suffix == ".json":
            return "json"
        elif suffix in [".yml", ".yaml"]:
            return "yaml"

        # Try to detect from content
        if content.strip().startswith("{"):
            return "json"
        elif content.strip().startswith("---") and re.search(r'^### [A-Z]', content, re.MULTILINE):
            return "markdown"
        elif re.match(r'^\w+:\s*\S', content.strip(), re.MULTILINE):
            return "yaml"
        else:
            raise ValueError(f"Unable to detect format for {file_path}")

    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """Parse USS Markdown format"""
        data = {"format": "USS v1.3", "sections": {}}

        # Extract frontmatter
        frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            data["frontmatter"] = {}
            for line in frontmatter_match.group(1).split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    data["frontmatter"][key.strip()] = value.strip()

        # Extract sections
        section_pattern = r"### ([A-Z][A-Z\s&()]+)\n\n(.*?)(?=\n---|\n###|$)"
        sections = re.findall(section_pattern, content, re.DOTALL)

        for section_name, section_content in sections:
            section_name = section_name.strip()
            data["sections"][section_name] = self._parse_section(section_content)

        return data

    def _parse_section(self, content: str) -> Dict[str, Any]:
        """Parse individual section content"""
        section_data = {}

        # Extract fields with **Field_Name**: value format
        field_pattern = r"\*\*([^*]+)\*\*:\s*(.+?)(?=\n\*\*|\n\n|$)"
        # amazonq-ignore-next-line
        fields = re.findall(field_pattern, content, re.DOTALL)

        for field_name, field_value in fields:
            field_name = field_name.strip()
            field_value = field_value.strip()

            # Handle lists
            if field_value.startswith("- ") or "\n- " in field_value:
                # It's a list
                items = [item.strip() for item in re.split(r"\n?-\s*", field_value) if item.strip()]
                section_data[field_name] = items
            else:
                section_data[field_name] = field_value

        # If no fields found, store raw content
        if not section_data:
            section_data["_content"] = content.strip()

        return section_data

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON format"""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Parse YAML format (basic implementation)"""
        # Note: This is a simple YAML parser. For production use, consider PyYAML library
        data = {"sections": {}}
        current_section = None
        current_field = None
        indent_stack = []

        try:
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue

                indent = len(line) - len(line.lstrip())

                if ":" in line and not line.strip().startswith("-"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if not key:
                        raise ValueError(f"Empty key at line {line_num}")

                    if indent == 0:
                        # Top level key
                        if value:
                            data[key] = value
                        else:
                            data[key] = {}
                            current_section = key
                    elif current_section and current_section in data:
                        # Section content
                        if value:
                            data[current_section][key] = value
                        else:
                            data[current_section][key] = []
                            current_field = key
                elif line.strip().startswith("-") and current_field and current_section and current_section in data:
                    # List item
                    item = line.strip()[1:].strip()
                    if current_field in data[current_section] and isinstance(data[current_section][current_field], list):
                        data[current_section][current_field].append(item)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Malformed YAML structure: {e}")

        return data

    def _to_json(self, data: Dict[str, Any]) -> str:
        """Convert to JSON format"""
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _to_yaml(self, data: Dict[str, Any]) -> str:
        """Convert to YAML format"""
        lines = []

        # Frontmatter
        if "frontmatter" in data:
            for key, value in data["frontmatter"].items():
                lines.append(f"{key}: {value}")
            lines.append("")

        # Sections
        if "sections" in data:
            for section_name, section_data in data["sections"].items():
                lines.append(f"{section_name}:")

                if isinstance(section_data, dict):
                    for field_name, field_value in section_data.items():
                        if field_name == "_content":
                            # Raw content
                            lines.append(f"  content: |")
                            if isinstance(field_value, str):
                                for content_line in field_value.split("\n"):
                                    lines.append(f"    {content_line}")
                            else:
                                lines.append(f"    {str(field_value)}")
                        elif isinstance(field_value, list):
                            lines.append(f"  {field_name}:")
                            for item in field_value:
                                if item is None:
                                    lines.append(f"    - null")
                                else:
                                    lines.append(f"    - {item}")
                        else:
                            if field_value is None:
                                lines.append(f"  {field_name}: null")
                            else:
                                lines.append(f"  {field_name}: {field_value}")

                lines.append("")

        return "\n".join(lines)

    def _to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert to Markdown format"""
        lines = []

        # Frontmatter
        if "frontmatter" in data:
            lines.append("---")
            for key, value in data["frontmatter"].items():
                lines.append(f"{key}: {value}")
            lines.append("---")
            lines.append("")

        # Sections
        if "sections" in data:
            sections_items = list(data["sections"].items())
            for idx, (section_name, section_data) in enumerate(sections_items):
                lines.append(f"### {section_name}")
                lines.append("")

                if isinstance(section_data, dict):
                    fields_items = list(section_data.items())
                    for field_idx, (field_name, field_value) in enumerate(fields_items):
                        if field_name == "_content":
                            # Raw content
                            lines.append(field_value)
                        elif isinstance(field_value, list):
                            lines.append(f"**{field_name}**:")
                            for item in field_value:
                                lines.append(f"- {item}")
                        else:
                            lines.append(f"**{field_name}**: {field_value}")
                        
                        if field_idx < len(fields_items) - 1:
                            lines.append("")

                if idx < len(sections_items) - 1:
                    lines.append("---")
                    lines.append("")

        return "\n".join(lines)


# MUSS Conversion Functions
def upgrade_to_muss(filepath: str) -> None:
    """USS v1.3 artifact -> MUSS v1.0 artifact"""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Update protocol field
    content = re.sub(
        r'^protocol:.*$',
        'protocol: Memory-Augmented Universal Seed System',
        content,
        flags=re.MULTILINE
    )

    # 2. Add/rename version to protocol_version
    content = re.sub(
        r'^version:.*$',
        'protocol_version: "1.0"',
        content,
        flags=re.MULTILINE
    )

    # 3. Inject MUSS YAML fields after timestamp line
    muss_fields = f"session_id: MUSS_SESSION_{ts}\nexchange_count: 0\ndrift_risk: LOW\n"
    content = re.sub(
        r'(timestamp:.*)\n(---)',
        f'\\1\n{muss_fields}\\2',
        content
    )

    # 4. Inject LIVE MEMORY SNAPSHOT section after HEADER section
    live_memory = "\n### LIVE MEMORY SNAPSHOT\n\n"
    live_memory += "**SESSION_LOG_DIGEST**: No entries logged. (Scaffolded via USS->MUSS upgrade.)\n"
    live_memory += "**NOTEBOOK_STATE**: No notebook entries. (Scaffolded via USS->MUSS upgrade.)\n"
    live_memory += "**Active_Directives**: None.\n"
    live_memory += "**Commands_Issued**: None.\n"

    # Find HEADER section and insert after it
    content = re.sub(
        r'(### HEADER.*?(?=\n###|\n\n|\Z))',
        r'\1' + live_memory,
        content,
        flags=re.DOTALL
    )

    # 5. Update Resurrection_Hook prefix
    content = re.sub(r'> INGESTION:', '> MUSS INGESTION:', content)

    out_path = path.with_name(path.stem + "_muss_v1.0.md")
    out_path.write_text(content, encoding="utf-8")
    print(f"[CONVERTER] Upgraded: {filepath} -> {out_path}")


def downgrade_to_uss(filepath: str) -> None:
    """MUSS v1.0 artifact -> USS v1.3 artifact"""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    # 1. Update protocol field
    content = re.sub(
        r'^protocol:.*$',
        'protocol: Universal Seed Summary Invoker',
        content,
        flags=re.MULTILINE
    )

    # 2. Update version
    content = re.sub(
        r'^protocol_version:.*$',
        'version: "1.3"',
        content,
        flags=re.MULTILINE
    )

    # 3. Remove MUSS-only YAML fields
    for field in ["session_id", "exchange_count", "drift_risk"]:
        content = re.sub(rf'^{field}:.*\n', '', content, flags=re.MULTILINE)

    # 4. Remove LIVE MEMORY SNAPSHOT section
    content = re.sub(
        r'\n### LIVE MEMORY SNAPSHOT.*?(?=\n###|\Z)',
        '',
        content,
        flags=re.DOTALL
    )

    # 5. Revert Resurrection_Hook prefix
    content = re.sub(r'> MUSS INGESTION:', '> INGESTION:', content)

    out_path = path.with_name(path.stem + "_uss_v1.3.md")
    out_path.write_text(content, encoding="utf-8")
    print(f"[CONVERTER] Downgraded: {filepath} -> {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert USS summaries between formats (Markdown, JSON, YAML)"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input USS file"
    )
    parser.add_argument(
        "-t", "--to",
        choices=["json", "yaml", "markdown", "md"],
        required=True,
        help="Output format"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (default: input filename with new extension)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Normalize format
    output_format = "markdown" if args.to == "md" else args.to

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        format_extensions = {
            "json": ".json",
            "yaml": ".yaml",
            "markdown": ".md"
        }
        new_suffix = format_extensions.get(output_format, ".txt")
        output_path = args.input.with_suffix(new_suffix)

    # Convert
    try:
        converter = USSConverter(verbose=args.verbose)
        result = converter.convert(args.input, output_format)

        # Write output
        try:
            output_path.write_text(result, encoding="utf-8")
        except (PermissionError, OSError) as e:
            print(f"[ERROR] Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"[PASS] Converted: {args.input} -> {output_path}")
        print(f"   Format: {output_format}")
        print(f"   Size: {len(result)} characters")

    except FileNotFoundError as e:
        print(f"[ERROR] Error: Input file not found: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"[ERROR] Error: Permission denied reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"[ERROR] Error: Invalid file encoding: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Check for MUSS upgrade/downgrade mode first
    if len(sys.argv) >= 3 and sys.argv[1] in ("--upgrade", "--downgrade"):
        mode, filepath = sys.argv[1], sys.argv[2]
        if mode == "--upgrade":
            upgrade_to_muss(filepath)
        elif mode == "--downgrade":
            downgrade_to_uss(filepath)
        else:
            print(f"Unknown mode: {mode}")
            sys.exit(1)
    else:
        main()
