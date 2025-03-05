import os
import streamlit as st

from cognite.client import CogniteClient, ClientConfig
from cognite.client.credentials import OAuthInteractive, OAuthClientCredentials
from streamlit_slb_gallery import streamlit_slb_gallery

def assign_auth(project_name):
        
    if project_name == "slb-test":        
        tenant_id = os.environ.get("CDF_SLBTEST_TENANT_ID") 
        client_id = os.environ.get("CDF_SLBTEST_CLIENT_ID") 
        client_secret = os.environ.get("CDF_SLBTEST_CLIENT_SECRET")
        cluster = os.environ.get("CDF_SLBTEST_CLUSTER")     
    elif project_name == "petronas-pma-dev" or project_name == "petronas-pma-playground":
        tenant_id = os.environ.get("CDF_PETRONASPMA_TENANT_ID") 
        cluster = os.environ.get("CDF_PETRONASPMA_CLUSTER") 
        client_id = os.environ.get("CDF_PETRONASPMA_CLIENT_ID") 
        client_secret = ""
    elif project_name == "hess-malaysia-dev":
        tenant_id = os.environ.get("CDF_HESSDEV_TENANT_ID") 
        client_id = os.environ.get("CDF_HESSDEV_CLIENT_ID") 
        client_secret = os.environ.get("CDF_HESSDEV_CLIENT_SECRET") 
        cluster = os.environ.get("CDF_HESSDEV_CLUSTER") 
    elif project_name == "hess-malaysia-prod":
        tenant_id = os.environ.get("CDF_HESSPROD_TENANT_ID") 
        client_id = os.environ.get("CDF_HESSPROD_CLIENT_ID") 
        client_secret = os.environ.get("CDF_HESSPROD_CLIENT_SECRET") 
        cluster = os.environ.get("CDF_HESSPROD_CLUSTER")     
    elif project_name == "mubadala-dev":
        tenant_id = os.environ.get("CDF_MUBADALADEV_TENANT_ID") 
        cluster = os.environ.get("CDF_MUBADALADEV_CLUSTER")
        client_id = os.environ.get("CDF_MUBADALADEV_CLIENT_ID") 
        client_secret = os.environ.get("CDF_MUBADALADEV_CLIENT_SECRET") 
           
    base_url = f"https://{cluster}.cognitedata.com"
    scopes = [f"{base_url}/.default"]
    
    return {
        "tenant_id": tenant_id, 
        "client_id": client_id, 
        "client_secret": client_secret, 
        "cluster": cluster,
        "base_url": base_url,
        "project_name": project_name,
        "scopes": scopes
    }

def interactive_client(project_name):
    
    auth_data: any = assign_auth(project_name)
    
    """Function to instantiate the CogniteClient, using the interactive auth flow"""
    return CogniteClient(
        ClientConfig(
            client_name=auth_data['project_name'],
            project=auth_data['project_name'],
            base_url=auth_data['base_url'],
            credentials=OAuthInteractive(
                authority_url=f"https://login.microsoftonline.com/{auth_data['tenant_id']}",
                client_id=auth_data['client_id'],
                scopes=auth_data['scopes'],
            ),
        )
    )

def client_credentials(project_name):
    
    auth_data = assign_auth(project_name)

    credentials = OAuthClientCredentials(
        token_url=f"https://login.microsoftonline.com/{auth_data['tenant_id']}/oauth2/v2.0/token", 
        client_id=auth_data['client_id'], 
        client_secret= auth_data['client_secret'],
        scopes=auth_data['scopes']
    )

    config = ClientConfig(
        client_name=auth_data['project_name'],
        project=auth_data['project_name'],
        base_url=auth_data['base_url'],
        credentials=credentials,
    )
    client = CogniteClient(config)

    return client

def connect(project_name):
    auth = assign_auth(project_name=project_name)  
    if auth["client_secret"] == "":
        return interactive_client(project_name)
    else:
        return client_credentials(project_name)

st.set_page_config(page_title="Streamlit Slb Gallery", layout='wide')
st.subheader("Streamlit Slb Gallery")

client: CogniteClient = connect("mubadala-dev")

cognite_token = client.iam.token

def show_main_content():
    
    st.session_state["selected_datetime_from"] = st.selectbox(key="start_date", label="Start Date", options=["2025-03-03 00:00:00","2024-07-02 06:00:00","2024-07-03 06:00:00","2024-07-04 06:00:00","2024-07-05 06:00:00", "2024-01-22 06:00:00"], )	
    st.session_state["selected_datetime_to"] = st.selectbox(key="end_date", label="End Date", options=["2025-03-04 10:00:00","2024-11-29 06:00:00","2024-07-03 06:00:00","2024-07-04 06:00:00","2024-07-05 06:00:00", "2025-01-22 06:00:00"])	
    
    st.session_state.selected_deck = st.selectbox(label="Deck", options=["Main Deck", "Upper Deck"])
    
    col_comp_1, col_comp_2 = st.columns([1,1])
    with col_comp_1:
        st.session_state["crewsafety_selected_category_status"] = st.selectbox(key="crewsafe_categoryStatus", label="Review Status", options=["All", "Reviewed"])
    with col_comp_2:
        st.session_state["crewsafety_selected_category_type"] = st.selectbox(key="crewsafe_categoryType", label="Review Category", options=["All", "Valid", "Invalid", "Not Reviewed", "Excluded"])
    
    if "selected_data" in st.session_state:
        st.write(st.session_state.selected_data)
    
    

@st.fragment()       
def show_streamlit_slb_gallery():      
    if "selected_datetime_from" in st.session_state and "selected_datetime_to" in st.session_state:
        st.session_state.selected_data = streamlit_slb_gallery(
            data={
                "height": 600, 
                "items_per_page": 10, 
                "event_start_time": st.session_state["selected_datetime_from"], 
                "event_end_time": st.session_state["selected_datetime_to"], 
                "event_type": "PPE_VIOLATION", 
                "load_delay": 2000,
                # "selected_object": {
                #     "type": "camera",
                #     "id": 2,
                #     "externalId": "AYS310",
                #     "name": "Camera 2"
                # },
                "selected_category_status": st.session_state["crewsafety_selected_category_status"],
                "selected_category_type": st.session_state["crewsafety_selected_category_type"],
                "compliance_type": "Glove",
                "limit": 1000
                },
            token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImltaTBZMnowZFlLeEJ0dEFxS19UdDVoWUJUayIsImtpZCI6ImltaTBZMnowZFlLeEJ0dEFxS19UdDVoWUJUayJ9.eyJhdWQiOiJodHRwczovL2F6LXNpbi1zcC0wMDEuY29nbml0ZWRhdGEuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNmUzMDJmZTktMTE4Ni00MjgxLTlmYjMtOTQ0ZDdiYjgyOGNjLyIsImlhdCI6MTc0MTE1MjcxNywibmJmIjoxNzQxMTUyNzE3LCJleHAiOjE3NDExNTY2MTcsImFpbyI6ImsyUmdZSkE0TmFkaDgwYlB1eXJGbGVXWjd0dmJBQT09IiwiYXBwaWQiOiIzM2ZiY2NjYS0xZjEzLTQzMzktOWQ0Ni02NDE4MjJiYWRiZmUiLCJhcHBpZGFjciI6IjEiLCJncm91cHMiOlsiNDc5YTM2M2QtZGQ5Ny00ZTNjLTk5MjktMWQyOTljODk0ZmIxIiwiNGZhYzhhNWMtNjQzNC00MzQwLTgzMTQtNWRiOWQ0ZjdjNzBiIl0sImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzZlMzAyZmU5LTExODYtNDI4MS05ZmIzLTk0NGQ3YmI4MjhjYy8iLCJvaWQiOiI1OGYzZjk5ZS1kZWUxLTQ4YmEtODYyMS00ZThkNzMzZmU4NzUiLCJyaCI6IjEuQWNZQTZTOHdib1lSZ1VLZnM1Uk5lN2dvekVMc1hQNlk0cWhPcWZkVmZLbTFVYTdHQUFER0FBLiIsInN1YiI6IjU4ZjNmOTllLWRlZTEtNDhiYS04NjIxLTRlOGQ3MzNmZTg3NSIsInRpZCI6IjZlMzAyZmU5LTExODYtNDI4MS05ZmIzLTk0NGQ3YmI4MjhjYyIsInV0aSI6InRPN2RzbG0wa1VHVUxzSW9lcGswQUEiLCJ2ZXIiOiIxLjAifQ.pzca64ss-2Uwzp6tt7wOlue5U4OQSolJPLfkU7FrnN8PZi00eKchBwRwEfhDZXM6mqccuXAtcIuC3_yGahLrTvqMIzgc5Dh3HDHJDfhvtUMj34Anqhq3CqR-WRULTv3NRGUJDDhGNKT6v4SIl8T1fetPI1XHHWCOgcriPdCW1gqri6HJNoLeMcdOjwPZcYzTuhzoSdeqb2uGLtCB7GO9UpIlIjUuqy0m2fe2X2jWKV7P_S55cRl-24y3bqFZdQst5HHSAfpJfDLvYQhKeTbuBm9x9txV-BgkTSCuUDVx8d1Q8cmtZCl5enRsvyFsDOaK8qtR0wvqP7CWm6iI-qCFPw",
            key="streamlit_slb_gallery"
        )
        st.write(st.session_state.selected_data)

main_content, gallery = st.columns([1,1])

with main_content:
    show_main_content()
    
with gallery:
    show_streamlit_slb_gallery()



