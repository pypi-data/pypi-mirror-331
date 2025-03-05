import re
import logging
import dataclasses
from abc import ABCMeta
from collections.abc import MutableSequence
from typing import Self


class WebClientObject:
    """Базовый класс для всех объектов web части библиотеки."""

    __metaclass__ = ABCMeta

    def remove_html_tags(self, __obj: str | dict | MutableSequence | Self = '__dataclass__', *, replace_p_with='\n') -> str | dict | MutableSequence | Self:
        """Преобразует словари, изменяемые последовательности, классы и строки в читабельный формат, без HTML тегов.
        Также заменяет теги <a> на гиперссылки для отправки в Телеграм.

        Аргумент ``replace_p_with`` заменяет теги <p> на введённый символ. По умолчанию новая строка.

        Возвращаемый предмет зависит от типа данных __obj. Не меняйте __obj если используете на датаклассе.
        """

        if __obj == '__dataclass__':
            __obj = self

        if isinstance(__obj, str):
            __obj = re.sub(r'<[^>]+>', '', __obj.replace('<p', f'{replace_p_with}<p'))
            if replace_p_with == ' ':
                __obj = __obj.replace('  ', ' ')  # исключаем двойные <p>
            return __obj.strip()
        elif isinstance(__obj, MutableSequence):
            for i, item in enumerate(__obj):
                __obj[i] = self.remove_html_tags(item)
        elif isinstance(__obj, dict):
            for k, v in __obj.copy().items():
                __obj[k] = self.remove_html_tags(v)
        elif dataclasses.is_dataclass(__obj):
            for f in dataclasses.fields(__obj):
                __obj.__setattr__(f.name, self.remove_html_tags(__obj.__getattribute__(f.name)))

        return __obj

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
