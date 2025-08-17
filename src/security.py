import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

SECRET = "my-secret"
ALGORITHM = "HS256"


class AccessToken(BaseModel):
    iss: str
    sub: int
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    access_token: AccessToken


def sign_jwt(user_id: int) -> JWTToken:
    now = time.time()
    print("user_id",user_id)
    print("exp:", now + (60 * 30))
    payload = {
        "iss": "curso-fastapi.com.br",
        "sub": str(user_id),
        "aud": "curso-fastapi",
        "exp": now + (60 * 60 * 24),  # 24 horas
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    print(token)
    return {"access_token": token}  # dict compatível com LoginOut


async def decode_jwt(token: str) -> JWTToken | None:
    try:
        print("token",token)
        decoded_token = jwt.decode(token, SECRET, audience="curso-fastapi", algorithms=[ALGORITHM])
        print("decoded_token",decoded_token)
        _token = JWTToken.model_validate({"access_token": decoded_token})
        print("_token",_token)
        return _token if _token.access_token.exp >= time.time() else None
    except Exception as e:
        print("JWT decode error:", e)
        return None
    

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            print("credentials",credentials)
            print("scheme",scheme)
            if not scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

            payload = await decode_jwt(credentials)
            print("payload",payload)
            if not payload:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code.")


async def get_current_user(token: Annotated[JWTToken, Depends(JWTBearer())]) -> dict[str, int]:
    return {"user_id": int(token.access_token.sub)}


def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user