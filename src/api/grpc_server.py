import grpc
from src.infrastructure.grpc import auth_pb2_grpc, auth_pb2
from src.infrastructure.config.logger_config import setup_logger
from src.domain.entities.user import UserCreate, UserUpdate, UserRole

logger = setup_logger(__name__)

class AuthServicer(auth_pb2_grpc.AuthNavigationServicer):
    def __init__(self, auth_service, user_service):
        self.auth_service = auth_service
        self.user_service = user_service
        logger.info("gRPC AuthServicer успешно запущен.")

    async def Login(self, request, context):
        logger.info(f"gRPC Call: Login | User: {request.login}")
        try:
            from src.domain.entities.login import LoginRequest
            login_data = LoginRequest(login=request.login, password=request.password)
            token = await self.auth_service.authenticate_user(login_data)
            return auth_pb2.TokenResponse(access_token=token.access_token, token_type=token.token_type)
        except Exception as e:
            logger.error(f"Login failed: {e}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid credentials")
            return auth_pb2.TokenResponse()

    async def ValidateToken(self, request, context):
        logger.debug("gRPC Call: ValidateToken")
        try:
            payload = await self.auth_service.validate_token(request.token)
            return auth_pb2.ValidateResponse(
                user_id=payload["user_id"],
                login=payload["sub"],
                role=payload["role"],
                is_valid=True
            )
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return auth_pb2.ValidateResponse(is_valid=False)

    async def CreateUser(self, request, context):
        logger.info(f"gRPC Call: CreateUser | Login: {request.login}")
        try:
            role_val = request.role if request.role else "user"
            user_data = UserCreate(
                login=request.login,
                password=request.password,
                role=UserRole(role_val)
            )
            user = await self.user_service.create_user(user_data)
            return auth_pb2.UserResponse(
                id=user.id,
                login=user.login,
                role=user.role.value,
                is_active=user.is_active
            )
        except Exception as e:
            logger.error(f"CreateUser failed: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserResponse()

    async def UpdateUser(self, request, context):
        logger.info(f"gRPC Call: UpdateUser | ID: {request.id}")
        try:
            update_fields = {}
            if request.role:
                update_fields["role"] = UserRole(request.role)
            if request.password:
                update_fields["password"] = request.password
            if request.HasField('is_active'):
                update_fields["is_active"] = request.is_active

            update_data = UserUpdate(**update_fields)
            user = await self.user_service.update_user(request.id, update_data)

            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return auth_pb2.UserResponse()

            return auth_pb2.UserResponse(
                id=user.id,
                login=user.login,
                role=user.role.value,
                is_active=user.is_active
            )
        except Exception as e:
            logger.error(f"UpdateUser failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserResponse()

    async def DeleteUser(self, request, context):
        logger.warning(f"gRPC Call: DeleteUser | ID: {request.id}")
        try:
            success = await self.user_service.soft_delete_user(request.id)
            return auth_pb2.DeleteResponse(result=success)
        except Exception as e:
            logger.error(f"DeleteUser failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.DeleteResponse(result=False)

    async def ListUsers(self, request, context):
        logger.info("gRPC Call: ListUsers")
        try:
            users = await self.user_service.get_all_users()
            return auth_pb2.UserListResponse(users=[
                auth_pb2.UserResponse(
                    id=u.id, login=u.login, role=u.role.value, is_active=u.is_active
                ) for u in users
            ])
        except Exception as e:
            logger.error(f"ListUsers failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserListResponse()