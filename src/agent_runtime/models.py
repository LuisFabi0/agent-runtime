from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

AppointmentStatus = Literal["booked", "cancelled"]
ConversationStatus = Literal["open", "closed", "handed_off"]
Channel = Literal[
    "whatsapp", "sms", "telegram", "webchat", "facebook", "instagram", "tiktok", "other"
]
Role = Literal["user", "ai", "tool", "system", "other"]
MessageType = Literal["text", "audio", "image", "document", "video", "other"]


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(tz=UTC)


class Base(DeclarativeBase):
    pass


class Service(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, unique=True)
    duration_minutes: Mapped[int]


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String)


class Slot(Base):
    __tablename__ = "slots"
    __table_args__ = (UniqueConstraint("professional_id", "starts_at"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    professional_id: Mapped[str] = mapped_column(ForeignKey("professionals.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    professional: Mapped[Professional] = relationship()
    appointment: Mapped[Appointment | None] = relationship(back_populates="slot")


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String, unique=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    slot_id: Mapped[str] = mapped_column(ForeignKey("slots.id"), unique=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id"))
    status: Mapped[AppointmentStatus] = mapped_column(String, default="booked")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    slot: Mapped[Slot] = relationship(back_populates="appointment")
    customer: Mapped[Customer] = relationship()
    service: Mapped[Service] = relationship()


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    customer_phone: Mapped[str] = mapped_column(String)
    channel: Mapped[Channel] = mapped_column(String)
    status: Mapped[ConversationStatus] = mapped_column(String, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[Role] = mapped_column(String, default="user")
    message_type: Mapped[MessageType] = mapped_column(String, default="text")
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
