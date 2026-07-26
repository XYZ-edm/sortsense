"""Illustrative version of the temporal-stability gate used before a crop is
handed to the classifier.

A single detection frame is noisy -- hand tremor, motion, partial occlusion.
Rather than classify every frame the detector fires on, this tracker waits
for the detected box to stay in roughly the same place, in roughly the same
size, for a run of consecutive frames, before declaring the object "present
and stable" and releasing exactly one crop for classification per episode.

Real tuning constants (how much box movement counts as "the same box", how
many consecutive frames are required) are the product of on-hardware
measurement against real hand-held motion and are not published here --
placeholders below are illustrative only.
"""
from dataclasses import dataclass


@dataclass
class Box:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)


class BoxStabilityTracker:
    # Placeholder tuning constants -- not the validated production values.
    REQUIRED_STABLE_FRAMES = 6
    MAX_AREA_VARIATION_PX2 = 1500

    def __init__(self):
        self._last_box = None
        self._stable_count = 0

    def update(self, box: Box) -> bool:
        """Feed one frame's detection box. Returns True exactly on the frame
        where stability is first confirmed (the trigger for classification)."""
        if self._last_box is None:
            self._last_box = box
            self._stable_count = 1
            return False

        area_delta = abs(box.area - self._last_box.area)
        if area_delta <= self.MAX_AREA_VARIATION_PX2:
            self._stable_count += 1
        else:
            self._stable_count = 1

        self._last_box = box

        if self._stable_count == self.REQUIRED_STABLE_FRAMES:
            return True
        return False

    def reset(self):
        self._last_box = None
        self._stable_count = 0
