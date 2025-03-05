import logging
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from talentwizer_commons.utils.db import mongo_database
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

session_router = s = APIRouter()

# MongoDB Setup
collection = mongo_database["session"]
sessions = mongo_database["session"]

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema):
        return {"type": "string"}

class SessionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    mainSession: Optional[dict]
    integrationSession: Optional[dict] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SessionData(BaseModel):
    email: str
    accessToken: str
    refreshToken: str
    provider: str

class StoredSession(BaseModel):
    mainSession: Optional[SessionData] = None
    integrationSession: Optional[SessionData] = None

@s.post("/", response_model=SessionModel)
async def create_session(session: SessionModel):
    result = collection.insert_one(session.dict(by_alias=True))
    session.id = str(result.inserted_id)
    return session

class SessionData(BaseModel):
    email: str
    accessToken: str
    refreshToken: str
    provider: str

class StoredSessions(BaseModel):
    mainSession: Optional[SessionData]
    integrationSession: Optional[SessionData]

@s.put("/{email}", response_model=SessionModel)
async def update_session(email: str, session: SessionModel):
    session_dict = session.dict(by_alias=True)
    result = collection.update_one({"email": email}, {"$set": session_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@s.delete("/{email}", response_model=SessionModel)
async def delete_session(email: str):
    session = collection.find_one_and_delete({"email": email})
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@s.get("/linked/{email}")
async def get_linked_sessions(email: str):
    # First try to find as main email
    session = collection.find_one({"main_email": email})
    if session:
        return session

    # If not found, try to find as integration email
    session = collection.find_one({"integration_session.email": email})
    if session:
        return session

    raise HTTPException(status_code=404, detail="Sessions not found")

@s.post("/store/{email}")
async def store_session(email: str, session_data: StoredSession):
    try:
        logger.debug(f"Storing session for email: {email}")
        logger.debug(f"Received session data: {session_data.dict()}")

        # Ensure email is properly formatted
        email = email.replace("%40", "@")
        
        # Convert session data to dict and add email
        session_dict = session_data.dict()
        session_dict["email"] = email
        
        logger.debug(f"Formatted session dict: {session_dict}")

        # Update or insert the session
        result = collection.update_one(
            {"email": email},
            {"$set": session_dict},
            upsert=True
        )
        
        logger.debug(f"MongoDB result: {result.raw_result}")

        if result.matched_count > 0 or result.upserted_id:
            logger.debug("Session stored successfully")
            return {"status": "success", "message": "Session stored successfully"}
        else:
            logger.error("Failed to store session - no document modified or inserted")
            raise HTTPException(
                status_code=500,
                detail="Failed to store session"
            )
            
    except Exception as e:
        logger.error(f"Error storing session for {email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@s.post("/link/{email}")
async def link_session(email: str, session_data: StoredSession):
    try:
        logger.debug(f"Linking integration session for main email: {email}")
        logger.debug(f"Integration session data: {session_data.dict()}")

        # Find existing main session
        existing = collection.find_one({"email": email})
        if not existing:
            logger.error(f"No main session found for email: {email}")
            raise HTTPException(status_code=404, detail="Main session not found")

        # Store integration session with reference to main session
        result = collection.update_one(
            {"email": email},
            {
                "$set": {
                    "integrationSession": session_data.dict().get("integrationSession"),
                    "linkedAccounts": {
                        "mainEmail": email,
                        "integrationEmail": session_data.dict().get("integrationSession", {}).get("email"),
                        "linkedAt": datetime.utcnow()
                    }
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to link sessions")

        return {"status": "success", "message": "Sessions linked successfully"}

    except Exception as e:
        logger.error(f"Error linking sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@s.delete("/unlink/{email}")
async def unlink_session(email: str):
    try:
        result = collection.update_one(
            {"email": email},
            {"$unset": {"integrationSession": ""}}
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@s.get("/{email}")
async def get_session(email: str):
    try:
        session = collection.find_one({"email": email})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert ObjectId to string before creating SessionModel
        if "_id" in session:
            session["_id"] = str(session["_id"])
            
        return SessionModel(**session)
    except Exception as e:
        logger.error(f"Error retrieving session for {email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

class TokenCreateRequest(BaseModel):
    token: str
    email: str
    expiresAt: datetime

@s.post("/create-token", response_model=dict)  # Add response_model
async def create_integration_token(token_data: TokenCreateRequest):
    """Store temporary integration token."""
    try:
        logger.debug(f"Creating token for email: {token_data.email}")
        
        # Convert datetime to proper format
        expires_at = token_data.expiresAt
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))

        # First check if there are any existing tokens
        sessions.delete_many({
            "main_email": token_data.email,
            "type": "integration_token"
        })

        # Insert new token
        result = sessions.insert_one({
            "token": token_data.token,
            "main_email": token_data.email,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "type": "integration_token"
        })

        logger.info(f"Token created with ID: {result.inserted_id}")
        return {"status": "success", "id": str(result.inserted_id)}

    except Exception as e:
        logger.error(f"Error creating integration token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to store token: {str(e)}"
        )

@s.get("/verify-token/{token}")
async def verify_integration_token(token: str):
    """Verify integration token and return main email."""
    try:
        token_doc = sessions.find_one({
            "token": token,
            "type": "integration_token",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        if not token_doc:
            raise HTTPException(status_code=404, detail="Invalid or expired token")
        return {"main_email": token_doc["main_email"]}
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))