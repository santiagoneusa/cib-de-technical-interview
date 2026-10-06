---
name: ai-log
description: How to record human–AI collaboration in docs/bitacora_ia.md. Load whenever a decision is taken at a checkpoint, an AI proposal is corrected/discarded, or an AI claim is validated against the data.
---

# AI collaboration log

The test states: "Usar IA no penaliza; ocultarlo o no validarlo sí." The log is the evidence.

## When to write an entry
- Every checkpoint decision (who decided, what options were on the table).
- Every AI proposal that the human corrected, discarded or validated against the data.
- Every AI claim about the data that was checked with code (show the check).

## Entry format (Spanish)
```
### <fecha> · <fase/actividad> · <título corto>
- **Prompt / pedido:** ...
- **Propuesta de la IA:** ...
- **Decisión humana:** aceptada | corregida | descartada — por qué
- **Validación contra datos:** notebook + celda / cifra que lo respalda
```

## Rules
- Write facts, not praise. Keep each entry ≤ 6 lines.
- Attribute decisions honestly: the human owns judgment calls; the AI implements and proposes.
- Never log secrets or personal data.
