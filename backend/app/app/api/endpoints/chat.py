import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState

from backend.app.app.api.deps import authenticate_token_value, get_db, role_required
from backend.app.app.core.chat_socket import chat_connection_manager
from backend.app.app.crud.chat import Chat
from backend.app.app.db.session import sessionLocal
from backend.app.app.schemas.chat_schema import MessageCreate

router = APIRouter(prefix="/Chat", tags=["Chat"])

CHAT_MEMBER_ROLES = [1, 2, 3, 4]
ADMIN_ONLY_ROLES = [1]


def _get_socket_token(websocket: WebSocket) -> Optional[str]:
    header = websocket.headers.get("authorization")
    if header and header.lower().startswith("bearer "):
        return header.split(" ", 1)[1].strip()
    return websocket.query_params.get("token")


def _get_socket_payload(raw_message: str) -> dict:
    try:
        payload = json.loads(raw_message)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass
    return {"type": "message", "content": raw_message}


@router.post("/group", include_in_schema=False)
@router.get("/my-groups", include_in_schema=False)
@router.get("/groups",name="List User Chat Groups",summary="List the chat groups assigned to the current user",)
def list_user_chat_groups(db: Session = Depends(get_db),current_user=Depends(role_required(CHAT_MEMBER_ROLES)),):
    service = Chat(db)
    return service.get_user_conversations(current_user.get("user_id"))


@router.get("/my-chat-context", include_in_schema=False)
@router.get(
    "/groups/context",
    name="Get User Chat Context",
    summary="Get the current user's batch and conversation id for chat APIs",
)
def get_user_chat_context(
    db: Session = Depends(get_db),
    current_user=Depends(role_required(CHAT_MEMBER_ROLES)),
):
    service = Chat(db)
    return service.get_user_chat_context(current_user.get("user_id"))


@router.get("/groups-list", include_in_schema=False)
@router.get("/groups/catalog",name="List Chat Groups",summary="List all active chat groups with id and name",)
def list_chat_group_catalog(db: Session = Depends(get_db),
    current_user=Depends(role_required(ADMIN_ONLY_ROLES)),):
    service = Chat(db)
    return service.get_group_catalog(current_user.get("user_id"))


@router.get("/batch/{batch_id}/users", include_in_schema=False)
@router.get("/batches/{batch_id}/users", name="List Active Users By Batch",summary="List active users for a batch",)
def list_active_users_by_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(ADMIN_ONLY_ROLES)),):
    service = Chat(db)
    return service.get_active_users_by_batch(batch_id, current_user.get("user_id"))


@router.post("/create_chat", include_in_schema=False)
@router.post(
    "/groups",
    name="Create Chat Group",
    summary="Create a new chat group for a batch",)
def create_chat_group(
    conversation_name: Optional[str] = None,
    batch: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(ADMIN_ONLY_ROLES)),):
    service = Chat(db)
    return service.create_conversation(
        conversation_name=conversation_name,
        batch=batch,
        created_by=current_user.get("user_id"),)


@router.post("/add_member", include_in_schema=False)
@router.post("/groups/{conversation_id}/members",name="Add Group Member",
    summary="Add or reactivate a member in a chat group",)

async def add_group_member(
    conversation_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(ADMIN_ONLY_ROLES)),):
    service = Chat(db)
    result = service.add_member_to_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        requester_id=current_user.get("user_id"),)
    await chat_connection_manager.broadcast(
        conversation_id,
        {
            "type": "member_added",
            "conversation_id": conversation_id,
            "user": result["user"],
        },)
    return result


@router.delete("/remove_member", include_in_schema=False)
@router.delete("/groups/{conversation_id}/members/{user_id}",
    name="Remove Group Member",
    summary="Remove a member from a chat group",)

async def remove_group_member(
    conversation_id: int,user_id: int,db: Session = Depends(get_db),
    current_user=Depends(role_required(ADMIN_ONLY_ROLES)),):
    service = Chat(db)
    result = service.remove_member_from_conversation(
        conversation_id=conversation_id,user_id=user_id,
        requester_id=current_user.get("user_id"),)
    
    await chat_connection_manager.close_user_connections(
        conversation_id=conversation_id,
        user_id=user_id,
        payload={
            "type": "removed_from_group",
            "conversation_id": conversation_id,
            "user": result["user"],
        },
        close_code=status.WS_1008_POLICY_VIOLATION,)
    await chat_connection_manager.broadcast(
        conversation_id,
        {
            "type": "member_removed",
            "conversation_id": conversation_id,
            "user": result["user"],
        },)
    return result


@router.get("/{conversation_id}/members", include_in_schema=False)
@router.get(
    "/groups/{conversation_id}/members",
    name="List Group Members",
    summary="List active members in a chat group",)
def list_group_members(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(CHAT_MEMBER_ROLES)),):
    service = Chat(db)
    return service.get_conversation_members(
        conversation_id=conversation_id,
        requester_id=current_user.get("user_id"),)


@router.get("/{conversation_id}/messages", include_in_schema=False)
@router.get(
    "/groups/{conversation_id}/messages",
    name="List Group Messages",
    summary="Read the message history of a chat group",)
def list_group_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(CHAT_MEMBER_ROLES)),):
    service = Chat(db)
    return service.get_conversation_messages(
        conversation_id=conversation_id,
        requester_id=current_user.get("user_id"),)


@router.post("/{conversation_id}/messages", include_in_schema=False)
@router.post(
    "/groups/{conversation_id}/messages",
    name="Create Group Message",
    summary="Send a message to a chat group",
)
async def create_group_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(CHAT_MEMBER_ROLES)),
):
    service = Chat(db)
    message = service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id"),
        message_content=data.content,
    )
    await chat_connection_manager.broadcast(
        conversation_id,
        {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": message,
        },
    )
    return message


@router.delete("/delete_group", include_in_schema=False)
@router.delete(
    "/groups/{conversation_id}",
    name="Delete Chat Group",
    summary="Soft delete a chat group and close its websocket connections",
)
async def delete_chat_group(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(ADMIN_ONLY_ROLES)),
):
    service = Chat(db)
    result = service.delete_conversation(
        conversation_id=conversation_id,
        requester_id=current_user.get("user_id"),
    )
    await chat_connection_manager.close_conversation(
        conversation_id=conversation_id,
        payload={
            "type": "group_deleted",
            "conversation_id": conversation_id,
            "group": result["group"],
        },
        close_code=status.WS_1008_POLICY_VIOLATION,
    )
    return result


@router.websocket("/ws/{conversation_id}")
@router.websocket("/groups/{conversation_id}/ws", name="Group Chat WebSocket")
async def group_chat_websocket(websocket: WebSocket, conversation_id: int):
    token = _get_socket_token(websocket)
    if not token:
        await websocket.accept()
        await websocket.send_json({"type": "error", "detail": "Authentication token is required"})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = sessionLocal()
    service = Chat(db)
    user_context = None
    joined_conversation = False

    try:
        current_user = authenticate_token_value(token, db)
        if current_user.get("role") not in CHAT_MEMBER_ROLES:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access chat",
            )

        user_context = service.get_realtime_context(
            conversation_id=conversation_id,
            requester_id=current_user.get("user_id"),)

        await chat_connection_manager.connect(
            conversation_id,
            current_user.get("user_id"),
            websocket,)
        joined_conversation = True

        await chat_connection_manager.send_personal_message(
            websocket,
            {
                "type": "connection_established",
                "conversation": user_context["conversation"],
                "user": user_context["user"],
                "active_connections": await chat_connection_manager.connection_count(
                    conversation_id
                ),
            },
        )
        await chat_connection_manager.broadcast(
            conversation_id,
            {
                "type": "member_joined",
                "conversation_id": conversation_id,
                "user": user_context["user"],
            },
        )

        while True:
            payload = _get_socket_payload(await websocket.receive_text())
            event_type = str(payload.get("type") or payload.get("action") or "message").lower()

            if event_type == "ping":
                await chat_connection_manager.send_personal_message(websocket, {"type": "pong"})
                continue

            if event_type == "get_members":
                members = service.get_conversation_members(
                    conversation_id=conversation_id,
                    requester_id=current_user.get("user_id"),
                )
                await chat_connection_manager.send_personal_message(
                    websocket,
                    {
                        "type": "members",
                        "conversation_id": conversation_id,
                        "members": members,
                    },
                )
                continue

            if event_type in {"message", "send_message"}:
                message = service.send_message(
                    conversation_id=conversation_id,
                    user_id=current_user.get("user_id"),
                    message_content=payload.get("content"),
                )
                await chat_connection_manager.broadcast(
                    conversation_id,
                    {
                        "type": "new_message",
                        "conversation_id": conversation_id,
                        "message": message,
                    },
                )
                continue

            await chat_connection_manager.send_personal_message(
                websocket,
                {
                    "type": "error",
                    "detail": "Unsupported websocket action",
                },
            )

    except WebSocketDisconnect:
        pass
    except HTTPException as exc:
        if websocket.client_state == WebSocketState.CONNECTING:
            await websocket.accept()
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({"type": "error", "detail": str(exc.detail)})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception:
        if websocket.client_state == WebSocketState.CONNECTING:
            await websocket.accept()
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({"type": "error", "detail": "Unexpected websocket error"})
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        if joined_conversation:
            await chat_connection_manager.disconnect(conversation_id, websocket)

            if user_context and service.is_active_member(
                conversation_id, user_context["user"]["user_id"]
            ):
                await chat_connection_manager.broadcast(
                    conversation_id,
                    {
                        "type": "member_left",
                        "conversation_id": conversation_id,
                        "user": user_context["user"],
                    },)

        db.close()
