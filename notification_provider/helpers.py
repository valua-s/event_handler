from fastapi.datastructures import Headers
from fastapi import HTTPException, status


async def check_headers_and_get_user_login(headers: Headers) -> str:
    user_login = headers.get("x-user-id", None)
    if not user_login:
        for key, value in headers:
            if key.lower() == "x-user-id":
                user_login = value
    if not user_login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login not provided in header"
        )
    return user_login