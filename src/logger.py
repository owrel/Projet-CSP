class Logger:
    DEBUG = "DEBUG"
    INFO = "INFO"
    QUIET = "QUIET"

    def __init__(self, log_level: str = "INFO") -> None:
        self.log_level = log_level

    def info(self, message: str):
        if self.log_level in ["DEBUG", "INFO"]:
            print(f"[INFO] {message}")

    def debug(self, message: str):
        if self.log_level == "DEBUG":
            print(f"[DEBUG] {message}")

    def error(self, message: str):
        if self.log_level != Logger.QUIET:
            print(f"[ERROR] {message}")
