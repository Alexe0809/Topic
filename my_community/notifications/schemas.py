from pydantic import BaseModel


class EmailMessageData(BaseModel):
    email: str
    username: str
    url: str


class MessageType(BaseModel):
    subject: str
    template_name_html: str
    template_name_txt: str

    class Config:
        frozen = True
