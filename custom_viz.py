from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import hashlib
import inspect
import logging
import traceback
import uuid
import zlib

from collections import defaultdict
from itertools import product
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from flask import request
from flask_babel import lazy_gettext as _
from markdown import markdown
import simplejson as json
from six import string_types, PY3
from dateutil import relativedelta as rdelta

from superset import app, utils, cache, get_manifest_file
from superset.utils import DTTM_ALIAS, merge_extra_filters

config = app.config
stats_logger = config.get('STATS_LOGGER')
from flask_babel import lazy_gettext as _

from superset import viz


class TableWithSumViz(viz.BaseViz):

    """A basic html table that is sortable and searchable and Sum"""

    viz_type = "table_with_sum"
    verbose_name = _("Table With Sum View")
    credits = 'a CHiter'
    is_timeseries = False

    def should_be_timeseries(self):
        fd = self.form_data
        # TODO handle datasource-type-specific code in datasource
        conditions_met = (
            (fd.get('granularity') and fd.get('granularity') != 'all') or
            (fd.get('granularity_sqla') and fd.get('time_grain_sqla'))
        )
        if fd.get('include_time') and not conditions_met:
            raise Exception(_(
                "Pick a granularity in the Time section or "
                "uncheck 'Include Time'"))
        return fd.get('include_time')

    def query_obj(self):
        d = super(TableWithSumViz, self).query_obj()
        fd = self.form_data

        if fd.get('all_columns') and (fd.get('groupby') or fd.get('metrics')):
            raise Exception(_(
                "Choose either fields to [Group By] and [Metrics] or "
                "[Columns], not both"))

        sort_by = fd.get('timeseries_limit_metric')
        if fd.get('all_columns'):
            d['columns'] = fd.get('all_columns')
            d['groupby'] = []
            order_by_cols = fd.get('order_by_cols') or []
            d['orderby'] = [json.loads(t) for t in order_by_cols]
        elif sort_by:
            if sort_by not in d['metrics']:
                d['metrics'] += [sort_by]
            d['orderby'] = [(sort_by, not fd.get("order_desc", True))]

        d['is_timeseries'] = self.should_be_timeseries()
        return d

    def get_data(self, df):
        if not self.should_be_timeseries() and DTTM_ALIAS in df:
            del df[DTTM_ALIAS]

        return dict(
            records=df.to_dict(orient="records"),
            columns=list(df.columns),
        )

    def json_dumps(self, obj):
        if self.form_data.get('all_columns'):
            return json.dumps(obj, default=utils.json_iso_dttm_ser)
        else:
            return super(TableWithSumViz, self).json_dumps(obj)


class TableZodViz(viz.BaseViz):

    """Html table for Zod that is sortable and searchable"""

    viz_type = "table_zod"
    verbose_name = _("Table For Zodiac View")
    credits = 'a CHiter'
    is_timeseries = False

    def should_be_timeseries(self):
        fd = self.form_data
        # TODO handle datasource-type-specific code in datasource
        conditions_met = (
            (fd.get('granularity') and fd.get('granularity') != 'all') or
            (fd.get('granularity_sqla') and fd.get('time_grain_sqla'))
        )
        if fd.get('include_time') and not conditions_met:
            raise Exception(_(
                "Pick a granularity in the Time section or "
                "uncheck 'Include Time'"))
        return fd.get('include_time')

    def query_obj(self):
        d = super(TableZodViz, self).query_obj()
        fd = self.form_data

        if fd.get('all_columns') and (fd.get('groupby') or fd.get('metrics')):
            raise Exception(_(
                "Choose either fields to [Group By] and [Metrics] or "
                "[Columns], not both"))

        sort_by = fd.get('timeseries_limit_metric')
        if fd.get('all_columns'):
            d['columns'] = fd.get('all_columns')
            d['groupby'] = []
            order_by_cols = fd.get('order_by_cols') or []
            d['orderby'] = [json.loads(t) for t in order_by_cols]
        elif sort_by:
            if sort_by not in d['metrics']:
                d['metrics'] += [sort_by]
            d['orderby'] = [(sort_by, not fd.get("order_desc", True))]

        d['is_timeseries'] = self.should_be_timeseries()
        return d

    def get_data(self, df):
        if not self.should_be_timeseries() and DTTM_ALIAS in df:
            del df[DTTM_ALIAS]

        return dict(
            records=df.to_dict(orient="records"),
            columns=list(df.columns),
        )

    def json_dumps(self, obj):
        if self.form_data.get('all_columns'):
            return json.dumps(obj, default=utils.json_iso_dttm_ser)
        else:
            return super(TableZodViz, self).json_dumps(obj)


class FilterBoxWithPreFilterViz(viz.BaseViz):

    """A multi filter, multi-choice filter box to make dashboards interactive"""

    viz_type = "filter_box_with_pre_filter"
    verbose_name = _("Filters with pre filter")
    is_timeseries = False
    credits = 'a CHiter'

    def query_obj(self):
        logging.info('query_obj')
        qry = super(FilterBoxWithPreFilterViz, self).query_obj()
        groupby = self.form_data.get('groupby')
        if len(groupby) < 1 and not self.form_data.get('date_filter'):
            raise Exception(_("Pick at least one filter field"))
        qry['metrics'] = [
            self.form_data['metric']]
        return qry

    def get_data(self, df):
        qry = self.query_obj()
        filters = [g for g in self.form_data['groupby']]
        d = {}
        for flt in filters:
            qry['groupby'] = [flt]
            df = super(FilterBoxWithPreFilterViz, self).get_df(qry)
            d[flt] = [{
                'id': row[0],
                'text': row[0],
                'filter': flt,
                'metric': row[1]}
                for row in df.itertuples(index=False)
            ]
        return d

custom_viz_types = {
    o.viz_type: o for o in globals().values()
    if (
        inspect.isclass(o) and
        issubclass(o, viz.BaseViz) and
        o.viz_type not in config.get('VIZ_TYPE_BLACKLIST'))}
