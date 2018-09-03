from facebook_business.adobjects.adaccount import AdAccount as fbAdAccount
from facebook_business.adobjects.campaign import Campaign as fbAdCampaign
from facebook_business.adobjects.adset import AdSet as fbAdSet
from facebook_business.adobjects.ad import Ad as fbAd
from facebook_business.adobjects.adsinsights import AdsInsights as fbAdsInsights

"""
TODO
If create user wizard, moved to db?
"""

# Fields For FB AdAccount
fb_ad_account_fields = frozenset([
    fbAdAccount.Field.id,
    fbAdAccount.Field.account_id,
    fbAdAccount.Field.name,

    # additional info
    fbAdAccount.Field.amount_spent,
    fbAdAccount.Field.balance,
    fbAdAccount.Field.timezone_offset_hours_utc,
    fbAdAccount.Field.account_status,

    # no in model
    # fbAdAccount.Field.owner,
    # fbAdAccount.Field.business_country_code,
])

# Fields For FB AdCampaign
fb_ad_campaign_fields = frozenset([
    fbAdCampaign.Field.id,
    fbAdCampaign.Field.account_id,
    fbAdCampaign.Field.name,

    # additional info
    fbAdCampaign.Field.budget_rebalance_flag,
    fbAdCampaign.Field.buying_type,
    fbAdCampaign.Field.spend_cap,
    fbAdCampaign.Field.can_use_spend_cap,
    fbAdCampaign.Field.configured_status,
    fbAdCampaign.Field.effective_status,
    fbAdCampaign.Field.objective,
    fbAdCampaign.Field.status,
    fbAdCampaign.Field.start_time,
    fbAdCampaign.Field.stop_time,
    fbAdCampaign.Field.created_time,
    fbAdCampaign.Field.updated_time,

    # no in model
    # fbAdCampaign.Field.adlabels,
    # fbAdCampaign.Field.brand_lift_studies,
    # fbAdCampaign.Field.can_create_brand_lift_study,
    # fbAdCampaign.Field.recommendations,
])

# Fields For FB AdSet
fb_ad_set_fields = frozenset([
    fbAdSet.Field.id,
    fbAdSet.Field.account_id,
    fbAdSet.Field.campaign_id,
    fbAdSet.Field.name,

    # additional info
    fbAdSet.Field.billing_event,
    fbAdSet.Field.budget_remaining,
    fbAdSet.Field.configured_status,
    fbAdSet.Field.daily_budget,
    fbAdSet.Field.effective_status,
    fbAdSet.Field.lifetime_budget,
    fbAdSet.Field.optimization_goal,
    fbAdSet.Field.status,
    fbAdSet.Field.bid_amount,
    # fbAdSet.Field.frequency_cap,  # remove in 2.11.1
    # fbAdSet.Field.frequency_cap_reset_period,  # remove in 2.11.1
    # fbAdSet.Field.lifetime_frequency_cap,  # remove in 2.11.1
    fbAdSet.Field.lifetime_imps,
    fbAdSet.Field.is_autobid,
    fbAdSet.Field.is_average_price_pacing,
    fbAdSet.Field.recurring_budget_semantics,
    fbAdSet.Field.rtb_flag,
    fbAdSet.Field.use_new_app_click,
    fbAdSet.Field.end_time,
    fbAdSet.Field.start_time,
    fbAdSet.Field.created_time,
    fbAdSet.Field.updated_time,

    # no in model
    # fbAdSet.Field.adset_schedule,
    # fbAdSet.Field.bid_info,
    # fbAdSet.Field.creative_sequence,
    # fbAdSet.Field.frequency_control_specs,
    # fbAdSet.Field.pacing_type,
    # fbAdSet.Field.promoted_object,
    # fbAdSet.Field.rf_prediction_id,
    # fbAdSet.Field.targeting,
    # fbAdSet.Field.time_based_ad_rotation_id_blocks,
    # fbAdSet.Field.time_based_ad_rotation_intervals,
    # fbAdSet.Field.adlabels,
    # fbAdSet.Field.instagram_actor_id,
    # fbAdSet.Field.recommendations,

    # Remove from api
    # fbAdSet.Field.attribution_window_days,
])

# Fields For FB Ad
fb_ad_fields = frozenset([
    fbAd.Field.id,
    fbAd.Field.account_id,
    fbAd.Field.campaign_id,
    fbAd.Field.adset_id,
    fbAd.Field.name,

    # additional info
    fbAd.Field.bid_amount,
    # fbAd.Field.bid_info  # hstore
    fbAd.Field.bid_type,
    fbAd.Field.configured_status,
    fbAd.Field.effective_status,
    fbAd.Field.status,
    fbAd.Field.created_time,
    fbAd.Field.updated_time,
    # fbAd.Field.filename,

    # no in model
    # fbAd.Field.conversion_specs,
])

# Fields For FB AdsInsights
fb_ads_insight_fields = frozenset([
    fbAdsInsights.Field.account_id,
    fbAdsInsights.Field.ad_id,
    fbAdsInsights.Field.adset_id,
    fbAdsInsights.Field.campaign_id,
    fbAdsInsights.Field.campaign_name,


    # additional info
    fbAdsInsights.Field.action_values,
    fbAdsInsights.Field.actions,
    fbAdsInsights.Field.buying_type,
    # fbAdsInsights.Field.call_to_action_clicks,
    fbAdsInsights.Field.canvas_avg_view_percent,
    fbAdsInsights.Field.canvas_avg_view_time,
    fbAdsInsights.Field.clicks,
    fbAdsInsights.Field.cost_per_10_sec_video_view,
    fbAdsInsights.Field.cost_per_action_type,
    fbAdsInsights.Field.cost_per_estimated_ad_recallers,
    fbAdsInsights.Field.cost_per_inline_link_click,
    fbAdsInsights.Field.cost_per_inline_post_engagement,
    # fbAdsInsights.Field.cost_per_total_action,
    fbAdsInsights.Field.cost_per_unique_action_type,
    fbAdsInsights.Field.cost_per_unique_click,
    fbAdsInsights.Field.cost_per_unique_inline_link_click,
    fbAdsInsights.Field.cpc,
    fbAdsInsights.Field.cpm,
    fbAdsInsights.Field.cpp,
    fbAdsInsights.Field.ctr,
    fbAdsInsights.Field.estimated_ad_recall_rate,
    fbAdsInsights.Field.estimated_ad_recallers,
    fbAdsInsights.Field.frequency,
    fbAdsInsights.Field.impressions,
    fbAdsInsights.Field.inline_link_click_ctr,
    fbAdsInsights.Field.inline_link_clicks,
    fbAdsInsights.Field.inline_post_engagement,
    fbAdsInsights.Field.objective,
    fbAdsInsights.Field.place_page_name,
    fbAdsInsights.Field.reach,
    fbAdsInsights.Field.relevance_score,
    # fbAdsInsights.Field.social_clicks,
    # fbAdsInsights.Field.social_impressions,
    # fbAdsInsights.Field.social_reach,
    fbAdsInsights.Field.social_spend,
    fbAdsInsights.Field.spend,
    fbAdsInsights.Field.total_action_value,
    # fbAdsInsights.Field.total_actions,
    # fbAdsInsights.Field.total_unique_actions,
    fbAdsInsights.Field.unique_actions,
    fbAdsInsights.Field.unique_clicks,
    fbAdsInsights.Field.unique_ctr,
    fbAdsInsights.Field.unique_inline_link_click_ctr,
    fbAdsInsights.Field.unique_inline_link_clicks,
    fbAdsInsights.Field.unique_link_clicks_ctr,
    # fbAdsInsights.Field.unique_social_clicks,
    fbAdsInsights.Field.video_10_sec_watched_actions,
    # fbAdsInsights.Field.video_15_sec_watched_actions,  # remove in 2.11.1
    fbAdsInsights.Field.video_30_sec_watched_actions,
    fbAdsInsights.Field.video_avg_percent_watched_actions,
    fbAdsInsights.Field.video_avg_time_watched_actions,
    fbAdsInsights.Field.video_p100_watched_actions,
    fbAdsInsights.Field.video_p25_watched_actions,
    fbAdsInsights.Field.video_p50_watched_actions,
    fbAdsInsights.Field.video_p75_watched_actions,
    fbAdsInsights.Field.video_p95_watched_actions,
    fbAdsInsights.Field.website_ctr,

    fbAdsInsights.Field.date_start,
    fbAdsInsights.Field.date_stop,

    # remove from api
    # fbAdsInsights.Field.app_store_clicks,
    # fbAdsInsights.Field.newsfeed_avg_position,
    # fbAdsInsights.Field.newsfeed_clicks,
    # fbAdsInsights.Field.newsfeed_impressions,
    # fbAdsInsights.Field.deeplink_clicks,
    # fbAdsInsights.Field.unique_impressions,
    # fbAdsInsights.Field.unique_social_impressions,
    # fbAdsInsights.Field.video_avg_pct_watched_actions,
    # fbAdsInsights.Field.video_avg_sec_watched_actions,
    # fbAdsInsights.Field.video_complete_watched_actions,
    # fbAdsInsights.Field.website_clicks,
])
