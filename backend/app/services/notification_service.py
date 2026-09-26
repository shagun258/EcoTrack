import asyncio

from sqlalchemy.orm import Session

from app.models.misc import Notification


def notify_user(db: Session, user_id: int, title: str, message: str) -> Notification:
    """Writes a notification row and, if the user has a live WebSocket
    connection (see app/api/routes/ws.py), pushes it in real time too."""
    notification = Notification(user_id=user_id, title=title, message=message)
    db.add(notification)
    db.flush()

    try:
        from app.api.routes.ws import manager

        payload = {"type": "notification", "title": title, "message": message}
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.send_to_user(user_id, payload))
    except Exception:
        # Real-time push is a nice-to-have; never let it break the request.
        pass

    return notification
