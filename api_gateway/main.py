import httpx
from fastapi import FastAPI, Request, HTTPException, status
from config import USER_SERVICE_URL
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing import Optional

app = FastAPI(title='Proxy API')


class ProxyBodyScheme(BaseModel):
    content: Optional[dict] = None


@app.get("/{path:path}", response_model=ProxyBodyScheme)
@app.post("/{path:path}", response_model=ProxyBodyScheme)
@app.put("/{path:path}", response_model=ProxyBodyScheme)
async def proxy(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        try:
            for cookie in request.cookies.items():
                client.cookies.set(*cookie)

            response = await client.request(
                method=request.method,
                url=f"{USER_SERVICE_URL}/{path}",
                headers=request.headers,
                params=request.query_params,
                content=await request.body()
            )
            response.raise_for_status()
            content = response.json()

            proxy_response = JSONResponse(content=content, status_code=response.status_code)
            for cookie in response.cookies.items():
                proxy_response.set_cookie(*cookie)
            return proxy_response
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Request error: {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
