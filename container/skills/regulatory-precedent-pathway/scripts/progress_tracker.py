"""Smart progress tracking for regulatory precedent & pathway analysis.

Execution profile:
- Phase 1: Precedent Discovery (~30%)
  - FDA approved drug search
  - EMA authorized medicine search
  - CT.gov pivotal trial extraction
- Phase 2: Pathway Analysis (~20%)
  - US pathway determination
  - EU pathway determination
- Phase 3: Designations & Considerations (~20%)
  - Designation history check
  - Pediatric obligations
  - Companion diagnostics
- Phase 4: RWE Context (~15%)
  - Medicare/Medicaid utilization
- Phase 5: Epidemiology (~15%)
  - Prevalence data
  - Disease burden
"""


class ProgressTracker:
    """Smart progress tracker with phase-aware weights."""

    # Core analysis (Phases 1-3 always run)
    CORE_WEIGHTS = {
        'precedent_discovery': 35,
        'patent_scan': 10,
        'pathway_analysis': 22,
        'designations': 23,
        'report': 10,
    }

    # Full analysis (Phases 1-5)
    FULL_WEIGHTS = {
        'precedent_discovery': 22,
        'patent_scan': 8,
        'pathway_analysis': 14,
        'designations': 14,
        'rwe': 14,
        'epidemiology': 14,
        'report': 14,
    }

    def __init__(self, callback=None, include_rwe=False, include_epidemiology=False):
        self.callback = callback
        self.include_rwe = include_rwe
        self.include_epidemiology = include_epidemiology
        self.current_step = 'precedent_discovery'
        self.step_progress = 0.0

        if include_rwe or include_epidemiology:
            self.weights = dict(self.FULL_WEIGHTS)
            if not include_rwe:
                removed = self.weights.pop('rwe', 0)
                self.weights['report'] += removed
            if not include_epidemiology:
                removed = self.weights.pop('epidemiology', 0)
                self.weights['report'] += removed
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


def create_progress_tracker(callback=None, include_rwe=False, include_epidemiology=False) -> ProgressTracker:
    """Factory function to create a progress tracker."""
    return ProgressTracker(
        callback=callback,
        include_rwe=include_rwe,
        include_epidemiology=include_epidemiology,
    )
