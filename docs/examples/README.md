# Example Domain Code — Do Not Use as Core API

**These examples are for reference only.** They contain domain-specific logic (e.g. spread, liquidity, PnL) and are **not** part of the core package.

- **Core API:** `modulate(Proposal, GuardPolicy, context)` — see main README and `dmc_core.dmc`.
- **Example domain legacy:** `example_domain_legacy_v0/` — legacy guards and policy; not installed with the package.

Do not import these modules in production code that depends on the domain-agnostic core.
