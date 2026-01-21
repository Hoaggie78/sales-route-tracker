import msal
import requests
from typing import Optional
from app.core.config import settings
import os


class OneDriveService:
    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.authority = settings.MICROSOFT_AUTHORITY
        self.scopes = settings.MICROSOFT_SCOPES
        self.redirect_uri = settings.MICROSOFT_REDIRECT_URI
        
    def get_auth_url(self, state: str = None):
        """Get the authorization URL for OAuth flow"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        auth_url = app.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.redirect_uri
        )
        return auth_url
    
    def get_token_from_code(self, code: str):
        """Exchange authorization code for access token"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        result = app.acquire_token_by_authorization_code(
            code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        if "access_token" in result:
            return result
        else:
            raise Exception(f"Failed to acquire token: {result.get('error_description')}")
    
    def refresh_token(self, refresh_token: str):
        """Refresh an expired access token"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        result = app.acquire_token_by_refresh_token(
            refresh_token,
            scopes=self.scopes
        )
        
        if "access_token" in result:
            return result
        else:
            raise Exception(f"Failed to refresh token: {result.get('error_description')}")
    
    def get_file_content(self, access_token: str, file_path: str) -> bytes:
        """Download file content from OneDrive"""
        # Search for the file first
        search_url = "https://graph.microsoft.com/v1.0/me/drive/root/search(q='{}')"
        file_name = os.path.basename(file_path)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"SEARCHING FOR FILE: {file_name}")
        # Search for file
        response = requests.get(
            search_url.format(file_name),
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"SEARCH FAILED: {response.text}")
            raise Exception(f"Failed to search for file: {response.text}")
        
        search_results = response.json()
        print(f"FOUND {len(search_results.get('value', []))} MATCHES")
        if not search_results.get("value"):
            raise Exception(f"File not found: {file_name}")
        
        # Get the first match
        file_item = search_results["value"][0]
        download_url = file_item["@microsoft.graph.downloadUrl"]
        print(f"DOWNLOADING FROM: {download_url[:50]}...")
        
        # Download file content
        file_response = requests.get(download_url)
        if file_response.status_code != 200:
            print(f"DOWNLOAD FAILED: {file_response.text}")
            raise Exception(f"Failed to download file: {file_response.text}")
        
        return file_response.content
    
    def upload_file_content(self, access_token: str, file_path: str, content: bytes):
        """Upload file content to OneDrive"""
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        
        # Construct upload URL
        if dir_path and dir_path != '/':
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{dir_path}/{file_name}:/content"
        else:
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}:/content"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream"
        }
        
        response = requests.put(upload_url, headers=headers, data=content)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to upload file: {response.text}")
        
        return response.json()
    
    def create_folder(self, access_token: str, folder_path: str):
        """Create a folder in OneDrive"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        parent_path = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        
        if parent_path and parent_path != '/':
            create_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{parent_path}:/children"
        else:
            create_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        
        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        
        response = requests.post(create_url, headers=headers, json=data)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create folder: {response.text}")
        
        return response.json()


# Global instance
onedrive_service = OneDriveService()
