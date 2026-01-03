import grpc
from concurrent import futures

from src.infrastructure.grpc import auth_pb2_grpc, auth_pb2


class AuthServicer(auth_pb2_grpc.AuthNavigationServicer):
    def __init__(self, auth_service, user_service):
        self.auth_service = auth_service
        self.user_service = user_service

    async def Login(self, request, context):
        try:
            from src.domain.entities.user import LoginRequest
            login_data = LoginRequest(login=request.login, password=request.password)
            token = await self.auth_service.authenticate_user(login_data)

            return auth_pb2.TokenResponse(
                access_token=token.access_token,
                token_type=token.token_type
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return auth_pb2.TokenResponse()

    async def ValidateToken(self, request, context):
        try:
            payload = await self.auth_service.validate_token(request.token)
            return auth_pb2.ValidateResponse(
                user_id=payload["user_id"],
                login=payload["sub"],
                role=payload["role"],
                is_valid=True
            )
        except Exception as e:
            print(f"Token validation failed: {e}")
            return auth_pb2.ValidateResponse(is_valid=False)

    async def CreateUser(self, request, context):
        from src.domain.entities.user import UserCreate
        user_data = UserCreate(login=request.login, password=request.password, role=request.role)
        user = await self.user_service.create_user(user_data)
        return auth_pb2.UserResponse(id=user.id, login=user.login)

    async def UpdateUser(self, request, context):
        from src.domain.entities.user import UserUpdate
        update_data = UserUpdate(
            role=request.role if request.role else None,
            is_active=request.is_active,
            password=request.password if request.password else None
        )
        user = await self.user_service.update_user(request.id, update_data)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return auth_pb2.UserResponse()

        return auth_pb2.UserResponse(id=user.id, login=user.login, role=user.role.value)

    async def DeleteUser(self, request, context):
        success = await self.user_service.soft_delete_user(request.id)
        return auth_pb2.DeleteResponse(result=success)

    async def ListUsers(self, request, context):
        users = await self.user_service.get_all_users()

        grpc_users = [
            auth_pb2.UserResponse(
                id=u.id,
                login=u.login,
                role=u.role.value,
                is_active=u.is_active
            ) for u in users
        ]

        return auth_pb2.UserListResponse(users=grpc_users)