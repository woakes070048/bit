# -*- coding: utf-8 -*-
from __future__ import absolute_import

from facebookads.adobjects.adaccount import AdAccount as fbAdAccount
from facebookads.adobjects.campaign import Campaign as fbAdCampaign
from facebookads.adobjects.adset import AdSet as fbAdSet

"""
TODO
If create user wizard, moved to db?
"""

# Fields For FB AdAccount
fb_ad_account_fields = frozenset([
    fbAdAccount.Field.name,
    fbAdAccount.Field.account_id,
    fbAdAccount.Field.amount_spent,
    fbAdAccount.Field.balance,
    fbAdAccount.Field.timezone_offset_hours_utc,
    fbAdAccount.Field.account_status,
    # fbAdAccount.Field.owner,
    # fbAdAccount.Field.business_country_code,
])

# Fields For FB AdCampaign
fb_ad_campaigns_fields = frozenset([
    fbAdCampaign.Field.id,
    fbAdCampaign.Field.account_id,
    fbAdCampaign.Field.adlabels,
    fbAdCampaign.Field.budget_rebalance_flag,
    fbAdCampaign.Field.buying_type,
    fbAdCampaign.Field.can_use_spend_cap,
    fbAdCampaign.Field.configured_status,
    fbAdCampaign.Field.created_time,
    fbAdCampaign.Field.effective_status,
    fbAdCampaign.Field.name,
    fbAdCampaign.Field.objective,
    fbAdCampaign.Field.spend_cap,
    fbAdCampaign.Field.start_time,
    fbAdCampaign.Field.status,
    fbAdCampaign.Field.stop_time,
    fbAdCampaign.Field.updated_time,
    # fbAdCampaign.Field.brand_lift_studies,
    # fbAdCampaign.Field.can_create_brand_lift_study,
    # fbAdCampaign.Field.recommendations,
])

# Fields For FB AdSet
fb_ad_set_fields = frozenset([
    fbAdSet.Field.id,
    fbAdSet.Field.adset_schedule,
    fbAdSet.Field.bid_amount,
    fbAdSet.Field.bid_info,
    fbAdSet.Field.billing_event,
    fbAdSet.Field.budget_remaining,
    fbAdSet.Field.campaign_id,
    fbAdSet.Field.configured_status,
    fbAdSet.Field.created_time,
    fbAdSet.Field.creative_sequence,
    fbAdSet.Field.daily_budget,
    fbAdSet.Field.effective_status,
    fbAdSet.Field.end_time,
    fbAdSet.Field.frequency_cap,
    fbAdSet.Field.frequency_cap_reset_period,
    fbAdSet.Field.frequency_control_specs,
    fbAdSet.Field.is_autobid,
    fbAdSet.Field.is_average_price_pacing,
    fbAdSet.Field.lifetime_budget,
    fbAdSet.Field.lifetime_frequency_cap,
    fbAdSet.Field.lifetime_imps,
    fbAdSet.Field.name,
    fbAdSet.Field.optimization_goal,
    fbAdSet.Field.pacing_type,
    fbAdSet.Field.promoted_object,
    fbAdSet.Field.recurring_budget_semantics,
    fbAdSet.Field.rf_prediction_id,
    fbAdSet.Field.rtb_flag,
    fbAdSet.Field.start_time,
    fbAdSet.Field.status,
    fbAdSet.Field.targeting,
    fbAdSet.Field.time_based_ad_rotation_id_blocks,
    fbAdSet.Field.time_based_ad_rotation_intervals,
    fbAdSet.Field.updated_time,
    fbAdSet.Field.use_new_app_click,
    # fbAdSet.Field.account_id,
    # fbAdSet.Field.adlabels,
    # fbAdSet.Field.instagram_actor_id,
    # fbAdSet.Field.recommendations,
    """Remove from api."""
    # fbAdSet.Field.attribution_window_days,
])
