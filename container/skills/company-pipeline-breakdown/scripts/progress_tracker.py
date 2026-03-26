"""Smart progress tracking for company pipeline analysis.

Supports multiple pipeline modes:
- Drugs only (default): CT.gov drug trials + FDA/EMA checks
- Devices only: CT.gov device trials + 510k/PMA checks
- Both drugs and devices: Full analysis
- With/without marketed products lookup

Based on actual timing patterns (measured from production runs):
- Company resolution: ~2% of total time
- Drug CT.gov search: ~1%
- Drug trial details: ~12%
- Drug regulatory checks: ~80% (FDA/EMA per drug - THE BOTTLENECK!)
- Device CT.gov search: ~1%
- Device trial details: ~6%
- Device regulatory checks: ~40% (510k/PMA)
- Marketed products: ~2%
- Aggregation: ~1%

Note: Regulatory checks dominate execution time due to sequential FDA/EMA API calls per drug.
"""


class ProgressTracker:
    """Smart progress tracker with realistic time-based weights.

    Dynamically adjusts weights based on which pipeline modes are enabled:
    - include_drugs: Drug search, trial details, regulatory
    - include_devices: Device search, trial details, regulatory
    - include_marketed: Marketed products lookup
    """

    # Base weight distribution for full analysis (both drugs and devices)
    # Based on actual production timings
    FULL_WEIGHTS = {
        'init': 2,                  # 2%: Company resolution
        'drug_search': 1,           # 1%: CT.gov drug search
        'drug_trials': 12,          # 12%: Fetching drug trial details
        'drug_regulatory': 80,      # 80%: FDA/EMA checks per drug (THE BOTTLENECK!)
        'device_search': 1,         # 1%: CT.gov device search
        'device_trials': 6,         # 6%: Fetching device trial details
        'device_regulatory': 40,    # 40%: 510k/PMA checks
        'marketed': 2,              # 2%: Marketed products lookup
        'aggregation': 1,           # 1%: Building output structure
    }

    # Step order for calculating cumulative percentages
    STEP_ORDER = [
        'init',
        'drug_search', 'drug_trials', 'drug_regulatory',
        'device_search', 'device_trials', 'device_regulatory',
        'marketed',
        'aggregation',
    ]

    def __init__(self, callback=None, skip_regulatory=False, skip_financial=False,
                 include_drugs=True, include_devices=False, include_marketed=True):
        """Initialize progress tracker.

        Args:
            callback: Optional callback(percent, message) for progress updates
            skip_regulatory: If True, skips ALL regulatory checks (drugs & devices)
            skip_financial: Legacy param, ignored (no longer used)
            include_drugs: If True, includes drug pipeline steps
            include_devices: If True, includes device pipeline steps
            include_marketed: If True, includes marketed products lookup
        """
        self.callback = callback
        self.skip_regulatory = skip_regulatory
        self.include_drugs = include_drugs
        self.include_devices = include_devices
        self.include_marketed = include_marketed
        self.current_step = 'init'
        self.step_progress = 0.0

        # Calculate weights based on enabled modes
        self._recalculate_weights()

    def _recalculate_weights(self):
        """Calculate weights based on enabled pipeline modes."""
        self.weights = {}
        self.starts = {}

        # Always include init
        self.weights['init'] = self.FULL_WEIGHTS['init']

        # Add drug steps if enabled
        if self.include_drugs:
            self.weights['drug_search'] = self.FULL_WEIGHTS['drug_search']
            self.weights['drug_trials'] = self.FULL_WEIGHTS['drug_trials']
            if not self.skip_regulatory:
                self.weights['drug_regulatory'] = self.FULL_WEIGHTS['drug_regulatory']

        # Add device steps if enabled
        if self.include_devices:
            self.weights['device_search'] = self.FULL_WEIGHTS['device_search']
            self.weights['device_trials'] = self.FULL_WEIGHTS['device_trials']
            if not self.skip_regulatory:
                self.weights['device_regulatory'] = self.FULL_WEIGHTS['device_regulatory']

        # Add marketed products if enabled
        if self.include_marketed:
            self.weights['marketed'] = self.FULL_WEIGHTS['marketed']

        # Always include aggregation
        self.weights['aggregation'] = self.FULL_WEIGHTS['aggregation']

        # Normalize weights to sum to 100
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            scale = 100.0 / total_weight
            for step in self.weights:
                self.weights[step] *= scale

        # Calculate start positions
        cumulative = 0.0
        for step in self.STEP_ORDER:
            self.starts[step] = cumulative
            cumulative += self.weights.get(step, 0)

    # Legacy compatibility methods - map old step names to new ones
    def _map_legacy_step(self, step: str) -> str:
        """Map legacy step names to new step names."""
        legacy_map = {
            'search': 'drug_search',
            'trial_details': 'drug_trials',
            'regulatory': 'drug_regulatory',
            'financial': 'marketed',  # Repurposed
        }
        return legacy_map.get(step, step)

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
            step: Step name. New names:
                  init, drug_search, drug_trials, drug_regulatory,
                  device_search, device_trials, device_regulatory,
                  marketed, aggregation
                  Legacy names also supported: search, trial_details, regulatory, financial
            message: Optional message to report
        """
        # Map legacy step names for backward compatibility
        self.current_step = self._map_legacy_step(step)
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

    def report_search_progress(self, page: int, message: str = None):
        """Report progress during CT.gov search (pagination).

        Args:
            page: Current page number (1-based)
            message: Optional message
        """
        # Estimate progress - most searches complete within 3 pages
        self.step_progress = min(1.0, page / 5)
        msg = message or f"Searching CT.gov (page {page})..."
        self.report(msg)

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

        Args:
            checked: Number of drugs checked so far
            total: Total drugs to check
        """
        if total > 0:
            self.step_progress = checked / total
        self.report(f"Checking FDA/EMA approvals: {checked}/{total} drugs")

    def report_aggregation_progress(self, step_name: str, progress: float = 0.5):
        """Report progress during aggregation phase.

        Args:
            step_name: Name of current aggregation step
            progress: Progress within aggregation (0.0 to 1.0)
        """
        self.step_progress = progress
        self.report(f"Building output: {step_name}")


def create_progress_tracker(
    callback=None,
    skip_regulatory=False,
    skip_financial=False,  # Legacy, ignored
    include_drugs=True,
    include_devices=False,
    include_marketed=True,
) -> ProgressTracker:
    """Factory function to create a progress tracker.

    Args:
        callback: Optional callback(percent, message) for progress updates
        skip_regulatory: If True, skips ALL regulatory checks (drugs & devices)
        skip_financial: Legacy param, ignored
        include_drugs: If True, includes drug pipeline steps
        include_devices: If True, includes device pipeline steps
        include_marketed: If True, includes marketed products lookup

    Returns:
        Configured ProgressTracker instance
    """
    return ProgressTracker(
        callback=callback,
        skip_regulatory=skip_regulatory,
        include_drugs=include_drugs,
        include_devices=include_devices,
        include_marketed=include_marketed,
    )
