from typing import List
from src.campaigns.models import Campaign
from src.donations.one_time_transactions.models import OneTimeTransaction


def rank_by_donor_score_with_campaign(donations=[]):
    if donations is None or not isinstance(donations, List):
        raise Exception(
            'rank_by_donor_score_with_campaign() requires a list argument for `donations`')

    scores = {}
    for donation in donations:
        contact = donation.contact_id or donation.company_id
        if not contact or str(contact) in scores:
            continue
        campaign: Campaign = Campaign.fetch_by_id(
            id=donation.campaign_id,
            organization_id=donation.organization_id
        ) if donation.campaign_id else None
        scores[str(contact)] = {
            "score": OneTimeTransaction.donor_score(donations, contact),
            "campaign_id": campaign.id if campaign else None,
            "campaign_name": campaign.name if campaign else None
        }

    return scores
