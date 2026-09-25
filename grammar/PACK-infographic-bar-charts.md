# Infographic Bar Charts — scene inventory from the preview

Source: `~/timeline/Infographic Bar Charts/preview_540p_crf22_higher_quality-2.mp4`
45.0s, 960x540, 30fps. Timestamps below are from a 2.5s sample grid, so they mark where a
scene is visible, not its exact cut. Style is dark with teal bars over a faint world map,
"BAR CHART" title and a PixelTruck watermark. All swappable.

| t | scene | serves |
|---|---|---|
| 0.0, 2.5 | overview grids of many small chart variants | catalogue only, not a scene |
| 5.0 | four rounded vertical bars, a percentage above each, caption block below | **`parallel_instances`** |
| 7.5 | same, second value set | **`parallel_instances`** |
| 10.0, 12.5 | three group panels, two bars per panel, two-item legend | **`inversion`** |
| 15.0 | horizontal rows A-D, two series per row, two-item legend | **`inversion`** |
| 20.0, 22.5 | signed-value chart, bars above and below a zero line, -1000 to 1000 | **`change_across_set`** |
| 25.0 | twelve-bar monthly series, JAN through DEC | `streak_over_time` |
| 30.0 | horizontal funnel rows, five labelled stages | `category_breakdown`, `proportion_of_cohort` |
| 32.5 | ten-bar year series | `streak_over_time` |
| 37.5 | single progress bar to 100% with caption | `derived_quantity` |
| 40.0, 42.5 | three group panels, three series per panel | `paired_values_by_group` at higher arity |

## Against `inversion`

Two scenes serve it and the horizontal one is the better fit.

**Horizontal rows with two series (t=15).** Each row is a member, each row carries two bars in
the same unit, and the legend names the two measures once. Reading down the rows, the reversal
is visible as the longer bar switching sides. That is the flip, which is the thing no template
in the library could show.

**Grouped panels with two bars (t=10, 12.5).** Same data shape, vertical. Shows three panels in
the preview; six members needs either six panels or two uses.

Neither is ranked, neither requires a portrait, and both encode magnitude rather than printing
values, which is the correction from review.

## Beyond the job it was sourced for

**`change_across_set` at t=20.** Bars above and below a zero line is exactly places gained and
lost, with the member who does not move sitting flat on the line. That is passage 12. Between
this and `truth-rank-fall`, the job now has two candidates and needs nothing built.

**`parallel_instances` at t=5.** Four bars, a percentage each, a caption each. This is the
graph treatment asked for in review, where four near-identical portrait cards were called
redundant.

## Still needed before binding

Scene boundaries and per-scene slot counts, which the clipping pass will produce. Everything
above is read off a preview grid, so treat the arity as approximate: what matters is the data
shape each scene accepts, not the number of bars visible in the sample.
