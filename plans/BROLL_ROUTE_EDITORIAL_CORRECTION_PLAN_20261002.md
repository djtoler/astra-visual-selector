# B-roll route editorial correction plan — 2026-10-02

## Scope

Apply the editor's new beat-specific b-roll rulings to the ordered route source of truth and gallery. Preserve one explicit ambiguity for clarification rather than guessing.

## Stages and acceptance checks

1. Save the rulings as durable task-scoped overrides with user provenance.
2. Rebuild ordered routes so:
   - beats 01 and 02 do not route to b-roll;
   - beats 05, 07, 17, 24, 29 and 30 route to b-roll;
   - beat 15 keeps its beat treatment and places b-roll after the beat;
   - beat 25 routes to an existing timeline-template review;
   - beat 27 permits b-roll or the existing artist images;
   - beat 28 does not route to b-roll;
   - beat 18 does not route to b-roll; the editor explicitly confirmed this after clarification.
3. Enforce the six-choice template gate. A no-b-roll route with fewer than six valid templates remains deferred/blocked rather than silently falling back.
4. Rebuild carried prior choices, release preparation and harness audit in order.
5. Update the existing gallery to show only genuine b-roll segments, including beat 15 as an after-beat segment.
6. Run route, carry-forward, release, harness and UI tests; verify stale inputs fail closed.

No rendering or publishing is authorized.
