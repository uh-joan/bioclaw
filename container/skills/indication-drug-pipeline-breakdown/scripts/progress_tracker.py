"""Smart progress tracking for drug pipeline analysis.

Based on actual timing measurements (from production runs):
- Init + Synonyms: ~2% of total time
- Phase discovery: ~1%
- Trial details: ~8%
- Regulatory checks: ~35%
- Visualization/approval search: ~54% (THE BOTTLENECK - DrugBank + brand lookups)

This module provides weighted progress tracking that reflects real time distribution.
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights.

    Instead of arbitrary percentages, this uses measured time weights
    to report progress that matches the user's actual wait experience.
    """

    # Weight distribution based on actual timing measurements
    # These weights represent approximate % of total job time
    STEP_WEIGHTS = {
        'init': 1,              # 1%: Initial setup
        'synonyms': 1,          # 1%: NLM synonym resolution
        'discovery': 1,         # 1%: CT.gov phase searches
        'trial_details': 8,     # 8%: Fetching trial details
        'regulatory': 35,       # 35%: FDA/EMA checks
        'visualization': 54,    # 54%: PubChem normalization + DrugBank search (THE BOTTLENECK!)
    }

    # Cumulative start percentages for each step
    STEP_STARTS = {
        'init': 0,
        'synonyms': 1,
        'discovery': 2,
        'trial_details': 3,
        'regulatory': 11,
        'visualization': 46,
    }

    def __init__(self, callback=None, skip_regulatory=False):
        """Initialize progress tracker.

        Args:
            callback: Optional callback(percent, message) for progress updates
            skip_regulatory: If True, redistributes regulatory weight to other steps
        """
        self.callback = callback
        self.skip_regulatory = skip_regulatory
        self.current_step = 'init'
        self.step_progress = 0.0

        # Recalculate weights if skipping regulatory
        if skip_regulatory:
            self._recalculate_weights_skip_regulatory()
        else:
            self.weights = self.STEP_WEIGHTS.copy()
            self.starts = self.STEP_STARTS.copy()

    def _recalculate_weights_skip_regulatory(self):
        """Redistribute weights when regulatory checks are skipped."""
        # When skipping regulatory (35%), visualization dominates even more
        # Without regulatory: trial_details=8%, visualization=54%, other=3%
        # Scaled to 100%: trial_details=12%, visualization=83%, other=5%
        self.weights = {
            'init': 2,
            'synonyms': 1,
            'discovery': 2,
            'trial_details': 12,
            'regulatory': 0,  # Skipped
            'visualization': 83,
        }
        self.starts = {
            'init': 0,
            'synonyms': 2,
            'discovery': 3,
            'trial_details': 5,
            'regulatory': 17,  # Will be skipped
            'visualization': 17,
        }

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
            step: Step name (init, synonyms, discovery, trial_details, regulatory, visualization)
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

    def report_trial_progress(self, processed: int, total: int, phase: str = None):
        """Report progress during trial detail fetching.

        Args:
            processed: Number of trials processed so far
            total: Total trials to process
            phase: Optional phase name for the message
        """
        if total > 0:
            self.step_progress = processed / total
        msg = f"Processing trials: {processed}/{total}"
        if phase:
            msg = f"Processing {phase}: {processed}/{total} trials"
        self.report(msg)

    def report_regulatory_progress(self, checked: int, total: int):
        """Report progress during regulatory checks.

        This is the slowest step, so we report every drug.

        Args:
            checked: Number of drugs checked so far
            total: Total drugs to check
        """
        if total > 0:
            self.step_progress = checked / total
        self.report(f"Checking FDA/EMA approvals: {checked}/{total} drugs")

    def report_phase_discovery(self, phase_num: int, total_phases: int = 4):
        """Report progress during phase discovery.

        Args:
            phase_num: Current phase number (1-4)
            total_phases: Total phases (default 4)
        """
        self.step_progress = phase_num / total_phases
        self.report(f"Discovering Phase {phase_num} trials...")


def create_progress_tracker(callback=None, skip_regulatory=False) -> ProgressTracker:
    """Factory function to create a progress tracker.

    Args:
        callback: Optional callback(percent, message) for progress updates
        skip_regulatory: If True, skips regulatory checks (faster)

    Returns:
        Configured ProgressTracker instance
    """
    return ProgressTracker(callback=callback, skip_regulatory=skip_regulatory)
