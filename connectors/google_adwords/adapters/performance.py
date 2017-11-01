# local
from bit.models import PerformanceReportAdapter


class AdwordsPerformanceReportAdapter(PerformanceReportAdapter):

    def __init__(self, data, name):
        super(AdwordsPerformanceReportAdapter, self).__init__(data)
        self._name = name

    @property
    def date(self):
        # return self.string_to_date(self.data['date'])
        return self.data['date']

    @property
    def measurements(self):
        # return self.data
        return {}

    @property
    def clicks(self):
        # return self.string_to_float(self.data['clicks'])
        return self.data['clicks']

    @property
    def name(self):
        return self._name

    @property
    def impressions(self):
        # return self.string_to_float(self.data['impressions'])
        return self.data['impressions']

    @property
    def campaign_id(self):
        return self.data['campaignid']

    @property
    def cost(self):
        # return self.string_to_float(self.data['cost'])
        return self.data['cost']

    @property
    def mobile_app_installs(self):
        # return self.string_to_float(self.data['conversions'])
        return self.data['conversions']

    @property
    def mobile_app_purchases(self):
        # return self.string_to_float(self.data['impressions'])
        return self.data['impressions']

    @property
    def cost_per_mobile_app_installs(self):
        try:
            return self.cost/self.mobile_app_installs
        except:
            return 0

    @property
    def cost_per_mobile_app_purchases(self):
        return 0

    @property
    def clicks_unique(self):
        return self.clicks

    @property
    def campaign_name(self):
        return self.data['campaignname']

    @property
    def conversions(self):
        # return self.string_to_float(self.data['conversions'])
        return self.data['conversions']

    @property
    def breakdowns(self):
        raise NotImplementedError()

    @property
    def device(self):
        return self.data['device']

    @property
    def campaign_source(self):
        return "adwords"
