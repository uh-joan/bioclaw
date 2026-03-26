"""Smart progress tracking for disease burden analysis.

Execution profile (sequential phases):
- Phase 1: Epidemiology (~20%)
- Phase 2: Demographics (~15%)
- Phase 3: Trends (~15%)
- Phase 4: Treatment Landscape (~15%)
- Phase 5: Unmet Need (~10%)
- Phase 6: Economic Burden (~15%)
- Phase 7: Assembly + Visualization (~10%)
"""


class ProgressTracker:
    """Smart progress tracker with phase-aware weights."""

    WEIGHTS = {
        'epidemiology': 20,
        'demographics': 15,
        'trends': 15,
        'treatment_landscape': 15,
        'unmet_need': 10,
        'economic_burden': 15,
        'assembly': 10,
    }

    def __init__(self, callback=None, skip_sections=None):
        self.callback = callback
        self.skip_sections = skip_sections or set()

        # Build active weights (exclude skipped sections)
        self.weights = {
            k: v for k, v in self.WEIGHTS.items()
            if k not in self.skip_sections
        }

        # Normalize weights to sum to 100
        total = sum(self.weights.values())
        if total > 0 and total != 100:
            factor = 100.0 / total
            self.weights = {k: v * factor for k, v in self.weights.items()}

        # Calculate cumulative start percentages
        self.starts = {}
        cumulative = 0
        for step, weight in self.weights.items():
            self.starts[step] = cumulative
            cumulative += weight

        self.current_step = 'epidemiology'
        self.step_progress = 0.0

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
    return ProgressTracker(callback=callback, skip_sections=skip_sections)
