"""Smart progress tracking for drug safety intelligence analysis.

Execution profile (8 steps):
- Step 1: Drug Resolution (~10%)
- Step 2: Target Biology (~12%)
- Step 3: Label Comparison (~20%)
- Step 4: Trial Safety Signals (~15%)
- Step 5: Literature Synthesis (~12%)
- Step 6: Interaction Analysis (~10%)
- Step 7: Epidemiology Context (~8%)
- Step 8: Risk Matrix + Report (~13%)
"""


class ProgressTracker:
    """Smart progress tracker with phase-aware weights."""

    CORE_WEIGHTS = {
        'drug_resolution': 10,
        'target_biology': 12,
        'label_comparison': 20,
        'trial_signals': 15,
        'literature': 12,
        'interactions': 10,
        'risk_matrix': 13,
        'report': 8,
    }

    FULL_WEIGHTS = {
        'drug_resolution': 8,
        'target_biology': 10,
        'label_comparison': 18,
        'trial_signals': 13,
        'literature': 10,
        'interactions': 9,
        'epidemiology': 10,
        'risk_matrix': 12,
        'report': 10,
    }

    def __init__(self, callback=None, include_epidemiology=False):
        self.callback = callback
        self.include_epidemiology = include_epidemiology
        self.current_step = 'drug_resolution'
        self.step_progress = 0.0

        if include_epidemiology:
            self.weights = dict(self.FULL_WEIGHTS)
        else:
            self.weights = dict(self.CORE_WEIGHTS)

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


def create_progress_tracker(callback=None, include_epidemiology=False) -> ProgressTracker:
    """Factory function to create a progress tracker."""
    return ProgressTracker(
        callback=callback,
        include_epidemiology=include_epidemiology,
    )
