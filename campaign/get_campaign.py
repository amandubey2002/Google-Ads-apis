from flask import jsonify
from auth import authenticate_client
from _constrant import credentials
from app import app


def get_campaign(access_token):
    client = authenticate_client(access_token)
    customer_id = credentials["login_customer_id"]
    service = client.get_service('GoogleAdsService')
    
    query = """
    SELECT
    campaign.id,
    campaign.name,
    campaign.status
    FROM campaign
    ORDER BY campaign.id
    """
    stream = service.search(customer_id = customer_id , query = query)
    return stream
    