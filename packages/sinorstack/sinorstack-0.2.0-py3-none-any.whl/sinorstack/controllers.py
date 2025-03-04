from dependency_injector.wiring import inject, Provide
from sinorstack.exceptions import AppException


class BaseController:
    @inject
    def __init__(self, use_case=Provide["use_case"], validator=Provide["validator"]):
        self.use_case = use_case
        if validator:
            self.validator = validator

    def handle(self, *args, **kwargs):
        raise NotImplementedError

    def validate(self, data):
        if hasattr(self, "validator"):
            return self.validator(**data)
        return data

    def execute(self, *args, **kwargs):
        try:
            return self.handle(*args, **kwargs)
        except AppException as e:
            return e.to_dict()
