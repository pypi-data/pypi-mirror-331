from pydantic import BaseModel
from typing import Optional

class SessionData(BaseModel):
    email: str
    accessToken: str
    refreshToken: str
    provider: Optional[str] = None

class LinkedSessions(BaseModel):
    main_email: str
    main_session: SessionData
    integration_session: Optional[SessionData] = None
