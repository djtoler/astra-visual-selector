# Root-cause reference manifest

## Story layer — commit pinned

Repository: `https://github.com/djtoler/patterns`

Branch: `claude/friendly-maxwell-i5brux`

Audited commit: `d5117a6de0fd0c640a336c6f456946ec8b40f319`

### Contract and implementation

- `architecture/storypackage/SPEC-0.2.md`
- `architecture/storypackage/storypackage-0.2.schema.json`
- `architecture/storypackage/matching-handoff-0.2.schema.json`
- `architecture/storypackage/tools/build_tagged_script.py`
- `architecture/storypackage/tools/check.py`
- `architecture/storypackage/tools/build_matching_handoff.py`
- `architecture/storypackage/tools/check_handoff.py`
- `architecture/storypackage/HANDOFF_data_matching_media.md`
- `architecture/storypackage/MATCHING_LAYER_FEEDBACK.md`
- `architecture/storypackage/HANDOVER-v12-repin-20261003.md`

GitHub root:
`https://github.com/djtoler/patterns/tree/d5117a6de0fd0c640a336c6f456946ec8b40f319`

### Current StoryPackages and authoring inputs

- `architecture/storypackage/future-volksgeist@5.storypackage-0.2.json`
- `architecture/storypackage/jayz-drake-settle-it@4.storypackage-0.2.json`
- `architecture/storypackage/year-seventeen@9.storypackage-0.2.json`
- `architecture/storypackage/stories/future-volksgeist.story.json`
- `architecture/storypackage/stories/jayz-drake-settle-it.story.json`
- `script/future-volksgeist-cleaned.md`
- `script/jayz-drake-settle-it-v2.md`
- `script/year-seventeen-script-v2.1.md`
- `architecture/storypackage/HANDOVER-future-volksgeist.md`
- `architecture/storypackage/HANDOVER-jayz-drake-settle-it.md`
- `architecture/storypackage/HANDOVER-year-seventeen.md`

### Source/reference transcripts

- `youtube_doc_analysis/transcripts/full/002_This_Is_The_Only_Way_To_Settle_This_Debate_XMaPrXzclaQ.txt`
- `youtube_doc_analysis/transcripts/full/006_Raps_Misunderstood_Genius_The_Story_of_Future_NZ105XlGPus.txt`
- `youtube_doc_analysis/analyses/analysis_002.json`
- `youtube_doc_analysis/analyses/analysis_006.json`
- `youtube_doc_analysis/synthesis/pattern_library.json`
- `youtube_doc_analysis/synthesis/playbook.md`

These source transcripts are structural references, not the scripts being
matched. Compare how source structure became beats/claims/visual obligations;
do not copy source subject matter into Matching rules.

## Matching layer — authoritative branch

Repository: `https://github.com/djtoler/astra-visual-selector`

Branch: `matching-layer`

### Product and execution contracts

- `AGENTS.md`
- `media_workflows.md`
- `grammar/general-matching-layer-contract.json`
- `grammar/matching-entrypoint-contract.json`
- `grammar/matching-harness-stage-contract.json`
- `plans/general-matching-layer-tasks.json`
- `reports/matching-harness-audit.json`

### Actual transformation path

- `pipeline/matching_contract_gate.py`
- `pipeline/storypackage_adapter.py`
- `pipeline/storypackage_splitter.py`
- `pipeline/visualtask_requirements.py`
- `pipeline/visualtask_matching.py`
- `pipeline/visualtask_batch_matching.py`
- `pipeline/storypackage_candidate_gallery.py`
- `pipeline/focused_candidate_diversity.py`
- `pipeline/focused_review_queue.py`
- `pipeline/focused_review_reconciliation.py`
- `pipeline/matching_harness.py`

### Grammar, tags and capability authority

- `grammar/JOBS.md`
- `grammar/SCOPE.md`
- `grammar/semantic-split-proposal.schema.json`
- `grammar/bindings.json`
- `grammar/capability.json`
- `grammar/class-tags.json`
- `grammar/local-templates.json`
- `grammar/library-snapshot.json`
- `grammar/ae-template-technical-index.json`
- `grammar/ae-scene-composition-mappings.json`
- `grammar/visual-task-technical-requirements.json`
- `grammar/visual-task-media-requirements.json`
- `grammar/visual-task-overrides.json`
- `grammar/eligibility-overrides.json`

### Historical/manual reference evidence

- `grammar/beat-review-export-2026-09-27.json`
- `grammar/visual-tasks.json`
- `pipeline/beats-all.json`
- `pipeline/shotlist.capacity.json`
- `reports/prior-editor-review-reconciliation.json`
- `reports/ordered-visual-route-decisions.json`
- `matching-accuracy/batch-001/`
- `matching-accuracy/held-out-001/`
- `reports/storypackage-02-year-seventeen-matching-handoff.json`
- `reports/storypackage-02-future-volksgeist-v12-candidate-review.json`
- `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-review.json`
- `reports/astra-matching-review-evidence-20261004.json`

The normalized evidence package is the canonical index of editor notes. The
older artifacts are necessary to reconstruct what narration, job, candidates
and constraints the editor was reacting to.

## Missing-reference protocol

Before claiming that an “org” source mapping is absent, search all paths above
and follow their source manifests. If an exact transcript-to-beat/visual-job
artifact is still missing, report:

- expected name and role;
- exact spans or decisions that cannot be verified without it;
- why existing artifacts are insufficient;
- the smallest file or export the editor must supply.

Continue every audit question not dependent on that missing input.
