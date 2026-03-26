"""Smart progress tracking for drug sales forecasting.

Based on actual timing for each phase (measured from production runs):
- Init: ~1%
- Drug identification: ~1%
- Patent analysis: ~1%
- Market sizing: ~23%
- Comparable analysis: ~57% (slowest phase - extensive MCP calls)
- Time-series forecasting: ~12%
- Visualization: ~5%

This module provides weighted progress tracking that reflects real time distribution.
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights."""

    STEP_WEIGHTS = {
        'init': 1,
        'drug_id': 1,
        'patent': 1,
        'market': 23,
        'comparables': 57,
        'forecast': 12,
        'visualization': 5,
    }

    STEP_STARTS = {
        'init': 0,
        'drug_id': 1,
        'patent': 2,
        'market': 3,
        'comparables': 26,
        'forecast': 83,
        'visualization': 95,
    }

    def __init__(self, callback=None):
        """Initialize progress tracker.

        Args:
            callback: Optional callback(percent, message) for progress updates
        """
        self.callback = callback
        self.current_step = 'init'
        self.step_progress = 0.0
        self.weights = self.STEP_WEIGHTS.copy()
        self.starts = self.STEP_STARTS.copy()

    def _calculate_percent(self) -> int:
        """Calculate current overall progress percentage."""
        start = self.starts.get(self.current_step, 0)
        weight = self.weights.get(self.current_step, 0)
        return min(99, int(start + (weight * self.step_progress)))

    def report(self, message: str):
        """Report current progress with a message."""
        if self.callback:
            pct = self._calculate_percent()
            self.callback(pct, message)

    def start_step(self, step: str, message: str = None):
        """Start a new step in the pipeline."""
        self.current_step = step
        self.step_progress = 0.0
        if message:
            self.report(message)

    def update_step(self, progress: float, message: str = None):
        """Update progress within the current step."""
        self.step_progress = min(1.0, max(0.0, progress))
        if message:
            self.report(message)

    def complete_step(self, message: str = None):
        """Mark current step as complete."""
        self.step_progress = 1.0
        if message:
            self.report(message)


def create_progress_tracker(callback=None) -> ProgressTracker:
    """Factory function to create a progress tracker."""
    return ProgressTracker(callback=callback)
