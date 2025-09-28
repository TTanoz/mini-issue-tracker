from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import auth, users, projects, issues, comments
from app.db.session import engine
from app.db.base import Base


from app.models import user as _m_user
from app.models import project as _m_project
from app.models import issue as _m_issue
from app.models import comment as _m_comment

#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    Base.metadata.create_all(bind=engine)
#    yield

app = FastAPI(title="Mini issue-tracker") #lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.routerprojectissue)
app.include_router(issues.router)
app.include_router(comments.routerissuecomment)
app.include_router(comments.router)



@app.get("/health")
def health():
    return {"status": "ok"}