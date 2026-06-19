"""Runtime prompt compiler for USS Engine v0.4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .redactor import RedactionReport
from .schema import InvocationMode, ValidationReport
from .transcript import NormalizedThread


class RuntimePrompt(BaseModel):
    """Compiled prompt payload ready for an LLM client."""

    mode: InvocationMode
    protocol_version: str = "1.3"
    system_prompt: str
    user_prompt: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    def as_messages(self) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]

    def as_text(self) -> str:
        return f"SYSTEM:\n{self.system_prompt}\n\nUSER:\n{self.user_prompt}"


def load_protocol(path: str | Path) -> dict[str, Any]:
    """Load a USS protocol JSON file."""

    protocol_path = Path(path)
    with protocol_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("protocol JSON must parse to an object")
    return data


def compile_runtime_prompt(
    *,
    protocol: dict[str, Any],
    thread: NormalizedThread,
    mode: InvocationMode | str,
    max_transcript_chars: int | None = None,
    redaction_report: RedactionReport | None = None,
) -> RuntimePrompt:
    """Compile USS v1.3 protocol + normalized thread into LLM runtime prompts."""

    resolved_mode = InvocationMode(mode)
    protocol_name = str(protocol.get("protocol", "Universal Seed Summary Invoker"))
    protocol_version = str(protocol.get("version", "1.3"))
    invocation_modes = protocol.get("invocation_modes", {})
    mode_spec = invocation_modes.get(resolved_mode.value, {}) if isinstance(invocation_modes, dict) else {}
    output_spec = protocol.get("output_specification", {})
    enforcement_rules = protocol.get("enforcement_rules", {})
    sections = protocol.get("sections", {})
    checklist = protocol.get("validation_checklist", {})

    required_section_titles = _extract_required_section_titles(sections, resolved_mode)
    transcript_block = thread.to_prompt_block(max_chars=max_transcript_chars)
    redaction_payload = (
        redaction_report.model_dump(mode="json")
        if redaction_report is not None
        else {"redacted": False, "hit_count": 0, "hits": [], "categories": {}}
    )

    system_prompt = f"""You are executing {protocol_name} v{protocol_version} as a strict runtime protocol.

NON-NEGOTIABLE RULES:
- Use only the supplied normalized transcript as source material.
- Do not add external facts, outside context, assumed user history, or invented artifacts.
- If information is absent, explicitly declare absence using the protocol's required null language.
- Preserve explicit decisions, unresolved tensions, constraints, and epistemic boundaries.
- Output only the final USS Markdown artifact. Do not include analysis, explanations, code fences, or prefaces.
- Follow the requested invocation mode exactly: {resolved_mode.value}.
""".strip()

    user_prompt = f"""# Runtime Invocation

Protocol: {protocol_name}
Protocol Version: {protocol_version}
Invocation Mode: {resolved_mode.value}
Mode Spec:
{json.dumps(mode_spec, indent=2, ensure_ascii=False)}

# Output Specification
{json.dumps(output_spec, indent=2, ensure_ascii=False)}

# Enforcement Rules
{json.dumps(enforcement_rules, indent=2, ensure_ascii=False)}

# Required Sections For This Mode
{chr(10).join(f'- {title}' for title in required_section_titles)}

# Section Contract
{json.dumps(sections, indent=2, ensure_ascii=False)}

# Validation Checklist
{json.dumps(checklist, indent=2, ensure_ascii=False)}

# Evidence Anchoring Guidance
USS Engine v0.4 can inspect deterministic evidence anchors after generation. When making concrete claims, prefer brief source hints using this syntax when it does not damage readability: [evidence: msg_0001, msg_0002]. Evidence hints must only reference message IDs present in the normalized transcript. Do not fabricate message IDs.

# Normalized Thread Metadata
- thread_id: {thread.thread_id}
- source: {thread.source}
- created_at: {thread.created_at}
- message_count: {len(thread.messages)}
- exchange_pair_count: {thread.exchange_pair_count}
- char_count: {thread.char_count}

# Redaction Report
{json.dumps(redaction_payload, indent=2, ensure_ascii=False)}

# Normalized Transcript
{transcript_block}

# Task
Generate one valid USS Markdown artifact for invocation mode `{resolved_mode.value}`. Include YAML front matter at the top. Use the normalized thread metadata where appropriate. The output must pass structural validation by USS Engine. Keep claims tightly grounded in source messages so the v0.4 evidence inspector can anchor them.
""".strip()

    return RuntimePrompt(
        mode=resolved_mode,
        protocol_version=protocol_version,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        metadata={
            "thread_id": thread.thread_id,
            "message_count": len(thread.messages),
            "exchange_pair_count": thread.exchange_pair_count,
            "required_sections": required_section_titles,
            "redaction_hit_count": int(redaction_payload.get("hit_count", 0)),
        },
    )


def compile_repair_prompt(
    *,
    previous_output: str,
    validation_report: ValidationReport,
    runtime_prompt: RuntimePrompt,
) -> RuntimePrompt:
    """Compile a repair prompt for retry-on-validation-failure loops."""

    issues = [issue.model_dump(mode="json") for issue in validation_report.issues]
    repair_user_prompt = f"""The previous USS artifact failed validation. Repair the artifact so it passes USS Engine validation.

# Validation Report
{json.dumps(issues, indent=2, ensure_ascii=False)}

# Previous Output
{previous_output}

# Repair Rules
- Return only the corrected USS Markdown artifact.
- Preserve all thread-derived content that is still valid.
- Fix missing sections, missing fields, vague nulls, invalid timestamps, and archive-only requirements.
- Do not add facts beyond the normalized transcript supplied in the original runtime prompt.
""".strip()

    return RuntimePrompt(
        mode=runtime_prompt.mode,
        protocol_version=runtime_prompt.protocol_version,
        system_prompt=runtime_prompt.system_prompt,
        user_prompt=repair_user_prompt,
        metadata={**runtime_prompt.metadata, "repair": True},
    )


def _extract_required_section_titles(sections: Any, mode: InvocationMode) -> list[str]:
    if not isinstance(sections, dict):
        return []

    titles: list[str] = []
    for _, section in sections.items():
        if not isinstance(section, dict):
            continue
        required = section.get("required") is True
        required_for = section.get("required_for")
        if required or (mode == InvocationMode.archive and required_for == "archive mode only"):
            title = section.get("title")
            if title:
                titles.append(str(title))
    return titles
