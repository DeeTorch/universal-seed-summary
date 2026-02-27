#!/usr/bin/env python3
"""
converter.py — MUSS/USS Bidirectional Converter (v1.0 MUSS patch)
Adds MUSS <-> USS upgrade/downgrade modes to the existing converter.
Usage:
  python converter.py --upgrade <uss_artifact.md>    # USS v1.3 → MUSS v1.0
  python converter.py --downgrade <muss_artifact.md> # MUSS v1.0 → USS v1.3
"""

import re
import sys
from pathlib import Path
from datetime import datetime

LIVE_MEMORY_SCAFFOLD = """
### LIVE MEMORY SNAPSHOT

**SESSION_LOG_DIGEST**: No entries logged. (Scaffolded via USS→MUSS upgrade.)
**NOTEBOOK_STATE**: No notebook entries. (Scaffolded via USS→MUSS upgrade.)
**Active_Directives**: None.
**Commands_Issued**: None.
"""

MUSS_YAML_ADDITIONS = """session_id: MUSS_SESSION_UPGRADED_{ts}
exchange_count: 0
drift_risk: LOW
"""

def upgrade_to_muss(filepath: str) -> None:
    """USS v1.3 artifact → MUSS v1.0 artifact"""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Update protocol field
    content = re.sub(
        r'protocol:\s*"?Universal Seed Summary Invoker"?',
        'protocol: "Memory-Augmented Universal Seed System"',
        content
    )
    # 2. Update version
    content = re.sub(r'protocol_version:\s*["']?1\.3.*?["']?', 'protocol_version: "1.0"', content)
    # 3. Inject MUSS YAML fields after timestamp line
    content = re.sub(
        r'(timestamp:.*?)\n---',
        f'\\1\n{MUSS_YAML_ADDITIONS.strip()}\n---',
        content
    )
    # 4. Inject LIVE MEMORY SNAPSHOT section after HEADER section
    content = re.sub(
        r'(### HEADER.*?)(### FAILURE)',
        f'\\1{LIVE_MEMORY_SCAFFOLD}\\2',
        content,
        flags=re.DOTALL
    )
    # 5. Update Resurrection_Hook prefix
    content = re.sub(r'> INGESTION:', '> MUSS INGESTION:', content)

    out_path = path.with_name(path.stem + "_muss_v1.0.md")
    out_path.write_text(content, encoding="utf-8")
    print(f"[CONVERTER] Upgraded: {filepath} → {out_path}")


def downgrade_to_uss(filepath: str) -> None:
    """MUSS v1.0 artifact → USS v1.3 artifact"""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    # 1. Update protocol field
    content = re.sub(
        r'protocol:\s*"?Memory-Augmented Universal Seed System"?',
        'protocol: "Universal Seed Summary Invoker"',
        content
    )
    # 2. Update version
    content = re.sub(r'protocol_version:\s*["']?1\.0["']?', 'protocol_version: "1.3"', content)
    # 3. Remove MUSS-only YAML fields
    for field in ["session_id", "exchange_count", "drift_risk"]:
        content = re.sub(rf'^{field}:.*\n', '', content, flags=re.MULTILINE)
    # 4. Remove LIVE MEMORY SNAPSHOT section
    content = re.sub(
        r'### LIVE MEMORY SNAPSHOT.*?(?=###)',
        '',
        content,
        flags=re.DOTALL
    )
    # 5. Revert Resurrection_Hook prefix
    content = re.sub(r'> MUSS INGESTION:', '> INGESTION:', content)

    out_path = path.with_name(path.stem + "_uss_v1.3.md")
    out_path.write_text(content, encoding="utf-8")
    print(f"[CONVERTER] Downgraded: {filepath} → {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python converter.py --upgrade <file.md>")
        print("       python converter.py --downgrade <file.md>")
        sys.exit(1)
    mode, filepath = sys.argv[1], sys.argv[2]
    if mode == "--upgrade":
        upgrade_to_muss(filepath)
    elif mode == "--downgrade":
        downgrade_to_uss(filepath)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
