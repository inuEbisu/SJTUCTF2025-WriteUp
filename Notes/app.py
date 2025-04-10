import asyncio
from contextlib import asynccontextmanager
import os
import random
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from gmssl import sm3
from gmssl.func import bytes_to_list
import base64
import uvicorn

secret = os.urandom(random.randint(10, 20))
systemuser = "tomo0"
systempwd = "penguins"
notes = {
    "GO": "GO.txt",
    "CRYCRY": "CRYCRY.txt",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(rotate_secret())
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


async def rotate_secret():
    while True:
        # Rotate secret in a short time, don't try to brute force it
        await asyncio.sleep(10)
        global secret
        # Very secure secret with random length
        secret = os.urandom(random.randint(10, 20))
        print(secret)


def b64_encode(value: str) -> str:
    encoded = base64.urlsafe_b64encode(str.encode(value, "latin1"))
    result = encoded.rstrip(b"=")
    return result.decode("latin1")


def b64_decode(value: str) -> str:
    padding = 4 - (len(value) % 4)
    value = value + ("=" * padding)
    result = base64.urlsafe_b64decode(value)
    return result.decode("latin1")


def sign_token(username: str, password: str, org: str) -> str:
    payload = f"{username}.{org}"
    params = [secret.hex(), password, payload]
    payload_to_sign = ".".join(params)
    # We proudly use Chinese national standard SM3 to sign our token
    signature = sm3.sm3_hash(bytes_to_list(payload_to_sign.encode()))
    print("Issued:", signature, "for", payload_to_sign)
    lst = [payload, signature]
    ret = ".".join([b64_encode(x) for x in lst])
    return ret


def verify_token(token: str):
    assert token.count(".") == 1
    payload, signature = token.split(".")
    payload = b64_decode(payload)
    signature = b64_decode(signature)
    params = [secret.hex(), systempwd, payload]
    payload_to_sign = ".".join(params)
    if sm3.sm3_hash(bytes_to_list(payload_to_sign.encode("latin1"))) != signature:
        raise Exception("Invalid sign, maybe expired")
    try:
        params = payload.split(".")
        username = params[0]
        org = params[-1]
        assert isinstance(username, str)
        assert isinstance(org, str)
    except Exception as e:
        raise Exception("Invalid payload")
    return {"username": username, "org": org}


@app.get("/")
async def index():
    return FileResponse("index.html")


@app.get("/source")
async def view_source():
    return FileResponse("app.py")


@app.get("/note")
async def view_note(request: Request):
    token = request.query_params.get("token")
    if not token:
        return JSONResponse(
            content={"message": "Authorization required"}, status_code=401
        )
    try:
        payload = verify_token(token)

    except Exception as e:
        return JSONResponse(
            content={"error": "Invalid Authorization", "detail": str(e)},
            status_code=401,
        )
    if payload.get("username") != systemuser:
        return JSONResponse(
            content={"error": f"Only {systemuser} can access this note"},
            status_code=401,
        )
    org = payload.get("org")
    if org not in notes:
        return JSONResponse(content={"error": "Who are u?"}, status_code=403)
    # You can't download the note directly!
    return FileResponse(notes[org])


@app.post("/login")
async def login(request: Request):
    data = await request.form()
    username: str = data.get("username")
    password: str = data.get("password")
    if not username or not password:
        return JSONResponse(
            content={"message": "Username and password required"}, status_code=400
        )
    if username == systemuser and password == systempwd:
        token = sign_token(username, password, "GO")
        return RedirectResponse(url="/note?token=" + token, status_code=302)
    else:
        return JSONResponse(
            content={"message": "Invalid username or password"}, status_code=401
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
