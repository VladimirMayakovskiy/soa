import httpx
from fastapi import FastAPI, Request, HTTPException, status
from config import USER_SERVICE_URL
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing import Optional

app = FastAPI(title='Proxy API')


class ProxyBody(BaseModel):
    content: Optional[dict] = None


@app.get("/{path:path}", response_model=ProxyBody)
@app.post("/{path:path}", response_model=ProxyBody)
@app.put("/{path:path}", response_model=ProxyBody)
async def proxy(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{USER_SERVICE_URL}/{path}",
                headers=dict(request.headers),
                params=dict(request.query_params),
                content=await request.body()
            )
            response.raise_for_status()
            content = response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Request error: {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return JSONResponse(content=content, status_code=response.status_code)
