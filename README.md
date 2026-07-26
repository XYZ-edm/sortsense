# SortSense

**Real-time waste sorting with on-device computer vision.**

SortSense is an end-to-end pipeline that turns a single camera frame into a
sorting decision — object detection, waste-category classification, and a
cost-aware policy that decides whether to trust the prediction or reject it
— designed to run fully on-device on embedded hardware (Jetson-class SBCs),
with no cloud round-trip required for the sorting decision itself.

This repository is a curated, from-scratch write-up of the system's
architecture and engineering process. It intentionally does not include the
trained model weights, the calibrated production thresholds, the training
dataset, or deployment-specific configuration — those are the parts that
took the most iteration to get right, and stay private for now.

## Why this exists

Recycling contamination — the wrong material in the wrong bin — is one of
the main reasons collected waste ends up in landfill instead of being
recycled. A sorting assistant that gives real-time feedback at the point of
disposal (before contamination happens) is cheap to deploy compared to
sorting-facility infrastructure, and can run on low-cost embedded hardware.

## Architecture

```
 camera frame
      |
      v
 [ 1. Detector ]        class-agnostic object detection (YOLOX, Apache-2.0
      |                  license — chosen deliberately over YOLOv8/AGPL for
      |                  commercial-use compatibility, see engineering notes)
      v
 [ 2. Stability &        rejects transient/blurry frames; only a
    presence tracker ]   temporally-stable, well-formed crop proceeds
      |
      v
 [ 3. Classifier ]      waste-category classification (6 classes) on the
      |                  cropped region
      v
 [ 4. Decision policy ] asymmetric confidence thresholds, calibrated
      |                  per-class to weigh "false accept" (contamination)
      |                  against "false reject" (missed recyclable) —
      |                  see engineering notes for the reasoning
      v
 [ 5. Crop logger ]     every processed frame (accepted or rejected) is
                         logged locally with its metadata, from day one,
                         so real-world data exists before any cloud/active-
                         learning layer is built on top of it
```

Each stage is a separate, independently testable module. The detector and
classifier are swappable behind a thin adapter interface — the project
migrated detector backbones once already (see below) without touching the
decision logic downstream.

## Engineering notes (a few decisions worth explaining)

- **Detector license migration.** The initial detector choice (YOLOv8)
  carries an AGPL-3.0 license, which is incompatible with a closed-source
  commercial product. Migrated to YOLOX (Apache-2.0) behind a class-agnostic
  adapter — six downstream consumer modules updated, core product logic
  (crop quality control) untouched. Hit-rate improved as a side effect
  (~88% vs ~81% on an internal detection sample).

- **Asymmetric decision thresholds, not a single confidence cutoff.**
  Treating every misclassification as equally costly is wrong here: a
  contaminated recyclable stream is more expensive to fix downstream than a
  recyclable item conservatively routed to "unsure." Thresholds are
  calibrated per class against a declared cost ratio, trading a higher
  rejection rate for a large drop in contamination rate.

- **Data logging before any cloud/ML-ops layer.** Crop capture + local
  logging was deliberately built *before* any cloud upload or active-learning
  pipeline, specifically so that real operating data would exist before
  betting engineering time on infrastructure for data that didn't exist yet.
  (An internal review later flagged that some downstream infra had been
  built ahead of data volume anyway — a useful lesson in sequencing,
  documented and corrected.)

- **Camera-loop hardening.** Long-running/unattended operation needs to
  survive a camera dropping out. Reconnection uses exponential backoff with
  a bounded retry count, tested with dependency-injected fakes (no real
  camera needed to exercise the failure paths). A dedicated stress harness
  cycles real images through the full production pipeline for thousands of
  iterations, sampling RSS memory to catch slow leaks that a short
  interactive session wouldn't reveal.

- **Every module has direct-assert tests, run with one command.** No
  pytest dependency — a single script discovers and runs every `test_*.py`
  module and reports pass/fail counts, intentionally simple so it's obvious
  what is and isn't covered.

## Status

Actively developed. Detection and classification pipeline validated on a
held-out test set; decision-policy calibration validated against a declared
(not yet field-verified) cost assumption; long-run stability tested via
synthetic stress runs. Physical deployment work is in progress.

## License

MIT — see [LICENSE](LICENSE). Model weights, calibrated thresholds, and
training data are not included in this repository.
