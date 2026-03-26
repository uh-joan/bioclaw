"""Smart progress tracking for company SWOT analysis.

Based on actual timing measurements (from production runs):
- Init: ~1%
- Financial data: ~5% (SEC EDGAR)
- FDA products: ~28% (FDA API - SLOW!)
- Clinical pipeline: ~31% (ClinicalTrials.gov search - THE BOTTLENECK!)
- Patent data: ~4% (Orange Book)
- EMA products: ~18% (EMA API)
- Market performance + peers: ~13% (Yahoo Finance)
- SWOT categorization: instant
- Report generation: instant

Note: Clinical pipeline and FDA checks dominate execution time (~60% combined).
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights."""

    # Weights reflect actual measured time for each phase
    # Order matches actual execution: init -> financial -> fda -> pipeline -> patent -> ema -> market -> categorize -> report
    STEP_WEIGHTS = {
        'init': 1,
        'financial': 5,
        'fda': 28,
        'pipeline': 31,
        'patent': 4,
        'ema': 18,
        'market': 13,  # Includes market perf (2%) + peer comparison (11%)
        'categorize': 0,  # Instant
        'report': 0,      # Instant
    }

    # Cumulative start percentages for each step (must match execution order!)
    STEP_STARTS = {
        'init': 0,        # 0-1%
        'financial': 1,   # 1-6%
        'fda': 6,         # 6-34%
        'pipeline': 34,   # 34-65%
        'patent': 65,     # 65-69%
        'ema': 69,        # 69-87%
        'market': 87,     # 87-100%
        'categorize': 100, # Instant
        'report': 100,     # Instant
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
