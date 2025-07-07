import os
import json
import logging
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config.settings import settings

logger = logging.getLogger(__name__)

class GoogleDriveClient:
    """Client for uploading files to Google Drive"""
    
    # If modifying these scopes, delete the token file.
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        """Initialize Google Drive client"""
        self.service = None
        self.folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', None)
        
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        token_file = 'config/token.json'
        credentials_file = 'config/credentials.json'
        
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    logger.error(f"Google Drive credentials file not found: {credentials_file}")
                    logger.error("Please download credentials.json from Google Cloud Console and place it in config/")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("✅ Google Drive authentication successful")
        return True
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a folder in Google Drive"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
                
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            logger.info(f"Created folder '{folder_name}' with ID: {folder.get('id')}")
            return folder.get('id')
            
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return None
    
    def upload_file(self, file_path, folder_id=None, file_name=None):
        """Upload a file to Google Drive"""
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            if not file_name:
                file_name = os.path.basename(file_path)
                
            file_metadata = {'name': file_name}
            
            # Use specified folder or default folder
            target_folder = folder_id or self.folder_id
            if target_folder:
                file_metadata['parents'] = [target_folder]
            
            # Determine MIME type based on file extension
            if file_path.endswith('.json'):
                mime_type = 'application/json'
            elif file_path.endswith('.csv'):
                mime_type = 'text/csv'
            elif file_path.endswith('.html'):
                mime_type = 'text/html'
            elif file_path.endswith('.md'):
                mime_type = 'text/markdown'
            else:
                mime_type = 'text/plain'
            
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            file_id = file.get('id')
            web_link = file.get('webViewLink')
            
            logger.info(f"✅ Uploaded '{file_name}' to Google Drive")
            logger.info(f"File ID: {file_id}")
            logger.info(f"View link: {web_link}")
            
            return {
                'file_id': file_id,
                'web_link': web_link,
                'file_name': file_name
            }
            
        except Exception as e:
            logger.error(f"Error uploading file to Google Drive: {str(e)}")
            return None
    
    def make_file_public(self, file_id):
        """Make a file publicly viewable"""
        try:
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            logger.info(f"Made file {file_id} publicly viewable")
            return True
            
        except Exception as e:
            logger.error(f"Error making file public: {str(e)}")
            return False
    
    def get_folder_link(self, folder_id=None):
        """Get the web view link for a folder"""
        try:
            target_folder = folder_id or self.folder_id
            if not target_folder:
                return None
                
            folder = self.service.files().get(
                fileId=target_folder,
                fields='webViewLink'
            ).execute()
            
            return folder.get('webViewLink')
            
        except Exception as e:
            logger.error(f"Error getting folder link: {str(e)}")
            return None
