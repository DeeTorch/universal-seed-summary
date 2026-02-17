# USS Frequently Asked Questions

## General Questions

### What is USS?
Universal Seed Summary Invoker is a protocol for distilling LLM conversation threads into compressed, signal-preserving summaries that maintain continuity across sessions.

### How is USS different from regular summarization?
USS is audit-grade distillation, not narrative summarization. It preserves architectural decisions, tracks epistemic boundaries, explicitly declares compression losses, and maintains decision audit trails.

### Which LLMs work with USS?
USS is model-agnostic. Tested on Claude (3.5 Sonnet, 4, Opus), GPT-4 (Turbo, 4.5), Perplexity AI, Grok (2, 3), and Gemini Pro/Ultra. Any instruction-following model should work.

### Is USS free to use?
Yes. USS is MIT licensed for commercial and personal use.

## Usage Questions

### When should I create a checkpoint?
Every 15-20 exchanges, at natural breakpoints, end of work sessions, or before context switches.

### When should I use re-entry mode?
When returning to a dormant thread after days or weeks away and need full context restoration.

### When should I archive?
When a thread is complete, abandoned, or needs permanent storage for compliance or knowledge base purposes.

### How long does USS take to generate?
Typically 30-60 seconds depending on thread length and LLM speed.

### Can I modify the protocol?
Yes. USS is MIT licensed. You can add custom fields, create new modes, or fork for proprietary use.

## Technical Questions

### What's the compression ratio?
USS achieves 15:1 to 30:1 compression ratios while maintaining signal integrity.

### How accurate is the token budget?
Token estimation uses `words * 1.3` as rough approximation. Actual tokenization varies by model.

### Can I automate USS invocation?
Yes. Create wrapper scripts that trigger USS-CHECKPOINT at intervals or token thresholds.

### How do I validate output?
Use `python tools/validator.py your-summary.md` to check protocol compliance.

### How do I search archived summaries?
Use `python tools/indexer.py ./summaries/ --search "keyword"` to search indexed archives.

## Thread Management

### How do I handle very long threads (100+ exchanges)?
Create checkpoints every 15-20 exchanges, use Thread Topology to link them, and create final archive referencing all checkpoints.

### Can I link related threads?
Yes. Use the Thread Topology section to document parent/child/sibling relationships.

### What if my thread has multiple topics?
USS captures this through Paradigm Nodes (framing shifts) and Focus Domains (domain intersections).

### Should I create multiple summaries for one thread?
Yes. Create checkpoints during development, re-entry when resuming, and archive at completion.

## Output Quality

### What if my LLM doesn't follow the format?
Use the full protocol specification reference in your invocation. Add explicit formatting instructions.

### What if sections are missing?
Re-invoke with clearer instructions or manually add missing sections following the protocol.

### What if Failure Semantics is vague?
Explicitly instruct: "Be specific about compression losses. Don't use generic phrases like 'some nuance may be lost'."

### What if token count exceeds budget?
For checkpoint/re-entry, this indicates need for compression. For archive, exceeding budget is acceptable.

### How do I know if output is good?
Run validator, check all sections present, verify no vague language in Failure Semantics, confirm thread-derived content only.

## Integration Questions

### Can I use USS with Obsidian/Notion/Roam?
Yes. Save summaries as markdown files in your vault/workspace. Use indexer to build searchable database.

### Can I convert USS to other formats?
Yes. Use `python tools/converter.py summary.md --to json` to convert between Markdown, JSON, and YAML.

### Can I build on top of USS?
Yes. USS is MIT licensed. Build tools, integrations, or extensions freely.

### How do I integrate with CI/CD?
Add validation step: `python tools/validator.py summaries/**/*.md --strict` in your pipeline.

## Troubleshooting

### "My output has concepts not in the thread"
Re-invoke with emphasis on "thread-derived only" constraint. Explicitly forbid external information.

### "Failure Semantics says 'None' but I see issues"
LLM may be too optimistic. Manually review and update Failure Semantics section.

### "Token count way over budget"
Thread may be too complex for mode. Try archive mode or break into multiple checkpoints.

### "Validator shows errors"
Check error messages. Common issues: missing sections, incorrect formatting, missing frontmatter.

### "Indexer doesn't find my files"
Ensure files have YAML frontmatter with `mode:` field. Check file extension is `.md`.

## Best Practices

### How often should I checkpoint?
Every 15-20 exchanges or at natural breakpoints (end of session, major decision, context switch).

### Should I edit USS output?
Yes. USS is a starting point. Manually refine for accuracy, especially Failure Semantics.

### How do I organize summaries?
Use naming convention: `{project}_{archetype}_{YYYYMMDD}_{mode}.md`. Organize by project or date.

### Should I commit summaries to git?
Yes. Summaries are valuable project documentation and benefit from version control.

### How do I share summaries with team?
Save in shared repository, use indexer to build searchable database, link in project documentation.

## Advanced Usage

### Can I create custom modes?
Yes. Define your own token budgets and section requirements. Document in your fork.

### Can I add custom fields?
Yes. Add to existing sections or create new optional sections. Maintain backward compatibility.

### Can I use USS for non-code projects?
Yes. USS works for any conversation: research, creative writing, project management, learning.

### Can I combine multiple threads?
Use Thread Topology to link related threads. Create meta-summary referencing child summaries.

### Can I use USS with local models?
Yes. Any instruction-following model works. Test with your specific model and adjust prompts as needed.

## Contributing

### How do I report bugs?
Open issue on GitHub with protocol version, LLM platform, mode, and reproducible example.

### How do I suggest features?
Open issue with problem statement, proposed solution, use cases, and compatibility notes.

### How do I contribute examples?
Submit PR with validated example in appropriate examples/ subdirectory.

### How do I improve tools?
Fork repository, make changes, test thoroughly, submit PR with description and tests.

## Still Have Questions?

- Check [Implementation Guide](implementation-guide.md) for detailed section explanations
- See [Mode Comparison](mode-comparison.md) for mode selection guidance
- Read [Design Philosophy](design-philosophy.md) for conceptual background
- Open issue on GitHub for specific questions
