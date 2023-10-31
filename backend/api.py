from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
from . import __version__ as version
from .auth import setup_auth, validated_user
from .authlocal import setup_authlocal
from .models import UserProfile, TokenUser
from .datasources import profile_info

load_dotenv()
app = FastAPI()

packagedir = Path(__file__).parent
distpath = packagedir/'dist'

@app.get('/')
@app.get('/{file}')
def frontend(request: Request, file=None):
    return FileResponse(distpath / (file or 'index.html'))

@app.get('/assets/{file}')
def static_files(request: Request, file=None, dir=None):
    return FileResponse(distpath / 'assets' / (file or 'index.html'))

@app.get('/api/version')
def apiVersion():
    return dict(
        version = version,
    )

@app.get('/api/me')
def apiMe(user: dict = Depends(validated_user)) -> UserProfile:
    return profile_info(user)

setup_auth(app)
setup_authlocal(app)

