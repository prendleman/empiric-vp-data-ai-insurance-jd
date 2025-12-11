"""
Microsoft Fabric Workspace Manager

Manages Fabric workspaces and items using Fabric REST API.
"""

import requests
import json
from typing import Dict, List, Optional
from msal import ConfidentialClientApplication
import os

class FabricWorkspaceManager:
    """Manages Microsoft Fabric workspaces and items."""
    
    def __init__(self, tenant_id=None, client_id=None, client_secret=None):
        """
        Initialize Fabric workspace manager.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD client ID
            client_secret: Azure AD client secret
        """
        self.tenant_id = tenant_id or os.getenv('FABRIC_TENANT_ID')
        self.client_id = client_id or os.getenv('FABRIC_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('FABRIC_CLIENT_SECRET')
        
        self.base_url = "https://api.fabric.microsoft.com/v1"
        self.access_token = None
        
        if self.tenant_id and self.client_id and self.client_secret:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Microsoft Fabric."""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        scope = ["https://analysis.windows.net/powerbi/api/.default"]
        
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority
        )
        
        result = app.acquire_token_for_client(scopes=scope)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            print("Successfully authenticated with Microsoft Fabric")
        else:
            raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
    
    def _get_headers(self):
        """Get request headers with authentication."""
        if not self.access_token:
            raise Exception("Not authenticated. Call _authenticate() first.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def list_workspaces(self):
        """List all Fabric workspaces."""
        url = f"{self.base_url}/workspaces"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_workspace(self, workspace_id: str):
        """Get workspace details."""
        url = f"{self.base_url}/workspaces/{workspace_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_workspace(self, name: str, description: str = ""):
        """Create a new Fabric workspace."""
        url = f"{self.base_url}/workspaces"
        payload = {
            "name": name,
            "description": description
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    
    def list_items(self, workspace_id: str, item_type: Optional[str] = None):
        """List items in a workspace."""
        url = f"{self.base_url}/workspaces/{workspace_id}/items"
        if item_type:
            url += f"?type={item_type}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_lakehouse(self, workspace_id: str, name: str, description: str = ""):
        """Create a Fabric Lakehouse."""
        url = f"{self.base_url}/workspaces/{workspace_id}/items"
        payload = {
            "type": "Lakehouse",
            "displayName": name,
            "description": description
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    
    def create_semantic_model(self, workspace_id: str, name: str, description: str = ""):
        """Create a Fabric semantic model."""
        url = f"{self.base_url}/workspaces/{workspace_id}/items"
        payload = {
            "type": "SemanticModel",
            "displayName": name,
            "description": description
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    
    def create_dataflow(self, workspace_id: str, name: str, description: str = ""):
        """Create a Fabric Gen2 dataflow."""
        url = f"{self.base_url}/workspaces/{workspace_id}/items"
        payload = {
            "type": "DataflowGen2",
            "displayName": name,
            "description": description
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()

