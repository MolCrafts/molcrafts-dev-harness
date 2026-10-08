## .claude/notes/law.md (canonical body)

Written on create. On update, append any missing `<!-- mol:law:id:* -->`. Never reword an id that already exists.

Each law is one prohibition. A rule that names no forbidden design is not a law. Carve-outs live in § VII and name the subsystem. YAGNI, SOLID, and DRY do not outrank a law.

```markdown
# Software Engineering Laws

Every rule here outranks scope and convenience. CLAUDE.md indexes one line per law.
Adding, changing, or repealing a law is `/mol:note`. No skill retires a law.

<!-- mol:law:id:conceptual-integrity -->
## 1. Conceptual integrity

Never create a second abstraction, alias, or layer for a concept that already exists.

<!-- mol:law:id:architecture-first -->
## 2. Architecture first

Never add a layer whose only justification is later use or unmeasured performance.

<!-- mol:law:id:earn-complexity -->
## 3. Earn complexity

Never generalize, add a knob, or add an extension point without a present caller.

<!-- mol:law:id:locality-of-change -->
## 4. Locality of change

Never require unrelated modules to change together, and never introduce a cycle. A unit goes green with `$META.build.test_single` and fakes. If it needs the whole graph, the boundary is wrong.

<!-- mol:law:id:hide-decisions -->
## 5. Hide decisions, expose contracts

Never leak representation, lifecycle, or storage across a boundary.

<!-- mol:law:id:dependencies-follow-policy -->
## 6. Dependencies follow policy

Never let domain code depend on UI, a serialization format, a language binding, or a framework that then defines the semantics.

<!-- mol:law:id:primitive-surface -->
## 7. Primitive public surface

Never ship an all-in-one façade or a second public name that becomes its own contract.

<!-- mol:law:id:explicit-flow -->
## 8. Explicit flow

Never rely on hidden context or on a step the caller can forget.

<!-- mol:law:id:one-home -->
## 9. One home per fact

Never keep two writable copies of the same fact. A serialization copy is fine; a second owner is not.

<!-- mol:law:id:no-silent-debt -->
## 10. No silent debt

Rot in a file you are editing is fixed or reported with path:line. Never skip-mark it, never weaken an assert, never widen the edit to files you are not already changing.

<!-- mol:law:id:tests-owned-behavior -->
## 11. Tests verify owned behavior

Tests live with the owner of the behavior. `tests/` is unit tests of one module. Broader scenarios go under `regressions/` with a stated reason.

# VII. Exceptions

A violation is recorded here, naming the law, the subsystem, the evidence, and the removal condition. An agent does not grant one.

# VIII. Heuristics

YAGNI, SOLID, and DRY are hints. They do not beat a law above.

<!-- project invariants: one `<!-- mol:law:id:<slug> -->` and one prohibition each -->
```
