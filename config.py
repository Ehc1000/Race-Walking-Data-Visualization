import os

class Config:
    DATADATABASE_PATH = os.getenv(
        "DATADATABASE_PATH",
        os.path.join(os.path.dirname(__file__), "db", "DrexelRaceWalking.db")
    )