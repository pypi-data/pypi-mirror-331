import re
from datetime import datetime, timezone
from fastapi import FastAPI, status, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from maleo_core.models import BaseSchemas, BaseTransfers
from maleo_core.services.token import TokenService

class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, permissions:BaseTransfers.Parameter.RoutesPermissions = {}):
        super().__init__(app)
        self.permissions = permissions

    def _normalizer(self, path:str) -> str:
        """Path normalizer that handles common patterns"""
        path = re.sub(r'\?.*', '', path) #* Remove query parameters
        path = re.sub(r'/(?P<digit>\d+)', '/{id}', path) #* Replace numeric segments with {id}
        path = re.sub(r'/(?P<dynamic>[a-zA-Z0-9-]+)', r'/\g<dynamic>', path) #* Replace alphanumeric dynamic segments with {param}
        #* Define mapping of leading identifiers to placeholders
        patterns = {
            r'/email/[^/]+': '/email/{email}',
            r'/id-card/[^/]+': '/id-card/{id_card}',
            r'/name/[^/]+': '/name/{name}',
            r'/org-id/[^/]+': '/org-id/{org_id}',
            r'/phone-number/[^/]+': '/phone-number/{phone_number}',
            r'/username/[^/]+': '/username/{username}',
            r'/uuid/[^/]+': '/uuid/{uuid}',
        }
        #* Apply replacements based on identifiers
        for pattern, replacement in patterns.items():
            path = re.sub(pattern, replacement, path)
        return path

    def _validate_path_permissions(self, normalized_path:str) -> bool:
        """Validate if the normalized path has defined permissions.

        Args:
            normalized_path (str): Normalized request path

        Returns:
            bool: Whether path permissions are defined
        """
        return normalized_path in self.permissions

    def _validate_method_permissions(self, normalized_path:str, request_method:str) -> bool:
        """Validate if the method has permissions for the given path.

        Args:
            normalized_path (str): Normalized request path
            request_method (str): HTTP request method

        Returns:
            bool: Whether method permissions are defined
        """
        return request_method in self.permissions.get(normalized_path)

    async def _authenticate_and_authorize(self, request:Request, allowed_role_ids:list[int], call_next:RequestResponseEndpoint) -> Response:
        """Authenticate and authorize the request based on tokens.

        Args:
            request (Request): Incoming HTTP request
            allowed_role_ids (List[str]): Roles allowed to access the resource
            call_next (RequestResponseEndpoint): Next middleware or request handler

        Returns:
            Response: Processed response with optional new access token
        """
        #* Extract tokens
        refresh_token = request.cookies.get("token")
        authorization_header = request.headers.get("Authorization")

        #* Validate access token
        if authorization_header and authorization_header.startswith("Bearer "):
            access_token = authorization_header.split(" ")[1]
            access_token_payload = TokenService.decode(token=access_token)

            #* Valid, non-expired access token with correct role
            if (access_token_payload and 
                access_token_payload.exp > datetime.now(timezone.utc) and 
                access_token_payload.role_id in allowed_role_ids):
                return await call_next(request)

        #* No valid access token, check refresh token
        if not refresh_token:
            return JSONResponse(
                content=BaseSchemas.Response.Unauthorized(description="No refresh token", other="Please login again").model_dump(),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        #* Decode and validate refresh token
        refresh_token_payload = TokenService.decode(token=refresh_token)
        
        #* Invalid refresh token
        if not refresh_token_payload:
            return JSONResponse(
                content=BaseSchemas.Response.Unauthorized(description="Invalid refresh token", other="Please login again").model_dump(),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        #* Expired refresh token
        if refresh_token_payload.exp <= datetime.now(timezone.utc):
            return JSONResponse(
                content=BaseSchemas.Response.Unauthorized(description="Expired refresh token", other="Please login again").model_dump(),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        #* Check role permissions for refresh token
        if refresh_token_payload.role_id not in allowed_role_ids:
            return JSONResponse(
                content=BaseSchemas.Response.Forbidden(description="You are forbidden from requesting this resource").model_dump(),
                status_code=status.HTTP_403_FORBIDDEN
            )

        #* Generate new access token and process request
        response = await call_next(request)
        new_access_token = TokenService.encode(
            BaseTransfers.Payload.Token(
                id=refresh_token_payload.id,
                uuid=refresh_token_payload.uuid,
                role_id=refresh_token_payload.role_id,
                scope="access"
            )
        )
        response.headers["Authorization"] = f"Bearer {new_access_token}"

        return response

    async def dispatch(self, request:Request, call_next:RequestResponseEndpoint):
        """Middleware to handle request authorization and permission checking.

        Args:
            request (Request): Incoming HTTP request
            call_next (RequestResponseEndpoint): Next middleware or request handler

        Returns:
            Response: Processed response with optional new access token
        """

        #* Normalize and validate path
        normalized_path = self._normalizer(request.url.path)

        #* Check path permissions
        if not self._validate_path_permissions(normalized_path):
            return JSONResponse(
                content=BaseSchemas.Response.Forbidden(description="Permission for this route is not yet set").model_dump(),
                status_code=status.HTTP_403_FORBIDDEN
            )

        #* Check method permissions
        request_method = request.method
        if not self._validate_method_permissions(normalized_path, request_method):
            return JSONResponse(
                content=BaseSchemas.Response.Forbidden(description="Permission for this route and request method is not yet set").model_dump(),
                status_code=status.HTTP_403_FORBIDDEN
            )

        #* Get allowed role IDs
        allowed_role_ids = self.permissions[normalized_path][request_method]

        #* Public route handling
        if allowed_role_ids == "*":
            return await call_next(request)

        #* Authenticate and authorize request
        response = await self._authenticate_and_authorize(
            request,
            allowed_role_ids,
            call_next
        )

        return response

def add_authorization_middleware(app:FastAPI, permissions:BaseTransfers.Parameter.RoutesPermissions = {}):
    app.add_middleware(AuthorizationMiddleware, permissions)