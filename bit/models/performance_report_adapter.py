from .data_adapter import DataAdapter
from .performance_report import PerformanceReport


class PerformanceReportAdapter(DataAdapter):
    model = PerformanceReport

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def campaign_id(self):
        raise NotImplementedError()

    @property
    def campaign_name(self):
        raise NotImplementedError()

    @property
    def campaign_source(self):
        raise NotImplementedError()

    @property
    def breakdowns(self):
        raise NotImplementedError()

    @property
    def clicks(self):
        raise NotImplementedError()

    @property
    def clicks_unique(self):
        raise NotImplementedError()

    @property
    def impressions(self):
        raise NotImplementedError()

    @property
    def conversions(self):
        raise NotImplementedError()

    @property
    def cost(self):
        raise NotImplementedError()

    @property
    def mobile_app_installs(self):
        raise NotImplementedError()

    @property
    def mobile_app_purchases(self):
        raise NotImplementedError()

    @property
    def cost_per_mobile_app_installs(self):
        raise NotImplementedError()

    @property
    def cost_per_mobile_app_purchases(self):
        raise NotImplementedError()

    @property
    def date(self):
        raise NotImplementedError()

    @property
    def measurements(self):
        raise NotImplementedError()

    def adapt(self):
        _date = self.date
        return PerformanceReport(
            date=_date,
            year=_date.year,
            month=_date.month,
            day=_date.day,
            name=self.name,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            campaign_source=self.campaign_source,
            breakdowns=self.breakdowns,
            clicks=self.clicks,
            clicks_unique=self.clicks_unique,
            conversions=self.conversions,
            impressions=self.impressions,
            cost=self.cost,
            mobile_app_installs=self.mobile_app_installs,
            mobile_app_purchases=self.mobile_app_purchases,
            cost_per_mobile_app_installs=self.cost_per_mobile_app_installs,
            cost_per_mobile_app_purchases=self.cost_per_mobile_app_purchases,
            measurements=self.measurements
        )
