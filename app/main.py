from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import files_api.routers
from swagger import root_swagger

app = FastAPI(
    title="Test task",
    description="This is a sample API",
    version="1.0.0",
    contact={
        "name": "Kolyadich Mark",
        "email": "...",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5500', 'http://127.0.0.1:5500'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', responses=root_swagger()
         )
async def root():
    return {"message": "This is root url"}

app.include_router(files_api.routers.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
