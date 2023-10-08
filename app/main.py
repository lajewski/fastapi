from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import post, user, auth, vote
from .config import settings
#imported for sqlalchemy
# from . import models
# from .database import engine, SessionLocal

# models.Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#imported for sqlalchemy

app = FastAPI()

origins = ["*"] #this determins which domains can actually access the api. IF it's a *, then all domains can access. However, for web apps, probably best to just limit access to the webapp in terms of security best practices.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")  # the decorator denoted by @ sign (determines the end of the url path to access the specific api service e.g. /prod/getSegments)
def root():
    return {"message": "Hello World"}





