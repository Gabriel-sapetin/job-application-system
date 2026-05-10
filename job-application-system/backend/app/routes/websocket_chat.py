"""
WebSocket Real-Time Chat — JobTrack
Mounted at /ws in main.py
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.database import supabase
import jwt, os, json
from typing import Dict

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "jobtrack-secret-change-in-production")

class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, ws: WebSocket, app_id: int, uid: int):
        await ws.accept()
        self.active.setdefault(app_id, {})[uid] = ws

    def disconnect(self, app_id: int, uid: int):
        if app_id in self.active:
            self.active[app_id].pop(uid, None)
            if not self.active[app_id]: del self.active[app_id]

    async def broadcast(self, app_id: int, msg: dict, exclude: int = None):
        if app_id not in self.active: return
        dead = []
        for uid, ws in self.active[app_id].items():
            if uid == exclude: continue
            try: await ws.send_json(msg)
            except: dead.append(uid)
        for uid in dead: self.disconnect(app_id, uid)

mgr = ConnectionManager()

def verify_ws_token(token):
    try: return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except: return None

def check_participant(app_id, uid):
    r = supabase.table("applications").select("user_id, jobs(employer_id)").eq("id", app_id).execute()
    if not r.data: return False
    a = r.data[0]
    return uid in (a["user_id"], (a.get("jobs") or {}).get("employer_id"))

@router.websocket("/chat/{application_id}")
async def ws_chat(ws: WebSocket, application_id: int, token: str = Query(None)):
    if not token:
        await ws.close(code=4001); return
    payload = verify_ws_token(token)
    if not payload:
        await ws.close(code=4001); return
    uid = int(payload["sub"])
    if not check_participant(application_id, uid):
        await ws.close(code=4003); return

    await mgr.connect(ws, application_id, uid)
    await mgr.broadcast(application_id, {"type":"presence","user_id":uid,"status":"online"}, exclude=uid)

    try:
        while True:
            data = json.loads(await ws.receive_text())
            if data.get("type") == "message":
                body = data.get("body","").strip()
                if not body and not data.get("image_url"): continue
                result = supabase.table("messages").insert({
                    "application_id": application_id, "sender_id": uid,
                    "body": body, "reply_to_id": data.get("reply_to_id"),
                    "image_url": data.get("image_url"), "is_read": False,
                }).execute()
                if result.data:
                    u = supabase.table("users").select("id,name,profile_pic").eq("id",uid).execute()
                    await mgr.broadcast(application_id, {
                        "type":"new_message","message":{**result.data[0],"users":u.data[0] if u.data else {}}
                    })
            elif data.get("type") == "typing":
                await mgr.broadcast(application_id, {"type":"typing","user_id":uid}, exclude=uid)
            elif data.get("type") == "read":
                supabase.table("messages").update({"is_read":True}).eq(
                    "application_id",application_id).neq("sender_id",uid).eq("is_read",False).execute()
                await mgr.broadcast(application_id, {"type":"read_receipt","user_id":uid}, exclude=uid)
            elif data.get("type") == "reaction":
                await mgr.broadcast(application_id, {
                    "type":"reaction","message_id":data.get("message_id"),
                    "emoji":data.get("emoji"),"user_id":uid
                })
    except WebSocketDisconnect:
        mgr.disconnect(application_id, uid)
        await mgr.broadcast(application_id, {"type":"presence","user_id":uid,"status":"offline"})
    except Exception as e:
        print(f"[WS] Error: {e}")
        mgr.disconnect(application_id, uid)
