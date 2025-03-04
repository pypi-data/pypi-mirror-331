class AppException(Exception):
    """Базовый класс для всех исключений приложения"""

    message = "Произошла ошибка"
    status_code = 400

    def __init__(self, message=None):
        if message:
            self.message = message

    def to_dict(self):
        return {
            "error": self.message,
            "status_code": self.status_code,
        }
