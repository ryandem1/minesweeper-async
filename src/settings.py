from pydantic import BaseSettings, BaseModel


class BoardSettings(BaseModel):
    """
    Global board settings
    """
    length: int = 9
    height: int = 9
    mines: int = 10


class AppSettings(BaseModel):
    """
    Global app settings
    """
    max_boards: int = 5  # Maximum number of outstanding boards to allow


class Settings(BaseSettings):
    board: BoardSettings = BoardSettings()
    app: AppSettings = AppSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
