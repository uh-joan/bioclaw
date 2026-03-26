"""Smart progress tracking for clinical trial landscape analysis.

Execution profile (8 steps):
- Step 1: Overview (~20%)
- Step 2: Phase Distribution (~15%)
- Step 3: Enrollment (~15%)
- Step 4: Endpoints (~15%)
- Step 5: Sponsors (~10%)
- Step 6: Geography (~10%)
- Step 7: Competitors (~5%)
- Step 8: Assembly (~10%)
"""


class ProgressTracker:
    """Smart progress tracker with phase-aware weights."""

    WEIGHTS = {
        'overview': 20,
        'phase_distribution': 15,
        'enrollment': 15,
        'endpoints': 15,
        'sponsors': 10,
        'geography': 10,
        'competitors': 5,
        'assembly': 10,
    }

    def __init__(self, callback=None, skip_sections=None):
        self.callback = callback
        self.current_step = 'overview'
        self.step_progress = 0.0

        # Build active weights, redistributing skipped weight
        if skip_sections:
            active = {k: v for k, v in self.WEIGHTS.items() if k not in skip_sections}
            total_active = sum(active.values())
            if total_active > 0:
                scale = 100.0 / total_active
                self.weights = {k: v * scale for k, v in active.items()}
            else:
                self.weights = dict(self.WEIGHTS)
        else:
            self.weights = dict(self.WEIGHTS)

        # Calculate cumulative start percentages
        self.starts = {}
        cumulative = 0
        for step, weight in self.weights.items():
            self.starts[step] = cumulative
            cumulative += weight

    def _calculate_percent(self) -> int:
        start = self.starts.get(self.current_step, 0)
        weight = self.weights.get(self.current_step, 0)
        return min(99, int(start + (weight * self.step_progress)))

    def report(self, message: str):
        if self.callback:
            pct = self._calculate_percent()
            self.callback(pct, message)

    def start_step(self, step: str, message: str = None):
        self.current_step = step
        self.step_progress = 0.0
        if message:
            self.report(message)

    def update_step(self, progress: float, message: str = None):
        self.step_progress = min(1.0, max(0.0, progress))
        if message:
            self.report(message)

    def complete_step(self, message: str = None):
        self.step_progress = 1.0
        if message:
            self.report(message)


def create_progress_tracker(callback=None, skip_sections=None) -> ProgressTracker:
    """Factory function to create a progress tracker."""
    return ProgressTracker(
        callback=callback,
        skip_sections=skip_sections,
    )
