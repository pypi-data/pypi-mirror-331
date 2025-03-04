from abc import ABC, abstractmethod
from comicbot_api.v1.static.types import PUBLISHERS, FORMATS


def check_parameter(param, valid_params, parameter_group_name):
    if param not in valid_params:
        raise ValueError(f"Invalid parameter: '{param}' as {parameter_group_name}. Valid parameters are: {valid_params}")


class ValidationRule(ABC):
    @staticmethod
    @abstractmethod
    def validate(self, value, **kwargs):
        pass


class PublisherValidationRule(ValidationRule):
    @staticmethod
    def validate(self, **kwargs):
        publishers = kwargs.get('publishers')
        for publisher in publishers:
            check_parameter(publisher, list(PUBLISHERS.keys()), "publisher")


class FormatValidationRule(ValidationRule):
    @staticmethod
    def validate(self, **kwargs):
        formats = kwargs.get('formats')
        for _format in formats:
            check_parameter(_format, FORMATS.keys(), "formats")


class WeekValidationRule(ValidationRule):
    @staticmethod
    def validate(self, **kwargs):
        value = kwargs.get('week')
        if value < 1 or value > 53:
            raise ValueError("Week must be between 1 and 52")


VALIDATION_RULES = [WeekValidationRule, FormatValidationRule, PublisherValidationRule]