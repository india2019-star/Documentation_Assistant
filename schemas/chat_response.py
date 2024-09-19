from pydantic import BaseModel


class ChatResponse(BaseModel):
    answer : str
    responseCode : int
    responseStatus : str
    sourceDocuments : str
