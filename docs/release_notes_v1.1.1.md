# USS Engine v1.1.1 Release Notes

## Evidence Classifier + Scoring Calibration Hotfix

This patch calibrates the evidence engine after the first live Gemini provider run.

### Fixed

- `Focus_Domains` is now classified as `derived_metadata` instead of unsupported.
- `Invoker` is now classified as `system_metadata` instead of unsupported.
- `Failure_Severity` is now classified as `protocol_assessment` instead of unsupported.
- Protocol-required null declarations are classified as `protocol_null_declaration`.
- Metadata/protocol classifications no longer reduce evidence support scores as unsupported claims.

### Preserved

- Real unsupported factual claims still receive `unsupported`.
- Missing explicit message references still fail evidence validation.
- Provider adapters and E2E run behavior are unchanged.
