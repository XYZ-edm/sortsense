# Contributing to SortSense

This repository is a curated write-up of the system's architecture and engineering
process, not the full production codebase (see the README for what is intentionally
left out: model weights, calibrated thresholds, training data).

That said, contributions and feedback on what is here are welcome.

## Useful ways to contribute

- **Vision / ML engineers**: try the showcase code on your own hardware, report
  what breaks and why.
- **Researchers**: point out failure modes the known-limits section does not
  cover, or reproduce the tested behavior independently.
- **Waste management operators or municipalities**: use the collaboration issue
  template if you are interested in a field trial.

## Process

1. Open an issue first describing what you want to change or add, so scope is
   agreed before any work happens.
2. Keep pull requests small and focused on one thing.
3. If a change touches a claim in the README (a number, a limitation, a design
   decision), it needs to stay backed by something verifiable in this repo -
   no unverified figures.

## Not looking for

- PRs that add dependencies to the showcase scripts (they are deliberately
  dependency-free).
- Speculative features beyond what the architecture section describes.
