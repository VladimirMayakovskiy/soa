import httpx
from fastapi import FastAPI, Request
from config import USER_SERVICE_URL
from starlette.responses import JSONResponse

app = FastAPI(title='Proxy API')


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{USER_SERVICE_URL}/{path}",
            headers=request.headers,
            params=request.query_params,
            content=await request.body()
        )

        try:
            content = response.json()
        except ValueError:
            content = response.text

        return JSONResponse(content=content, status_code=response.status_code)
