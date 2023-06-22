from google.ads.googleads.client import GoogleAdsClient
import _constrant

def authenticate_client(access_token):
    _constrant.credentials['access_token'] = access_token
    google_auth = GoogleAdsClient.load_from_dict(_constrant.credentials)
    return google_auth