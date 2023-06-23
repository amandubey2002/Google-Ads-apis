from flask import Flask,jsonify,request
from app import app
from get_campaign import get_campaign as get_camp
from acssess_token import get_authentication_url
from auth import authenticate_client
import uuid
import json
import requests
import datetime
from google.api_core import protobuf_helpers

get_authentication_url()

_DEFAULT_PAGE_SIZE = 1000
_DATE_FORMAT = "%Y%m%d"


@app.route("/get_campiagn_data")
def get_campiagn_data():
    access_token = request.json.get("access_token")
    stream = get_camp(access_token)
    campaign_data = [[{"campaign_id":batch.campaign.id,"campaign_name":batch.campaign.name,"campaign_status":batch.campaign.status}] for batch in stream]
    return jsonify({"campaign":campaign_data})

@app.route("/get_ad_group")
def get_ad_group():
    refresh_token = request.json.get("refresh_token")
    customer_id = request.json.get("customer_id")
    campaign_id = request.json.get("campaign_id")
    
    
    client = authenticate_client(refresh_token)
    service = client.get_service("GoogleAdsService")
    
    query = """
    SELECT
    campaign.id,
    campaign.name,
    campaign.status
    FROM ad_group
    """
    
    if campaign_id:
        query += f" WHERE campaign.id = {campaign_id}"
    
    search_request = client.get_type("SearchGoogleAdsRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    search_request.page_size = _DEFAULT_PAGE_SIZE
    
    result = service.search(request=search_request)
    # for row in result:
    #     print(
    #         f"Ad group with ID {row.ad_group.id} and name "
    #         f'"{row.ad_group.name}" was found in campaign with '
    #         f"ID {row.campaign.id}."
    #         f"campaign {row.campaign}"
    #     )

    campaign_data = [[{"ad_group_name":row.ad_group.id,"campaign_id":row.campaign.id,"campaign_status":row.campaign.status}] for row in result]
    return jsonify({"campaign":campaign_data})   


@app.route("/new_token")
def generate_new_access_token():
    token_endpoint = 'https://oauth2.googleapis.com/token'
    client_id = request.json.get("client_id")
    client_secret = request.json.get("client_secret")
    refresh_token = request.json.get("refresh_token")
    
    payload = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }

    response = requests.post(token_endpoint, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        new_access_token = token_data['access_token']
        return jsonify({"access_token":new_access_token})
    else:
        # Handle token refresh error
        print('Token refresh error:', response.text)
        return None
    
    
@app.route("/add_campaign")
def add_campaign():
    customer_id = request.json.get("customer_id")
    access_token = request.json.get("access_token")
    client = authenticate_client(access_token)
    campaign_budget_service = client.get_service("CampaignBudgetService")
    campaign_service = client.get_service("CampaignService")
    
    campaign_budgte_opration = client.get_type('CampaignBudgetOperation')
    campaign_budgte = campaign_budgte_opration.create
    campaign_budgte.name = f"custom ad_campaign {uuid.uuid4()}"
    campaign_budgte.delivery_method = (
        client.enums.BudgetDeliveryMethodEnum.STANDARD
        )
    campaign_budgte.amount_micros = 5000000
    
    try:
        campaign_budgte_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id = customer_id, operations = [campaign_budgte_opration]
            )
    except Exception as e:
        print(e)
        
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = f"Adding custom ad campaign {uuid.uuid4()}"
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH
    )
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.manual_cpc.enhanced_cpc_enabled = True
    campaign.campaign_budget = campaign_budgte_response.results[0].resource_name
    
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_partner_search_network = False
    
    campaign.network_settings.target_content_network = True
    
    start_time = datetime.date.today() + datetime.timedelta(days=1)
    campaign.start_date = datetime.date.strftime(start_time,_DATE_FORMAT)
    
    end_time = start_time + datetime.timedelta(weeks=4)
    campaign.end_date = datetime.date.strftime(end_time,_DATE_FORMAT)
    
    try:
        campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
    
    except Exception as e:
        print(e)
    
    return jsonify({"campaign_added sucssessfullyy":campaign_response.results[0].resource_name})


@app.route("/remove_campaign")
def remove_campaign():
    campaign_id = request.json.get("campaign_id")
    access_token = request.json.get("access_token")
    customer_id = request.json.get("customer_id")
    client = authenticate_client(access_token)
    campaign_service = client.get_service("CampaignService")
    campaign_opration = client.get_type("CampaignOperation")
    
    resourse_name = campaign_service.campaign_path(customer_id,campaign_id)
    campaign_opration.remove = resourse_name
    
    campaign_response = campaign_service.mutate_campaigns(
            customer_id = customer_id , operations = [campaign_opration]
        )
    return jsonify({"msg" :"Removed"})
    
@app.route("/update_campaign")
def update_campaign():
    campaign_id = request.json.get("campaign_id")
    access_token = request.json.get("access_token")
    customer_id = request.json.get("customer_id")
    client = authenticate_client(access_token)
    campaign_service = client.get_service("CampaignService")
    campaign_opration = client.get_type("CampaignOperation")
    campaign = campaign_opration.update
    
    campaign.resource_name = campaign_service.campaign_path(
        customer_id, campaign_id)
    
    campaign.status = client.enums.CampaignStatusEnum.ENABLED
    
    campaign.network_settings.target_search_network = False
    
    client.copy_from(campaign_opration.update_mask
                     ,protobuf_helpers.field_mask(None, campaign._pb),
                     )
    campaign_response = campaign_service.mutate_campaigns(
        customer_id = customer_id, operations = [campaign_opration]
    )
    
    return f"Updated Sucsessfullyy {campaign_response}" ,200 
    


if __name__ == "__main__":
    app.run(debug=True,port=5000)