"""Illustrative, standalone version of the decision-policy pattern used in
production. Real per-class thresholds and the underlying cost-ratio study
are not published here -- this file exists to show the *shape* of the
solution (asymmetric, per-class thresholds against a declared cost model),
not the calibrated numbers themselves.

In production this module is consumed right after classification: the
classifier's top-1 class + confidence + which detection "path" produced the
crop go in, and a routing decision comes out.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    ACCEPT = "accept"          # trust the top-1 prediction, route accordingly
    REJECT_UNSURE = "reject"   # route to a human-reviewed / general bin instead


@dataclass(frozen=True)
class PerClassThreshold:
    class_name: str
    min_confidence: float


class DecisionPolicy:
    """Confidence-gates a classification result before it is allowed to
    drive a physical sorting action.

    Uses per-class thresholds rather than one global cutoff, because the
    cost of a wrong "accept" is not symmetric across classes: some
    misclassifications contaminate a downstream recyclable stream (costly),
    others just waste one sorting opportunity (cheap). Real thresholds are
    calibrated offline against a declared cost ratio and are not included
    in this illustrative version -- values below are placeholders.
    """

    # Placeholder thresholds -- NOT the calibrated production values.
    _DEFAULT_THRESHOLDS = (
        PerClassThreshold("plastic", 0.60),
        PerClassThreshold("paper", 0.60),
        PerClassThreshold("glass", 0.65),
        PerClassThreshold("metal", 0.60),
        PerClassThreshold("organic", 0.55),
        PerClassThreshold("other", 0.70),
    )

    def __init__(self, thresholds=None):
        self._thresholds = {t.class_name: t.min_confidence
                             for t in (thresholds or self._DEFAULT_THRESHOLDS)}

    def decide(self, predicted_class: str, confidence: float, provenance: str) -> Decision:
        threshold = self._thresholds.get(predicted_class)
        if threshold is None:
            return Decision.REJECT_UNSURE
        if confidence >= threshold:
            return Decision.ACCEPT
        return Decision.REJECT_UNSURE
