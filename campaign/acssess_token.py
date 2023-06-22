from flask import Flask,redirect,request,session,jsonify
from auth_token_flow import authentication_flow
from app import app


@app.route("/")
def get_authentication_url():
    flow = authentication_flow()
    authentication_url , state = flow.authorization_url(
        access_type = "offline",
        prompt = "consent",
        include_granted_scopes = "true"
    )
    
    return redirect(authentication_url)

@app.route("/google_auth")
def get_access_token():
    if request.args.get("error"):
        return "Authorization Not Aproved"
    code = request.args.get("code")
    
    my_flow = authentication_flow()
    my_credentials = my_flow.fetch_token(code = code)
    acsess_token = my_credentials['access_token']
    id_token = my_credentials['id_token']
    refresh_token = my_credentials['refresh_token']
    expires_at = my_credentials['expires_at']
    scope = my_credentials['scope']
    return jsonify(my_credentials)
