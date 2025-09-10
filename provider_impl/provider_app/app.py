from fastapi import FastAPI, Depends, status
from fastapi.routing import APIRouter
from provider_app.auth import verify_token
import uvicorn



app_router = APIRouter()


@app_router.get("/hello",dependencies=[Depends(verify_token)],
         responses={status.HTTP_200_OK:{"description": "200 OK"},
                    status.HTTP_401_UNAUTHORIZED: {
                            "description": "Unauthorized - Invalid or missing token",
                            "content": {
                                "application/json": {
                                    "example": {"detail": "Unauthorized"}
                                }
                            },
                        }
                    },
)
async def hello():
    """
    Endpoint to return a greeting message.

    GET /hello
    Requires authentication via token verification.

    Returns:
        dict: A JSON object containing a greeting message.
            Example: {"message": "Hello, World!"}
    """
    return {"message": "Hello, World!"}

app = FastAPI(title="Provider App", version="1.0.0")
app.include_router(app_router, prefix="/provider-app/v1")

if __name__ == "__main__":
    uvicorn.run('app:app',host="127.0.0.1",port=8000, reload=True)