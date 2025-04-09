import functools

import httpx
import jwt
from fastapi import FastAPI, Request, HTTPException, status, Depends
from api_gateway.config import USER_SERVICE_URL, get_public_key, get_algorithms, setup_user_service_data
from starlette.responses import JSONResponse
from types import SimpleNamespace
import api_gateway.grpc_client
from google.protobuf.json_format import MessageToDict
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title='Proxy API')
setup_user_service_data(app)


async def get_current_user(request: Request, public_key: str = Depends(get_public_key), algorithms: str = Depends(get_algorithms)):
    if not public_key or not algorithms:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    token = request.cookies.get("user_access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')

    if not isinstance(algorithms, list):
        algorithms = [algorithms]

    try:
        payload = jwt.decode(token, public_key, algorithms=algorithms)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user_id


def handle_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Request error: {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return wrapper


async def process_request(method, *args):
    response = await method(*args)

    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
        proxy_response = JSONResponse(content=response.json(), status_code=response.status_code)
        for cookie in response.cookies.items():
            proxy_response.set_cookie(*cookie)
        return proxy_response
    else:
        return JSONResponse(
            content=MessageToDict(response, preserving_proto_field_name=True),
            status_code=200
        )


@app.post("/post")
@handle_errors
async def create_post_e(request: Request, user_id: str = Depends(get_current_user)):
    data = await request.json()
    return await process_request(
        api_gateway.grpc_client.create_post,
        SimpleNamespace(**data), user_id
    )


@app.put("/post/{post_id}")
@handle_errors
async def update_post_e(post_id: int, request: Request, user_id: str = Depends(get_current_user)):
    data = await request.json()
    return await process_request(
        api_gateway.grpc_client.update_post,
        post_id, SimpleNamespace(**data), user_id
    )


@app.delete("/post/{post_id}")
@handle_errors
async def delete_post_e(post_id: int, user_id: str = Depends(get_current_user)):
    return await process_request(
        api_gateway.grpc_client.delete_post,
        post_id, user_id
    )


@app.get("/post/{post_id}")
@handle_errors
async def delete_post_e(post_id: int, user_id: str = Depends(get_current_user)):
    return await process_request(
        api_gateway.grpc_client.get_post,
        post_id, user_id
    )


@app.get("/post")
@handle_errors
async def list_posts_e(page: int = 1, limit: int = 10, user_id: str = Depends(get_current_user)):
    return await process_request(
        api_gateway.grpc_client.list_posts,
        page, limit, user_id
    )


@app.get("/user/{path:path}")
@app.post("/user/{path:path}")
@app.put("/user/{path:path}")
@handle_errors
async def proxy(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        for cookie in request.cookies.items():
            client.cookies.set(*cookie)

        async def do_request():
            return await client.request(
                method=request.method,
                url=f"{USER_SERVICE_URL}/{path}",
                headers=request.headers,
                params=request.query_params,
                content=await request.body()
            )

        return await process_request(do_request)
