from pydantic import BaseModel, Field


class ConnectionSettings(BaseModel):
    connection_string: str = Field(alias="DefaultConnection")


class ApplicationSettings(BaseModel):
    connection_settings: ConnectionSettings = Field(alias="ConnectionStrings")


class DBConnectionSettings(BaseModel):
    host: str = Field(alias="Host")
    port: int = Field(alias="Port")
    database: str = Field(alias="Database")
    username: str = Field(alias="Username")
    password: str = Field(alias="Password")

    class Config:
        populate_by_name = True
