# Wave 7.2: Analytics UI

**Current Status:** Active
**Objective:** Implement analytics dashboard features including data export, trend visualizations, and executive summaries.

## Tracked Tasks

### ANA-01: Data Export Integration
- [ ] *Ripple 1*: Add CSV export button to all dashboard views via `export_modal.py`.
- [ ] *Ripple 2*: Add Excel export support using `openpyxl` or lightweight alternative.
- [ ] *Ripple 3*: Wire export modal to pull live data from the current active view.

### ANA-02: Cost Trend Visualization
- [ ] *Ripple 1*: Create `cost_chart.py` widget with sparkline rendering for cost over time.
- [ ] *Ripple 2*: Add daily/weekly/monthly grouping toggle for cost chart data.
- [ ] *Ripple 3*: Integrate chart widget into `cost_view.py` below the data table.

### ANA-03: Resource Summary Dashboard
- [ ] *Ripple 1*: Create `resource_summary.py` widget showing resource counts per service.
- [ ] *Ripple 2*: Add count badges (EC2: 12, S3: 5, RDS: 3) to sidebar or top bar.

### ANA-04: Security Score Gauge
- [ ] *Ripple 1*: Create `security_score.py` widget with 0-100 score visualization.
- [ ] *Ripple 2*: Color-coded severity (green 80+, yellow 50-79, red 0-49).
- [ ] *Ripple 3*: Integrate into `security_view.py` header area.

### ANA-05: AI Executive Summary
- [ ] *Ripple 1*: Design prompt template for cloud posture executive summary.
- [ ] *Ripple 2*: Create summary generation function that processes current view data.
- [ ] *Ripple 3*: Add "Generate Summary" button to dashboard toolbar.