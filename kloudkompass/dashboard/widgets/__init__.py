# kloudkompass/dashboard/widgets/__init__.py
# ----------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Export all dashboard widgets for clean imports.

from kloudkompass.dashboard.widgets.attribution_footer import AttributionFooter
from kloudkompass.dashboard.widgets.cost_table import CostTable
from kloudkompass.dashboard.widgets.filter_panel import FilterPanel
from kloudkompass.dashboard.widgets.status_bar import StatusBar
from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
from kloudkompass.dashboard.widgets.export_modal import ExportModal
from kloudkompass.dashboard.widgets.cost_chart import CostChart
from kloudkompass.dashboard.widgets.resource_summary import ResourceSummary
from kloudkompass.dashboard.widgets.security_score import SecurityScoreGauge

__all__ = [
    "AttributionFooter",
    "CostTable",
    "FilterPanel",
    "StatusBar",
    "QuitConfirmModal",
    "ExportModal",
    "CostChart",
    "ResourceSummary",
    "SecurityScoreGauge",
]

