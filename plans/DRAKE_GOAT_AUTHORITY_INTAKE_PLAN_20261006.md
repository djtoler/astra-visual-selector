# Drake GOAT authority intake plan

Objective: admit the newly released `drake-goat@1` StoryPackage through the existing general Matching path without weakening authority validation or adding story-specific matching behavior.

1. Add exact Story authority commit `727513e94d672302f1215c6659e7d614ac83fc41` to the existing supported-commit allow-list.
   - Acceptance: older pins remain intact; arbitrary commits still fail closed.
2. Run the authoritative adapter against the released package and its pinned registry.
   - Acceptance: upstream checker passes, package digest remains `6f67e533200f5867a4da28c03b4b636682d9bc5a02dea4415b5ce8a1e7eac057`, and selection/render authorization remain false.
3. Run the focused adapter/contract tests and the full Matching command with the unchanged task contract.
   - Acceptance: complete claim routing, structured capability admission, harness validation, schema-bound review receipt, and no story-specific runtime rule.

No visual selection or rendering is authorized by this plan.
