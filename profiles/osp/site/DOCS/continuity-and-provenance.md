# Continuity and provenance

Continuity is useful only when a maintainer can explain where a copy came from,
how it is updated, and how it can be restored.

## Minimum provenance record

Each synchronized repository or project should identify:

- the authoritative upstream location;
- the mirror direction and expected update cadence;
- the most recently verified source revision;
- any paths intentionally excluded or transformed;
- the responsible maintenance contact or process; and
- the license and attribution inherited from upstream.

## Verification cycle

1. Fetch the declared upstream revision.
2. Compare expected content and automation paths.
3. Record intentional transformations separately from unexplained drift.
4. Test that a documented recovery path can recreate the hosted copy.
5. Publish a clear status when verification or synchronization is impaired.

## Failure handling

Automation should fail closed when identity, provenance, or destination checks
do not match expectations. Recovery procedures should be testable without a
single provider account, proprietary export, or undocumented credential.
