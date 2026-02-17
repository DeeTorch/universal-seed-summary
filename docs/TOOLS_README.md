# USS Tools Documentation

The USS repository includes three utility tools for working with summaries:

## 1. validator.py - Protocol Compliance Checker

**Purpose**: Validates USS summary files for protocol compliance.

### Features
- Checks all required sections are present
- Validates HEADER and FAILURE SEMANTICS fields
- Verifies formatting standards (###, **, -, ---)
- Checks token budgets per mode
- Detects vague failure semantics language
- Validates INVOCATION LOCK completeness

### Usage

```bash
# Basic validation
python tools/validator.py examples/checkpoint/checkpoint_example.md

# Verbose output with details
python tools/validator.py examples/checkpoint/checkpoint_example.md -v

# Strict mode (treat warnings as errors)
python tools/validator.py my-summary.md --strict
```

### Exit Codes
- `0` - Validation passed
- `1` - Validation failed (errors or warnings in strict mode)

---

## 2. indexer.py - Summary Archive Indexer

**Purpose**: Builds searchable index of USS summary archives.

### Features
- Scans directories for USS summaries
- Extracts metadata (mode, archetype, project, domains)
- Creates JSON index for fast lookup
- Search by project, mode, archetype, or keywords
- Statistics reporting (modes, archetypes, projects)

### Usage

```bash
# Index current directory
python tools/indexer.py

# Index specific directory
python tools/indexer.py ./summaries/

# Specify output file
python tools/indexer.py ./summaries/ -o my-index.json

# Non-recursive (don't scan subdirectories)
python tools/indexer.py ./summaries/ --no-recursive

# Verbose progress
python tools/indexer.py ./summaries/ -v

# Search after indexing
python tools/indexer.py ./summaries/ --search "Erosforge"
python tools/indexer.py ./summaries/ --mode checkpoint
python tools/indexer.py ./summaries/ --archetype "Development_Forge"
python tools/indexer.py ./summaries/ --project "UVB"

# Combined filters
python tools/indexer.py ./summaries/ --mode archive --project "Erosforge"
```

### Output Format

Creates `uss-index.json` with structure:
```json
{
  "generated": "2026-02-07T08:00:00",
  "stats": {
    "total_files": 15,
    "indexed": 12,
    "errors": 0,
    "modes": {"checkpoint": 8, "archive": 4},
    "archetypes": {"Development_Forge": 5, "Inquiry_Audit": 3},
    "projects": ["Erosforge", "UVB", "Research"]
  },
  "summaries": [
    {
      "filename": "Erosforge_Development_Forge_20260206_checkpoint.md",
      "filepath": "/path/to/file.md",
      "mode": "checkpoint",
      "thread_archetype": "Development_Forge",
      "project": "Erosforge",
      "thread_depth": 12,
      "completion_state": "Development (40%)",
      "focus_domains": "AI_Architecture + Full_Stack_Development",
      "ignition_vector": "User initiated design session for...",
      "word_count": 954
    }
  ]
}
```

---

## 3. converter.py - Format Converter

**Purpose**: Converts USS summaries between Markdown, JSON, and YAML formats.

### Features
- Auto-detects input format
- Converts to JSON, YAML, or Markdown
- Preserves structure and metadata
- Handles frontmatter, sections, and fields

### Usage

```bash
# Convert Markdown to JSON
python tools/converter.py my-summary.md --to json

# Convert Markdown to YAML
python tools/converter.py my-summary.md --to yaml

# Convert JSON back to Markdown
python tools/converter.py my-summary.json --to markdown

# Specify output file
python tools/converter.py my-summary.md --to json -o output.json

# Verbose output
python tools/converter.py my-summary.md --to json -v
```

### Supported Formats

**Input**: `.md` (Markdown), `.json` (JSON), `.yml/.yaml` (YAML)  
**Output**: `json`, `yaml`, `markdown` (or `md`)

### Use Cases

- **JSON**: For programmatic processing, APIs, databases
- **YAML**: For human-readable configuration, version control
- **Markdown**: Native USS format, human-readable documentation

---

## Common Workflows

### Workflow 1: Create, Validate, Index

```bash
# 1. Create USS summary (manually invoke in LLM)
# 2. Save as: Erosforge_Development_Forge_20260207_checkpoint.md

# 3. Validate
python tools/validator.py Erosforge_Development_Forge_20260207_checkpoint.md

# 4. Move to archive
mv Erosforge_Development_Forge_20260207_checkpoint.md summaries/erosforge/

# 5. Re-index
python tools/indexer.py ./summaries/
```

### Workflow 2: Search and Convert

```bash
# Search for all UVB summaries
python tools/indexer.py ./summaries/ --project UVB

# Convert specific summary to JSON for processing
python tools/converter.py summaries/uvb/UVB_Conceptual_Synthesis_20260203_checkpoint.md --to json

# Process JSON with other tools (jq, Python scripts, etc.)
```

### Workflow 3: Batch Validation

```bash
# Validate all summaries in directory
for file in summaries/**/*.md; do
  echo "Validating $file..."
  python tools/validator.py "$file" || echo "FAILED: $file"
done
```

---

## Installation

All tools require **Python 3.9+** with standard library only (no external dependencies for basic functionality).

### Optional Dependencies

For enhanced functionality, install:

```bash
pip install -r requirements.txt
```

Current optional dependencies:
- `pyyaml>=6.0` - Better YAML parsing in converter.py
- `pandas>=2.0.0` - Data analysis in indexer.py (future)
- `click>=8.0.0` - Enhanced CLI (future)

---

## Integration Examples

### Python Script Integration

```python
from pathlib import Path
import json

# Use indexer programmatically
from tools.indexer import USSIndexer

indexer = USSIndexer(verbose=False)
indexer.scan_directory(Path("./summaries/"))
results = indexer.search(project="Erosforge", mode="checkpoint")

for result in results:
    print(f"{result['filename']} - {result['completion_state']}")

indexer.export_index(Path("my-index.json"))
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Validate USS Summaries

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Validate summaries
        run: |
          for file in summaries/**/*.md; do
            python tools/validator.py "$file" --strict
          done
```

---

## Troubleshooting

### validator.py

**Issue**: "Missing required section"  
**Fix**: Ensure all 6 required sections present with exact header format

**Issue**: "Token count exceeds target"  
**Fix**: Compress summary or use different mode (checkpoint → archive for more space)

### indexer.py

**Issue**: "No files indexed"  
**Fix**: Ensure files have valid YAML frontmatter with `mode:` field

**Issue**: Search returns nothing  
**Fix**: Check search terms match metadata fields (case-insensitive)

### converter.py

**Issue**: "Cannot parse YAML"  
**Fix**: Install PyYAML (`pip install pyyaml`) for better YAML support

**Issue**: "Lost formatting in conversion"  
**Fix**: Markdown → JSON → Markdown may lose some formatting nuances

---

## Future Enhancements

Planned features for future releases:

- **validator.py**: 
  - Auto-fix mode for common issues
  - JSON Schema validation
  - Custom rule definitions

- **indexer.py**:
  - Vector embeddings for semantic search
  - Web UI for browsing index
  - Relationship graph visualization

- **converter.py**:
  - XML format support
  - Batch conversion mode
  - Template-based customization

---

## Contributing

Contributions to tools are welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

Tool improvements should:
- Maintain backward compatibility
- Include --help documentation
- Handle errors gracefully
- Follow Python best practices

---

**Tool Versions**: 1.3  
**Last Updated**: February 7, 2025  
**Compatibility**: USS Protocol v1.3
