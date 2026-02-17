# Contributing to Universal Seed Summary Invoker

Thank you for your interest in improving USS! This protocol benefits from diverse perspectives and real-world testing across different use cases.

## How to Contribute

### 1. Reporting Issues

**Before submitting an issue**, please check:
- [ ] Is this a protocol compliance issue? (Use validator.py to check)
- [ ] Has this already been reported? (Search existing issues)
- [ ] Do you have a reproducible example?

**When reporting issues, include**:
- Protocol version (v1.3, etc.)
- LLM platform used (Claude, GPT-4, Grok, Perplexity, etc.)
- Invocation mode (checkpoint, re-entry, archive)
- Expected vs actual output (if applicable)
- Thread characteristics (depth, complexity, domain)

**Issue Types**:
- 🐛 **Bug**: Protocol specification ambiguity, validation errors
- 📚 **Documentation**: Unclear instructions, missing examples
- 💡 **Enhancement**: New features, improved workflows
- 🔧 **Tool**: Validator, indexer, converter improvements
- 🤔 **Question**: Usage questions, clarifications

### 2. Suggesting Enhancements

We welcome suggestions for:
- **New fields or sections** that improve signal preservation
- **Platform-specific optimizations** for different LLMs
- **Tool improvements** (validator, indexer, etc.)
- **Documentation enhancements** (guides, examples, tutorials)
- **Integration patterns** with other systems

**Enhancement proposals should include**:
1. **Problem statement**: What limitation does this address?
2. **Proposed solution**: How would this work?
3. **Use cases**: Who benefits and how?
4. **Compatibility**: Does this break existing implementations?
5. **Examples**: Show what it would look like

### 3. Contributing Examples

High-quality example outputs are valuable for:
- Demonstrating protocol compliance
- Showing domain-specific applications
- Illustrating edge cases
- Teaching best practices

**Example contribution checklist**:
- [ ] Passes validator.py without errors
- [ ] Token count within mode budget
- [ ] Real (or realistic) conversation thread
- [ ] Demonstrates specific use case or pattern
- [ ] Includes frontmatter with metadata
- [ ] Properly formatted (###, **, -, ---)

**Where to add**:
- `examples/checkpoint/` - Midway save points
- `examples/re-entry/` - Return after dormancy
- `examples/archive/` - Completed threads

### 4. Improving Documentation

Documentation improvements always welcome:
- Fix typos or unclear language
- Add missing explanations
- Create tutorials or guides
- Translate to other languages
- Add diagrams or visualizations

**Documentation locations**:
- `README.md` - Main overview
- `docs/quickstart.md` - Getting started guide
- `docs/implementation-guide.md` - Detailed usage (create if missing)
- `docs/mode-comparison.md` - Mode selection guide (create if missing)
- `docs/design-philosophy.md` - Why USS exists (create if missing)
- `docs/faq.md` - Common questions (create if missing)

### 5. Building Tools

Tool contributions help operationalize USS:
- **Validator enhancements**: Better checks, more detailed feedback
- **Indexer**: Build searchable archives of summaries
- **Converter**: Transform between formats (MD ↔ JSON ↔ YAML)
- **Visualizer**: Graph thread relationships and evolution
- **Automation**: Auto-trigger checkpoints, scheduled archives
- **Integrations**: Plugins for Obsidian, Notion, Roam, etc.

**Tool requirements**:
- Python 3.9+ for consistency
- Clear CLI interface with --help
- Error handling and user-friendly messages
- Documentation and usage examples
- Type hints for maintainability

### 6. Testing and Validation

Help test USS across different:
- **LLM platforms**: Claude, GPT-4, Grok, Gemini, local models
- **Domains**: Code, research, creative writing, project management
- **Thread lengths**: Short (5-10), medium (20-50), long (100+)
- **Languages**: Test non-English conversations
- **Use cases**: Personal, professional, academic, creative

**Testing feedback should include**:
- Platform and model version
- Thread characteristics
- What worked well
- What failed or confused
- Suggestions for improvement

## Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/[username]/universal-seed-summary.git
cd universal-seed-summary

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run validator on examples
python tools/validator.py examples/checkpoint/checkpoint_example.md -v
```

### Making Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**: Run validator on examples, test tools
5. **Commit with clear messages**: `git commit -m "Add: new validation check for..."`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**: Describe changes and motivation

### Commit Message Format

```
Type: Brief description (50 chars or less)

Detailed explanation if needed. Wrap at 72 characters.
Include motivation, context, and impact.

- Bullet points for multiple changes
- Reference issues: Fixes #123, Relates to #456
```

**Commit types**:
- `Add:` New features, fields, sections, tools
- `Fix:` Bug fixes, corrections
- `Docs:` Documentation only
- `Refactor:` Code restructuring without behavior change
- `Test:` Adding or updating tests
- `Style:` Formatting, typos (no functional change)

### Pull Request Guidelines

**Before submitting PR**:
- [ ] Code follows existing style
- [ ] All examples pass validator
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] No breaking changes (or clearly documented)

**PR description should include**:
1. **What changed**: Summary of modifications
2. **Why**: Motivation and context
3. **How to test**: Steps to verify changes
4. **Screenshots/examples**: If applicable
5. **Related issues**: Links to relevant issues

## Code Style

### Protocol Specifications (JSON/YAML)

- Use 2-space indentation
- Keep field names consistent: `Snake_Case_With_Capitals`
- Include descriptions for all fields
- Maintain alphabetical ordering where logical

### Python Code

- Follow PEP 8 style guide
- Use type hints for functions
- Include docstrings for classes and functions
- Maximum line length: 88 characters (Black formatter compatible)
- Use meaningful variable names

### Markdown Documentation

- One sentence per line (makes diffs cleaner)
- Use ATX-style headers (`###` not `---`)
- Include code blocks with language specification
- Link to other docs using relative paths

## Protocol Changes

Protocol changes require careful consideration due to backward compatibility.

### Minor Changes (v1.x)

**Acceptable for minor versions**:
- Adding new optional sections
- Adding new optional fields
- Clarifying existing requirements
- Adding examples or documentation
- Tool improvements

**Process**:
1. Discuss in issue before implementing
2. Ensure backward compatibility
3. Update CHANGELOG.md
4. Update version in protocol specification
5. Test with existing examples

### Major Changes (v2.0)

**Requires major version bump**:
- Removing required sections or fields
- Renaming core sections
- Changing fundamental structure
- Breaking existing implementations

**Process**:
1. Create RFC (Request for Comments) issue
2. Allow 2+ weeks for community feedback
3. Document upgrade path clearly
4. Provide migration tools if possible
5. Maintain v1.x in separate branch

## Community Guidelines

### Be Respectful

- Welcome newcomers and diverse perspectives
- Assume good intentions
- Provide constructive feedback
- Respect time and effort of contributors

### Be Clear

- Use specific examples
- Explain technical terms
- Link to relevant documentation
- Break down complex ideas

### Be Collaborative

- Credit others' ideas and work
- Build on existing contributions
- Share knowledge generously
- Help others succeed

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md for significant contributions
- README.md (optional contributors section)
- Git commit history (always)

## Questions?

- **Documentation questions**: Check docs/ directory
- **Usage questions**: See docs/faq.md or open issue
- **Protocol design questions**: Open discussion issue
- **Tool questions**: Check tool's --help or open issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping improve USS!** 🚀

Every contribution—whether bug report, documentation fix, or new feature—makes this protocol more useful for everyone.
