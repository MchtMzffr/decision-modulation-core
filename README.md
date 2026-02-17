# decision-modulation-core (Guards & Modulation)

This core converts a `Proposal` into a `FinalDecision` by applying **deterministic, fail-closed guards**.
It is domain-agnostic and depends only on `decision-schema`.

## Responsibilities

- Guard pipeline: allow / clamp / reject / escalate
- Deterministic guard ordering
- Fail-closed behavior on any error

## Contracts

- **Input**: `decision_schema.types.Proposal`
- **Output**: `decision_schema.types.FinalDecision`
- **Trace**: `decision_schema.packet_v2.PacketV2`

## Integration

**Core API:** `modulate(Proposal, GuardPolicy, context)`. Domain examples live only in `docs/examples/`.

```python
from decision_schema.types import Proposal, FinalDecision, Action
from dmc_core.dmc.modulator import modulate
from dmc_core.dmc.policy import GuardPolicy

proposal = Proposal(action=Action.ACT, confidence=0.8, ...)
context = {"now_ms": 1000, "last_event_ts_ms": 950, "errors_in_window": 0, "steps_in_window": 10, ...}

final_decision, mismatch = modulate(proposal, GuardPolicy(), context)

if mismatch.flags:
    # Guards triggered - fail-closed
    print(f"Guards triggered: {mismatch.reason_codes}")
else:
    # Proposal approved
    print(f"Final decision: {final_decision.action}")
```

## Documentation

- `docs/ARCHITECTURE.md`: System architecture
- `docs/FORMULAS.md`: Guard formulas and thresholds
- `docs/INTEGRATION_GUIDE.md`: Integration examples

## Installation

```bash
pip install -e .
```

Or from git:
```bash
pip install git+https://github.com/MeetlyTR/decision-modulation-core.git
```

## Tests

```bash
pytest tests/
```

## License

[Add your license]
