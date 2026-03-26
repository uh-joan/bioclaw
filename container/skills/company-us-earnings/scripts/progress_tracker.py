"""Smart progress tracking for company US earnings extraction.

Based on actual timing distribution (measured from production runs):
- CIK lookup: ~2% of total time
- Stock valuation fetch: ~4% (Yahoo Finance API)
- Analyst estimates fetch: ~2% (Yahoo Finance API)
- Peer comparison fetch: ~31% (Yahoo Finance API - SLOW!)
- Filing retrieval: ~3%
- XBRL parsing: ~52% (downloads and parsing - THE BOTTLENECK)
- Reconciliation: ~3%
- Formatting: ~3%

Note: Peer comparison is surprisingly slow, taking nearly 1/3 of execution time.
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights.

    Instead of arbitrary percentages, this uses measured time weights
    to report progress that matches the user's actual wait experience.
    """

    # Weight distribution based on typical execution times
    # These weights represent approximate % of total job time
    STEP_WEIGHTS = {
        'init': 2,              # 2%: CIK lookup
        'valuation': 4,         # 4%: Stock valuation from Yahoo Finance
        'estimates': 2,         # 2%: Analyst estimates from Yahoo Finance
        'peers': 31,            # 31%: Peer comparison from Yahoo Finance (SLOW!)
        'filings': 3,           # 3%: Get filing list from SEC
        'xbrl_parsing': 52,     # 52%: Download and parse XBRL files (THE BOTTLENECK)
        'reconciliation': 3,    # 3%: Calculate reconciliation
        'formatting': 3,        # 3%: Format output
    }

    # Cumulative start percentages for each step
    STEP_STARTS = {
        'init': 0,
        'valuation': 2,
        'estimates': 6,
        'peers': 8,
        'filings': 39,
        'xbrl_parsing': 42,
        'reconciliation': 94,
        'formatting': 97,
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
        """Start a new step in the pipeline.

        Args:
            step: Step name (init, valuation, estimates, peers, filings,
                  xbrl_parsing, reconciliation, formatting)
            message: Optional message to report
        """
        self.current_step = step
        self.step_progress = 0.0
        if message:
            self.report(message)

    def update_step(self, progress: float, message: str = None):
        """Update progress within the current step.

        Args:
            progress: Progress within this step (0.0 to 1.0)
            message: Optional message to report
        """
        self.step_progress = min(1.0, max(0.0, progress))
        if message:
            self.report(message)

    def complete_step(self, message: str = None):
        """Mark current step as complete."""
        self.step_progress = 1.0
        if message:
            self.report(message)

    # Convenience methods for common progress patterns

    def report_filing_progress(self, processed: int, total: int):
        """Report progress during XBRL file processing.

        Args:
            processed: Number of filings processed so far
            total: Total filings to process
        """
        if total > 0:
            self.step_progress = processed / total
        self.report(f"Processing XBRL filings: {processed}/{total}")


def create_progress_tracker(callback=None) -> ProgressTracker:
    """Factory function to create a progress tracker.

    Args:
        callback: Optional callback(percent, message) for progress updates

    Returns:
        Configured ProgressTracker instance
    """
    return ProgressTracker(callback=callback)
