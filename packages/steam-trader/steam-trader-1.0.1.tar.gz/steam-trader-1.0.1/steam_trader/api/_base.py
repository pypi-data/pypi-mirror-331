import dataclasses
import logging
from abc import ABCMeta


class TraderClientObject:
    """Базовый класс для всех api объектов библиотеки.

    Changes:
        0.3.0: Удалён метод is_valid_data из-за ненадобности.
    """

    __metaclass__ = ABCMeta

    @classmethod
    def _de_json(cls, data: dict) -> dict:
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.

        Returns:
            dict, optional: Словарь с валидными аттрибутами для создания датакласса.
        """

        if not dataclasses.is_dataclass(cls):
            raise TypeError("Ожидался датакласс.")

        data = data.copy()
        fields = {f.name for f in dataclasses.fields(cls)}

        cleaned_data = {}
        unknown_data = {}

        for k, v in data.items():
            if k in fields:
                cleaned_data[k] = v
            else:
                unknown_data[k] = v

        if unknown_data:
            logging.warning(f'Были получены неизвестные аттриубты для класса {cls} :: {unknown_data}')

        return cleaned_data
