from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from pydantic import BaseModel
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: UUID | None = None
    tenant_id: UUID | None = None
