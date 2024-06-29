from fastapi import FastAPI
import uvicorn
from . import models
from .database import engine
from .router import post, user, auth, votes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='1234', port=5433, cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print('Database connection was successful !!')
#         break
#     except Exception as error:
#         print('Error :', error)
#         time.sleep(2)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}
# if __name__ == "__main__":
#     uvicorn.run('main:app', host="0.0.0.0", port=8001, reload=True)
