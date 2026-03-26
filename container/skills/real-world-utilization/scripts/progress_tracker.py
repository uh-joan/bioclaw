"""Progress tracking for real-world utilization analysis.

Based on actual measured timing (from production runs):
- Init: ~1%
- Prescriber search: ~2%
- Spending data: instant
- Medicaid utilization: ~83% (THE BOTTLENECK - 50+ state-level queries!)
- NADAC pricing: instant
- ASP pricing: ~2%
- Drug interactions: instant
- FDA safety: ~2%
- Switching analysis: ~7%
- Visualization: ~3%

Note: Medicaid state-level queries completely dominate execution time.
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights."""

    # Weights based on actual measured execution time distribution
    # Total must equal 100
    STEP_WEIGHTS = {
        'init': 1,                  # 1%: Setup and validation
        'prescriber_search': 2,     # 2%: Medicare Part D prescriber data
        'spending_data': 0,         # 0%: Medicare spending totals (instant)
        'part_b_spending': 2,       # 2%: Medicare Part B spending (NEW)
        'medicaid_utilization': 79, # 79%: Medicaid state-level queries (THE BOTTLENECK!)
        'nadac_pricing': 0,         # 0%: NADAC pricing lookups (instant)
        'asp_pricing': 2,           # 2%: ASP Part B pricing
        'drug_interactions': 0,     # 0%: DrugBank interactions (not measured)
        'fda_safety': 2,            # 2%: FDA recalls, shortages, AE
        'switching_analysis': 7,    # 7%: Competitive switching patterns
        'visualization': 3,         # 3%: Format output
    }

    # Cumulative start percentages (calculated from weights)
    STEP_STARTS = {
        'init': 0,
        'prescriber_search': 1,
        'spending_data': 3,
        'part_b_spending': 3,
        'medicaid_utilization': 5,
        'nadac_pricing': 84,
        'asp_pricing': 84,
        'drug_interactions': 86,
        'fda_safety': 86,
        'switching_analysis': 88,
        'visualization': 95,
    }

    def __init__(self, callback=None, skip_medicaid=False):
        """Initialize progress tracker.

        Args:
            callback: Function to call with (percent, message) updates
            skip_medicaid: If True, redistributes Medicaid weight to other steps
        """
        self.callback = callback
        self.skip_medicaid = skip_medicaid
        self.current_step = 'init'
        self.step_progress = 0.0

        # Adjust weights if skipping Medicaid
        if skip_medicaid:
            self.step_weights = self.STEP_WEIGHTS.copy()
            medicaid_weight = self.step_weights.pop('medicaid_utilization', 0)
            # Redistribute Medicaid weight (83%) proportionally to remaining steps
            self.step_weights['prescriber_search'] += medicaid_weight * 0.12  # ~10%
            self.step_weights['switching_analysis'] += medicaid_weight * 0.40 # ~33%
            self.step_weights['fda_safety'] += medicaid_weight * 0.24         # ~20%
            self.step_weights['asp_pricing'] += medicaid_weight * 0.24        # ~20%

            # Recalculate start positions
            self.step_starts = {}
            cumulative = 0
            step_order = ['init', 'prescriber_search', 'spending_data', 'nadac_pricing',
                         'asp_pricing', 'drug_interactions', 'fda_safety',
                         'switching_analysis', 'visualization']
            for step in step_order:
                if step in self.step_weights:
                    self.step_starts[step] = cumulative
                    cumulative += self.step_weights.get(step, 0)
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

    def report_specialty_progress(self, processed: int, total: int):
        """Report progress on specialty analysis.

        Args:
            processed: Number of specialties processed
            total: Total specialties to process
        """
        if total > 0:
            self.step_progress = processed / total
        msg = f"Analyzing prescriber specialties: {processed}/{total}"
        self.report(msg)

    def report_state_progress(self, processed: int, total: int, data_type: str = "utilization"):
        """Report progress on state-level queries.

        Args:
            processed: Number of states processed
            total: Total states to query
            data_type: Type of data being collected
        """
        if total > 0:
            self.step_progress = processed / total
        msg = f"Collecting {data_type} data: {processed}/{total} states"
        self.report(msg)


def create_progress_tracker(callback=None, skip_medicaid=False) -> ProgressTracker:
    """Factory function to create a progress tracker.

    Args:
        callback: Function to call with (percent, message) updates
        skip_medicaid: If True, skips Medicaid data collection

    Returns:
        ProgressTracker instance
    """
    return ProgressTracker(callback=callback, skip_medicaid=skip_medicaid)
