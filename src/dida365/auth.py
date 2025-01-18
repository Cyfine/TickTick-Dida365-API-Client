"""Authentication module for the API client."""
import base64
from typing import Dict, Optional
from urllib.parse import urlencode
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
import threading

import httpx
from pydantic import BaseModel, Field

from .config import ApiConfig
from .exceptions import AuthenticationError
from .logger import logger

class TokenInfo(BaseModel):
    """Model for OAuth2 token information."""

    access_token: str = Field(..., description="OAuth2 access token")
    token_type: str = Field(..., description="Token type (usually 'Bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access token")
    scope: str = Field(..., description="Granted permission scopes")
    created_at: float = Field(default_factory=time.time, description="Token creation timestamp")

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired or about to expire (within 5 minutes)."""
        if not self.created_at:
            return True
        return time.time() >= (self.created_at + self.expires_in - 300)  # 5 min buffer


class OAuth2Manager:
    """Handles OAuth2 authentication flow."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        config: ApiConfig,
        redirect_uri: str = "http://localhost:8080/callback"
    ):
        """Initialize OAuth2 manager."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.config = config
        self.token: Optional[TokenInfo] = None
        self._server = None
        self._server_thread = None

    def get_authorization_url(
        self,
        scope: str = "tasks:write tasks:read",
        state: str = "state",
    ) -> str:
        """Get the authorization URL for OAuth2 flow."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
        }
        return f"{self.config.auth_url}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> TokenInfo:
        """Exchange authorization code for access token."""
        if not code:
            raise AuthenticationError("No authorization code provided")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": "tasks:write tasks:read",
        }

        encoded_data = urlencode(data)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "User-Agent": "Go-http-client/1.1",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.config.token_url,
                    content=encoded_data.encode(),
                    headers=headers,
                )

                response.raise_for_status()
                self.token = TokenInfo(**response.json())
                return self.token
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as e:
            raise AuthenticationError("Token exchange request timed out") from e
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Token exchange failed: {str(e)}") from e

    def _cleanup_server(self):
        """Clean up the local callback server."""
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
                if self._server_thread and self._server_thread.is_alive():
                    self._server_thread.join(timeout=5.0)
            except Exception as e:
                logger.debug(f"Server cleanup error: {e}")
            finally:
                self._server = None
                self._server_thread = None

    async def authenticate(
        self,
        scope: str = "tasks:write tasks:read",
        state: str = "state",
        port: int = 8080,
        timeout: float = 300.0,  # 5 minutes timeout
    ) -> TokenInfo:
        """
        Complete OAuth2 authentication flow:
        1. Get authorization URL
        2. Open browser for user approval
        3. Handle callback and exchange code for token
        """
        auth_code = None
        received_state = None
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code, received_state
                from urllib.parse import parse_qs, urlparse
                
                query = parse_qs(urlparse(self.path).query)
                if 'code' in query:
                    auth_code = query['code'][0]
                if 'state' in query:
                    received_state = query['state'][0]
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Authorization successful! You can close this window.")
                
            def log_message(self, format, *args):
                # Suppress logging
                pass
        
        try:
            # Get authorization URL
            auth_url = self.get_authorization_url(scope=scope, state=state)
            
            # Start local server
            self._server = HTTPServer(('localhost', port), CallbackHandler)
            self._server_thread = threading.Thread(target=self._server.serve_forever)
            self._server_thread.daemon = True
            self._server_thread.start()
            
            # Open browser for authorization
            logger.debug("Opening browser for authorization...")
            webbrowser.open(auth_url)
            
            # Wait for the authorization code with timeout
            start_time = time.time()
            while auth_code is None:
                if time.time() - start_time > timeout:
                    raise AuthenticationError("Authentication timed out")
                await asyncio.sleep(1)
            
            # Verify state
            if received_state != state:
                raise AuthenticationError("State mismatch in callback")
            
            # Exchange code for token
            return await self.exchange_code(auth_code)
            
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
        finally:
            self._cleanup_server()

    async def refresh_token(self, refresh_token: Optional[str] = None) -> None:
        """Refresh the access token using a refresh token."""
        if not refresh_token and not self.token:
            raise AuthenticationError("No refresh token available")
            
        refresh_token = refresh_token or self.token.refresh_token
        if not refresh_token:
            raise AuthenticationError("No refresh token available")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.config.token_url,
                    data=data,
                )
                response.raise_for_status()
                self.token = TokenInfo(**response.json())
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as e:
            raise AuthenticationError("Token refresh request timed out") from e
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}") from e


