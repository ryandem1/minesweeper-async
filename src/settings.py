from pydantic import BaseSettings, BaseModel, validator, ValidationError, NonNegativeInt


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


LatencyValue = tuple[NonNegativeInt, NonNegativeInt] | NonNegativeInt  # Either a range (20 - 50)ms or a number 50ms


class LatencySettings(BaseModel):
    """
    Controls the added latency of each endpoint
    """
    board: LatencyValue = 20, 50  # for the /board endpoint
    score: LatencyValue = 0  # for the /score endpoint
    hit: LatencyValue = 20, 50  # for the /hit endpoint
    check: LatencyValue = 20, 50  # for the /check endpoint
    flag: LatencyValue = 20, 50  # for the /flag endpoint
    is_space_blank: LatencyValue = 200, 300  # for the /is_space_blank endpoint
    get_space_value: LatencyValue = 600, 900  # for the /get_space_value endpoint

    @validator("board", "score", "hit", "is_space_blank", "check", "flag", pre=True)
    def _format_all_latency_values(cls, value: str | tuple[int, int] | int) -> LatencyValue:
        """
        Converts latency values from settings to proper format.

        Parameters
        ----------
        value : str
            Latency value either like <int> or <int>, <int>

        Returns
        -------
        LatencyValue
        """
        match value:
            case str(val) if "," in val:
                val = tuple(NonNegativeInt(v.strip()) for v in val.split(","))
                if len(val) != 2:
                    raise ValidationError(f"Invalid latency format: {val}", cls)
            case str(val):
                val = NonNegativeInt(val)
            case int(min_), int(max_):
                if not min_ < max_ and max_ > 0:
                    raise ValidationError(f"Invalid latency value: {min_}, {max_}", cls)
                val = min_, max_
            case _:
                raise ValidationError(f"Unexpected latency value: {value}", cls)
        return val


class Settings(BaseSettings):
    board: BoardSettings = BoardSettings()
    app: AppSettings = AppSettings()
    latency: LatencySettings = LatencySettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
