from typing import Optional

from fastapi import HTTPException, status

from backend.app.app.models.conversation import Conversation
from backend.app.app.models.conversationmembers import ConversationMember
from backend.app.app.models.message import Message
from backend.app.app.models.portal_users import Users


class Chat:
    ACTIVE_STATUS = 1
    ADMIN_ROLE = 1
    ROLE_LABELS = {
        1: "admin",
        2: "student",
        3: "mentor",
        4: "mentor",
    }

    def __init__(self, db):
        self.db = db

    def _get_user(self, user_id: int, active_only: bool = True) -> Users:
        user = self.db.query(Users).filter(Users.user_id == user_id).first()
        if user is None or (active_only and user.status != self.ACTIVE_STATUS):
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def _get_admin(self, user_id: int) -> Users:
        user = self._get_user(user_id)
        if user.type != self.ADMIN_ROLE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can manage chat groups",
            )
        return user

    def _get_conversation(self, conversation_id: int, active_only: bool = True) -> Conversation:
        query = self.db.query(Conversation).filter(Conversation.ConversationID == conversation_id)
        if active_only:
            query = query.filter(Conversation.status == self.ACTIVE_STATUS)

        conversation = query.first()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation

    def _get_member(self,conversation_id: int,user_id: int,active_only: bool = True,) -> Optional[ConversationMember]:
        query = self.db.query(ConversationMember).filter(
            ConversationMember.ConversationID == conversation_id,ConversationMember.UserID == user_id,)
        if active_only:
            query = query.filter(ConversationMember.status == self.ACTIVE_STATUS)
        return query.first()

    def _require_group_access(self, conversation_id: int, user_id: int) -> Conversation:
        self._get_user(user_id)
        conversation = self._get_conversation(conversation_id)

        if self._get_member(conversation_id, user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this conversation",
            )

        return conversation

    def _save_member(
        self,
        conversation_id: int,
        user: Users,
        created_by: Optional[int] = None,
    ) -> ConversationMember:
        member = self._get_member(conversation_id, user.user_id, active_only=False)

        if member is None:
            member = ConversationMember(
                ConversationID=conversation_id,
                UserID=user.user_id,
                Role=self._role_name(user.type),
                status=self.ACTIVE_STATUS,
                CreatedBy=str(created_by) if created_by is not None else None,
            )
            self.db.add(member)
            return member

        member.status = self.ACTIVE_STATUS
        member.Role = self._role_name(user.type)
        if created_by is not None and member.CreatedBy is None:
            member.CreatedBy = str(created_by)
        return member

    def _role_name(self, user_type: Optional[int]) -> str:
        return self.ROLE_LABELS.get(user_type, "member")

    def _conversation_name(
        self,
        batch: int,
        requested_name: Optional[str],
        current_name: Optional[str] = None,
    ) -> str:
        return requested_name or current_name or f"Batch {batch} Group"

    def _conversation_data(self, conversation: Conversation) -> dict:
        member_count = (
            self.db.query(ConversationMember)
            .filter(
                ConversationMember.ConversationID == conversation.ConversationID,
                ConversationMember.status == self.ACTIVE_STATUS,
            )
            .count()
        )
        return {
            "conversation_id": conversation.ConversationID,
            "name": conversation.Name,
            "batch": conversation.batch,
            "is_group": conversation.IsGroup,
            "member_count": member_count,
            "created_on": conversation.CreatedOn,
            "updated_on": conversation.updatedOn,
        }

    def _group_data(self, conversation: Conversation) -> dict:
        return {
            "conversation_id": conversation.ConversationID,
            "name": conversation.Name,
            "batch": conversation.batch,
        }

    def _user_data(self, user: Users) -> dict:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "batch": user.batch,
            "user_type": user.type,
            "conversation_role": self._role_name(user.type),
        }

    def _member_data(self, user: Users, member: ConversationMember) -> dict:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "batch": user.batch,
            "user_type": user.type,
            "conversation_role": member.Role,
            "joined_at": member.JoinedAt,
        }

    def _message_data(self, message: Message, sender: Users) -> dict:
        return {
            "message_id": message.MessageID,
            "conversation_id": message.ConversationID,
            "sender_id": sender.user_id,
            "sender_name": sender.username,
            "sender_type": sender.type,
            "content": message.Content,
            "created_on": message.CreatedOn,
            "updated_on": message.updatedOn,
        }

    def is_active_member(self, conversation_id: int, user_id: int) -> bool:
        conversation = (
            self.db.query(Conversation)
            .filter(
                Conversation.ConversationID == conversation_id,
                Conversation.status == self.ACTIVE_STATUS,
            )
            .first()
        )
        if conversation is None:
            return False
        return self._get_member(conversation_id, user_id) is not None

    def create_conversation(
        self,
        conversation_name: Optional[str],
        batch: Optional[int],
        created_by: Optional[int] = None,
    ):
        if created_by is None:
            raise HTTPException(status_code=400, detail="Admin user is required")
        if batch in (None, 0):
            raise HTTPException(
                status_code=400,
                detail="A valid batch is required to create a group conversation",
            )

        admin_user = self._get_admin(created_by)
        conversation = (
            self.db.query(Conversation).filter(Conversation.batch == batch).first()
        )

        if conversation is None:
            conversation = Conversation(
                Name=self._conversation_name(batch, conversation_name),
                batch=batch,
                IsGroup=True,
                status=self.ACTIVE_STATUS,
                CreatedBy=str(admin_user.user_id),
            )
            self.db.add(conversation)
            self.db.flush()
        else:
            conversation.status = self.ACTIVE_STATUS
            conversation.IsGroup = True
            conversation.Name = self._conversation_name(
                batch,
                conversation_name,
                conversation.Name,
            )

        self._save_member(conversation.ConversationID, admin_user, admin_user.user_id)

        self.db.commit()
        self.db.refresh(conversation)
        return self._conversation_data(conversation)

    def get_user_conversations(self, requester_id: int):
        self._get_user(requester_id)

        conversations = (
            self.db.query(Conversation)
            .join(
                ConversationMember,
                ConversationMember.ConversationID == Conversation.ConversationID,
            )
            .filter(
                Conversation.status == self.ACTIVE_STATUS,
                ConversationMember.UserID == requester_id,
                ConversationMember.status == self.ACTIVE_STATUS,
            )
            .order_by(Conversation.batch.asc(), Conversation.ConversationID.asc())
            .all()
        )
        return [self._conversation_data(conversation) for conversation in conversations]

    def get_group_catalog(self, requester_id: Optional[int] = None):
        if requester_id is not None:
            self._get_admin(requester_id)

        conversations = (
            self.db.query(Conversation)
            .filter(
                Conversation.status == self.ACTIVE_STATUS,
                Conversation.IsGroup.is_(True),
            )
            .order_by(Conversation.batch.asc(), Conversation.ConversationID.asc())
            .all()
        )
        return [self._group_data(conversation) for conversation in conversations]

    def get_user_chat_context(self, requester_id: int):
        user = self._get_user(requester_id)

        conversations = (
            self.db.query(Conversation)
            .join(
                ConversationMember,
                ConversationMember.ConversationID == Conversation.ConversationID,
            )
            .filter(
                Conversation.status == self.ACTIVE_STATUS,
                ConversationMember.UserID == requester_id,
                ConversationMember.status == self.ACTIVE_STATUS,
            )
            .order_by(Conversation.batch.asc(), Conversation.ConversationID.asc())
            .all()
        )

        selected_conversation = next(
            (
                conversation
                for conversation in conversations
                if conversation.batch == user.batch
            ),
            conversations[0] if conversations else None,
        )

        return {
            "user_id": user.user_id,
            "batch": user.batch,
            "conversation_id": (
                selected_conversation.ConversationID
                if selected_conversation is not None
                else None
            ),
            "conversation_name": (
                selected_conversation.Name
                if selected_conversation is not None
                else None
            ),
        }

    def get_active_users_by_batch(
        self, batch_id: int, requester_id: Optional[int] = None
    ):
        if requester_id is not None:
            self._get_admin(requester_id)
        if batch_id in (None, 0):
            raise HTTPException(status_code=400, detail="A valid batch is required")

        users = (
            self.db.query(Users)
            .filter(
                Users.batch == batch_id,
                Users.status == self.ACTIVE_STATUS,
            )
            .order_by(Users.type.asc(), Users.username.asc())
            .all()
        )
        return [self._user_data(user) for user in users]

    def add_member_to_conversation(
        self,
        conversation_id: int,
        user_id: int,
        requester_id: Optional[int] = None,
    ):
        if requester_id is None:
            raise HTTPException(status_code=400, detail="Admin user is required")

        admin_user = self._get_admin(requester_id)
        conversation = self._get_conversation(conversation_id)
        target_user = self._get_user(user_id)

        if (
            conversation.batch not in (None, 0)
            and target_user.batch not in (None, 0)
            and target_user.batch != conversation.batch
        ):
            raise HTTPException(
                status_code=400,
                detail="User batch does not match the conversation batch",
            )

        self._save_member(conversation.ConversationID, target_user, admin_user.user_id)
        self.db.commit()

        return {
            "message": "Member added to conversation",
            "conversation_id": conversation.ConversationID,
            "user_id": target_user.user_id,
            "user": self._user_data(target_user),
        }

    def remove_member_from_conversation(
        self,
        conversation_id: int,
        user_id: int,
        requester_id: Optional[int] = None,
    ):
        if requester_id is None:
            raise HTTPException(status_code=400, detail="Admin user is required")

        self._get_admin(requester_id)
        conversation = self._get_conversation(conversation_id)
        user = self._get_user(user_id, active_only=False)
        member = self._get_member(conversation_id, user_id)

        if member is None:
            raise HTTPException(
                status_code=404,
                detail="User is not an active member of this conversation",
            )

        member.status = 0
        self.db.commit()

        return {
            "message": "Member removed from conversation",
            "conversation_id": conversation.ConversationID,
            "user_id": user.user_id,
            "user": self._user_data(user),
        }

    def get_conversation_members(self, conversation_id: int, requester_id: int):
        self._require_group_access(conversation_id, requester_id)

        members = (
            self.db.query(ConversationMember, Users)
            .join(Users, Users.user_id == ConversationMember.UserID)
            .filter(
                ConversationMember.ConversationID == conversation_id,
                ConversationMember.status == self.ACTIVE_STATUS,
                Users.status == self.ACTIVE_STATUS,
            )
            .order_by(Users.type.asc(), Users.username.asc())
            .all()
        )
        return [self._member_data(user, member) for member, user in members]

    def get_conversation_messages(self, conversation_id: int, requester_id: int):
        self._require_group_access(conversation_id, requester_id)

        messages = (
            self.db.query(Message, Users)
            .join(Users, Users.user_id == Message.SenderID)
            .filter(
                Message.ConversationID == conversation_id,
                Message.status == self.ACTIVE_STATUS,
                Users.status == self.ACTIVE_STATUS,
            )
            .order_by(Message.CreatedOn.asc(), Message.MessageID.asc())
            .all())
        
        return [self._message_data(message, sender) for message, sender in messages]

    def delete_conversation(
        self,
        conversation_id: int,
        requester_id: Optional[int] = None,
    ):
        if requester_id is None:
            raise HTTPException(status_code=400, detail="Admin user is required")

        self._get_admin(requester_id)
        conversation = self._get_conversation(conversation_id)

        if not conversation.IsGroup:
            raise HTTPException(
                status_code=400,
                detail="Only group conversations can be deleted",
            )

        group = self._group_data(conversation)

        members = (
            self.db.query(ConversationMember)
            .filter(ConversationMember.ConversationID == conversation_id)
            .all()
        )
        for member in members:
            member.status = 0

        messages = (
            self.db.query(Message)
            .filter(Message.ConversationID == conversation_id)
            .all()
        )
        for message in messages:
            message.status = 0

        conversation.status = 0
        self.db.commit()

        return {
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id,
            "group": group,
        }

    def get_realtime_context(self, conversation_id: int, requester_id: int) -> dict:
        user = self._get_user(requester_id)
        conversation = self._require_group_access(conversation_id, requester_id)
        return {
            "conversation": self._conversation_data(conversation),
            "user": self._user_data(user),
        }

    def send_message(
        self, conversation_id: int, user_id: int, message_content: Optional[str]
    ):
        message_content = (message_content or "").strip()
        if not message_content:
            raise HTTPException(status_code=400, detail="Message content cannot be empty")

        sender = self._get_user(user_id)
        self._require_group_access(conversation_id, user_id)

        message = Message(
            ConversationID=conversation_id,
            SenderID=user_id,
            Content=message_content,
            CreatedBy=user_id,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return self._message_data(message, sender)

    def list_user_conversations(self, user_id: int):
        return self.get_user_conversations(user_id)

    def add_member(self, conv_id: int, user_id: int, admin_id: int):
        return self.add_member_to_conversation(conv_id, user_id, admin_id)

    def list_members(self, conv_id: int, user_id: int):
        return self.get_conversation_members(conv_id, user_id)

    def remove_member(self, conv_id: int, user_id: int, admin_id: int):
        return self.remove_member_from_conversation(conv_id, user_id, admin_id)
