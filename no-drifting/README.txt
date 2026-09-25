NO DRIFTING
===========

Rule set by the user on 2026-09-20.

Every new feature, addition, fix or implementation must have three things before it ships:

  1. A REAL PROBLEM        stated concretely, with evidence that it is occurring
  2. AN EXPLANATION        why that is the real problem to solve, given the objective
  3. A TEST                that fails without the change and passes with it

No entry is complete without all three. A change with no test is a change nobody can
know is working, which is how this project accumulated defects that only the user caught.

OBJECTIVE THIS IS MEASURED AGAINST
  Land the right media candidate on the right beat.

Anything that does not measurably move that is drift, whatever else it improves.

FILES
  LOG.txt        every change, newest last, in the entry format below
  RCA-*.txt      root cause analyses
  FP-*.txt       first-principles derivations

ENTRY FORMAT
  [NNNN] YYYY-MM-DD  one-line title
  PROBLEM     what was observed to be wrong, with numbers where possible
  WHY REAL    why this blocks the objective, not just why it is untidy
  CHANGE      what was done
  TEST        the test that validates it, by name
  VERIFIED    the measured result after the change
  STATUS      done | open | superseded

An entry may be logged with STATUS open and no CHANGE — a found problem is worth
recording before it is fixed. An entry with CHANGE and no TEST is not allowed to close.
