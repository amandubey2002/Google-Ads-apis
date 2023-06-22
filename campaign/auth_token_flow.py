from google_auth_oauthlib.flow import Flow

def authentication_flow():
    flow = Flow.from_client_config(
        {"web":{
            "client_id":"470857629645-371f905mblk11etraf88jhj680elndsp.apps.googleusercontent.com",
            "client_secret":"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",
            "token_uri":"https://oauth2.googleapis.com/token",
            "auth_uri":"https://accounts.google.com/o/oauth2/auth"
        }
        },
        scopes = ["openid", "https://www.googleapis.com/auth/adwords", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/content"],
        redirect_uri = "http://localhost:5000/google_auth"
        )
    return flow