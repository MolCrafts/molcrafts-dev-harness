# Large-spec split

`spec-writer` returns `Status: split-needed` only when the drafted Tasks list has more than 10 items. Cross-layer work stays one spec.

Cut into an ordered chain:

```
<base>-01-<phase>
<base>-02-<phase>
```

Each part has at most 10 tasks and is implementable once earlier parts have landed. A cut that cannot be ordered that way is `blocked`, not `split-needed`.

`/mol:spec` does not ask. It re-invokes `spec-writer` per sub-slug, runs architect design-mode on each, and persists none until every part is clear. Then one `/mol:impl-all` on `<base>`.

One commit for the whole chain, at `/mol:impl-all` chain end. No per-spec stage commit.
