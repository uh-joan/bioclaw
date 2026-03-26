"""Smart progress tracking for target landscape analysis.

Based on execution flow analysis:
- Init/target resolution: ~5% (Open Targets search)
- Druggability: ~2% (Open Targets details)
- Genetic validation: ~5% (Open Targets associations)
- Drug discovery: ~5% (DrugBank search)
- Drug details: ~5% (DrugBank details batch)
- Clinical trials: ~30% (CT.gov - THE BOTTLENECK, 20 drugs @ 10 trials each)
- Regulatory status: ~2% (FDA/EMA lookups - Phase 2)
- Company analysis: ~1% (aggregation - Phase 2)
- Safety analysis: ~2% (FDA FAERS - Phase 3)
- Patent analysis: ~1% (Orange Book - Phase 4)
- Landscape building: ~14% (aggregation + visualization)

Note: Clinical trials dominate execution time (~30%) when searching for many drugs.
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights."""

    # Weights based on actual execution flow
    # Phase 1 only (base): 67%
    # Phase 2 adds: 3%
    # Phase 3 adds: 2%
    # Phase 4 adds: 1%
    # Plus landscape/viz: 14%
    STEP_WEIGHTS = {
        'init': 5,
        'druggability': 2,
        'genetic': 5,
        'drug_discovery': 5,
        'drug_details': 5,
        'clinical_trials': 30,  # THE BOTTLENECK
        'regulatory': 2,  # Phase 2
        'company': 1,     # Phase 2
        'safety': 2,      # Phase 3
        'patent': 1,      # Phase 4
        'landscape': 14,  # Aggregation + visualization
    }

    # Cumulative start percentages
    STEP_STARTS = {
        'init': 0,
        'druggability': 5,
        'genetic': 7,
        'drug_discovery': 12,
        'drug_details': 17,
        'clinical_trials': 22,
        'regulatory': 52,
        'company': 54,
        'safety': 55,
        'patent': 57,
        'landscape': 58,
    }

    def __init__(self, callback=None, skip_phases=None):
        """Initialize progress tracker.

        Args:
            callback: Function to call with (percent, message) updates
            skip_phases: List of phases to skip (e.g., ['phase2', 'phase3', 'phase4'])
        """
        self.callback = callback
        self.current_step = 'init'
        self.step_progress = 0.0
        self.skip_phases = skip_phases or []

        # Adjust weights if skipping phases
        if skip_phases:
            self.step_weights = self.STEP_WEIGHTS.copy()
            self.step_starts = self.STEP_STARTS.copy()

            total_skipped = 0
            if 'phase2' in skip_phases:
                total_skipped += self.step_weights.pop('regulatory', 0)
                total_skipped += self.step_weights.pop('company', 0)
            if 'phase3' in skip_phases:
                total_skipped += self.step_weights.pop('safety', 0)
            if 'phase4' in skip_phases:
                total_skipped += self.step_weights.pop('patent', 0)

            # Redistribute skipped weight to clinical trials (main bottleneck)
            if total_skipped > 0:
                self.step_weights['clinical_trials'] += total_skipped

            # Recalculate cumulative starts
            cumulative = 0
            step_order = ['init', 'druggability', 'genetic', 'drug_discovery',
                         'drug_details', 'clinical_trials', 'regulatory', 'company',
                         'safety', 'patent', 'landscape']
            for step in step_order:
                if step in self.step_weights:
                    self.step_starts[step] = cumulative
                    cumulative += self.step_weights[step]
        else:
            self.step_weights = self.STEP_WEIGHTS
            self.step_starts = self.STEP_STARTS

    def _calculate_percent(self) -> int:
        """Calculate current overall percentage."""
        base = self.step_starts.get(self.current_step, 0)
        step_weight = self.step_weights.get(self.current_step, 0)
        step_contribution = step_weight * self.step_progress
        return min(100, int(base + step_contribution))

    def report(self, message: str):
        """Report current progress with a message."""
        if self.callback:
            pct = self._calculate_percent()
            self.callback(pct, message)

    def start_step(self, step: str, message: str = None):
        """Start a new step in the pipeline.

        Args:
            step: Step name (must be in STEP_WEIGHTS)
            message: Optional message to report
        """
        self.current_step = step
        self.step_progress = 0.0
        if message:
            self.report(message)

    def update_step_progress(self, progress: float, message: str = None):
        """Update progress within current step.

        Args:
            progress: Progress within step (0.0 to 1.0)
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


def create_progress_tracker(callback=None, skip_phases=None) -> ProgressTracker:
    """Factory function to create a progress tracker.

    Args:
        callback: Function to call with (percent, message) updates
        skip_phases: List of phases to skip

    Returns:
        ProgressTracker instance
    """
    return ProgressTracker(callback=callback, skip_phases=skip_phases)
