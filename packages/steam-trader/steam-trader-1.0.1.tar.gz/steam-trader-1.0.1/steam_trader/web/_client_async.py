######################################################################################
# ЭТО АВТОМАТИЧЕСКИ СОЗДАННАЯ КОПИЯ СИНХРОННОГО КЛИЕНТА. НЕ ИЗМЕНЯЙТЕ САМОСТОЯТЕЛЬНО #
######################################################################################

import bs4
import httpx
import logging
from functools import wraps
from collections.abc import Sequence, Callable
from typing import Optional, Literal, TypeVar, Any, Self, cast
from ._base import WebClientObject
from ._dataclasses import MainPage, ItemInfo, Referal, HistoryItem
from steam_trader import constants
from steam_trader.exceptions import *


logging.getLogger(__name__).addHandler(logging.NullHandler())

F = TypeVar('F', bound=Callable[..., Any])

def log(method: F) -> F:
    logger = logging.getLogger(method.__module__)

    @wraps(method)
    async def wrapper(*args, **kwargs):
        logger.debug(f'Entering: {method.__name__}')

        result = await method(*args, **kwargs)
        logger.info(result)

        logger.debug(f'Exiting: {method.__name__}')

        return result

    return wrapper  # type: ignore


class WebClientAsync(WebClientObject):
    """Этот клиент позволяет получить данные сайта без API ключа или получить информацию, которая недоступна через API.
    Для некоторых методов необходимо указать ID сессии. Он находится в файлах куки (или хедерах) и переодически сбрасывается.

    Если вам не нравятся предупреждения об устаревании от httpx, то повысьте уровень логов модуля.
    Это не ошибка https://github.com/encode/httpx/discussions/2931.

    Args:
        sessionid (int, optional): ID сессии. Может быть пустым.
        proxy (str, optional): Прокси для запросов. Для использования нужен контекстный менеджер with.
        base_url (str, optional): Ссылка на API Steam Trader.
        **kwargs: Будут переданы httpx клиенту. Например timeout.

    Attributes:
        sessionid (int, optional): ID сессии.
        proxy (str, optional): Прокси для запросов.
        base_url (str, optional): Ссылка на API Steam Trader.
    """

    __slots__ = [
        'proxy',
        'sessionid',
        'base_url',
        'headers'
    ]

    def __init__(
            self,
            sessionid: Optional[str] = None,
            *,
            proxy: Optional[str] = None,
            base_url: Optional[str] = None,
            **kwargs
    ):
        self.sessionid = sessionid

        if base_url is None:
            base_url = "https://steam-trader.com/"
        self.base_url = base_url

        self._httpx_client = None
        self.proxy = proxy
        self._kwargs = kwargs

    async def __aenter__(self) -> Self:
        self._httpx_client = httpx.AsyncClient(proxy=self.proxy, **self._kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._httpx_client:
            await self._httpx_client.aclose()

    async def _get_request(
        self,
        url: str,
        *,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        cookies: Optional[dict[str, str]] = None,
        de_json: bool = True,
        **kwargs
    ) -> Any:
        """Создать GET запрос и вернуть данные.

        Args:
            method (str): Ссылка для запроса.
            headers (dict[str, str], optional): Заголовки запроса.
            params (dict[str, Any], optional): Параметры запроса.
            cookies (dict[str, str], optional): Куки запроса.
            de_json (bool): Преобразовать запрос в формат для использования.
            **kwargs: Будут переданы httpx клиенту.

        Returns:
            Any: Ответ сервера.
        """

        if not self._httpx_client:
            raise ValueError("Используйте контекстный менеджер async with")

        result = await self._httpx_client.get(
            url,
            headers=headers,
            params=params,
            cookies=cookies,
            **kwargs
        )

        if de_json:
            return result.json()
        return result
        
    @log
    async def get_main_page(
        self,
        gameid: int,
        *,
        price_from: int = 0,
        price_to: int = 2000,
        filters: Optional[dict[str, int]] = None,
        text: Optional[str] = None,
        sort: Literal[
            '-rating', 'rating', '-price', 'price', '-benefit', 'benefit', '-name', 'name'
        ] = '-rating',
        page: int = 1,
        items_on_page: int = 24
    ) -> MainPage:
        """Получить главную страницу покупки для игры.

        Args:
            gameid (int): AppID игры.
            price_from (int): Минимальная цена предмета.
            price_to (int): Максимальная цена предмета.
                Если больше или равно 2000, ограничение снимается.
            filters (dict[str, int], optional): Словарь пар название/ID.
                См web_api.api.Filters для названий и web_api.constants для ID.
            text (str, optional): Текст, который должен встречаться в названии.
            sort (Literal): Метод сортировки.
                '-rating' - Сначала самые популярные. По умолчанию.
                'rating' - Сначала менее популярные.
                '-price' - Сначала самые дорогие.
                'price' - Сначала самые дешёвые.
                '-benefit' - Сначала самые невыгодные.
                'benefit' - Сначала самые выгодные.
                '-name' - В алфавитном порядке UNICODE.
                'name' - В обратном алфавитном порядке UNICODE.
            page (int): Номер страницы, начиная с 1.
            items_on_page (int): Кол-во отображаемых предметов на странице.
                Значение должно быть в диапазоне от 24 до 120 с интервалом 6.

        Returns:
            MainPage: Главная страница покупки.
        """

        try:
            game_name = constants.NAME_BY_APPID[gameid]
        except KeyError:
            raise UnsupportedAppID('Указан недействительный AppID.')

        if items_on_page not in range(24, 121) or items_on_page % 6 != 0:
            logging.warning(f'Неправильное значение items_on_page >> {items_on_page}')

        if sort not in ['-rating', 'rating', '-price', 'price', '-benefit', 'benefit', '-name', 'name']:
            logging.warning(f'Неправильное значение sort >> {sort}')

        if filters is None:
            filters = {}
            
        headers={
            'x-pjax': 'true',
            'x-requested-with': 'XMLHttpRequest',
            'x-pjax-container': 'form.market .items .wrap'
        }
        params={
            'price_from': price_from,
            'price_to': price_to,
            **filters,
            'text': text,
            'sort': sort,
            'page': page,
        }
        cookies={
            'sid': self.sessionid,
            'settings': f'%7B%22market_{gameid}_onPage%22%3A{items_on_page}%7D'
        }
        result = await self._get_request(self.base_url + game_name, headers=headers, params=params, cookies=cookies)

        return MainPage.de_json(result)

    @log
    async def get_item_info(
        self,
        gid: int,
        *,
        page: int = 1,
        items_on_page: int = 24
    ) -> ItemInfo:
        """Получить информацию о предмете через WebAPI. Позволяет увидеть описание индивидуальных предметов.

        Args:
            gid (int): ID группы предметов.
            page (int): Номер страницы.
            items_on_page (int): Кол-во предметов на странице.
                Значение должно быть в диапазоне от 24 до 120 с интервалом 6.

        Returns:
            ItemInfo: Информация о предмете.
        """

        if items_on_page not in range(24, 121) or items_on_page % 6 != 0:
            logging.warning(f"Неправильное значение items_on_page '{items_on_page}'")

        url = f'{self.base_url}tf2/{gid}-The-Wrap-Assassin'  # Сайт перенаправляет на корректную страницу
        correct_url = await self._get_request(
            url,
            follow_redirects=True,
            de_json=False
        )
        
        headers={
            'x-pjax': 'true',
            'x-requested-with': 'XMLHttpRequest',
            'x-pjax-container': '#content #wrapper'
        }
        params={'page': page}
        cookies={
            'sid': self.sessionid,
            'settings': f'%7B%22item_onPage%22%3A{items_on_page}%7D'
        }
        
        result = await self._get_request(str(correct_url.url), headers=headers, params=params, cookies=cookies)
        return ItemInfo.de_json(result)

    @log
    async def get_referral_link(self) -> str:
        """Получить реферальную ссылку.

        Returns:
            str: Реферальная ссылка.
        """

        if not self.sessionid:
            raise Unauthorized('Для использования данного метода нужно указать sessionid (sid). Вы можете найти его в файлах куки.')

        headers = {
            'x-pjax': 'true',
            'x-requested-with': 'XMLHttpRequest',
            'x-pjax-container': '#content #wrapper'
        }
        cookies = {'sid': self.sessionid}

        result = await self._get_request(self.base_url + 'referral/', headers=headers, cookies=cookies)
        html = bs4.BeautifulSoup(result['contents'], 'lxml')
        tag = cast(bs4.Tag, html.find('input', {'class': 'big'}))
        return cast(str, tag.get('value'))

    @log
    async def get_referals(
        self,
        status: Optional[Literal[1, 2]] = None,
        items_on_page: int = 24
    ) -> Sequence[Referal]:
        """Получить список рефералов.

        Args:
            status (int): Статус реферала.
                None - Все. По умолчанию.
                1 - Активный.
                2 - Пассивный.
            items_on_page (int): Кол-во рефералов на странице.
                Значение должно быть в диапазоне от 24 до 120.

        Returns:
            Sequence[Referal]: Список рефералов.
        """

        if not self.sessionid:
            raise Unauthorized('Для использования данного метода нужно указать sessionid (sid). Вы можете найти его в файлах куки.')

        if items_on_page not in range(24, 121) or items_on_page % 6 != 0:
            logging.warning(f'Неправильное значение items_on_page >> {items_on_page}')

        headers = {
            'x-pjax': 'true',
            'x-requested-with': 'XMLHttpRequest',
            'x-pjax-container': '#content #wrapper'
        }
        params={'type': status}
        cookies={'sid': self.sessionid, 'settings': f'%7B%22referral_onPage%22%3A{items_on_page}%7D'}
        
        result = await self._get_request(self.base_url + 'referral/', headers=headers, params=params, cookies=cookies)
        html = bs4.BeautifulSoup(result['contents'], 'lxml')
        tds = html.find_all('td')

        if tds[0].get('colspan') == '4':  # Ничего не найдено
            return []

        referals = []
        for td in tds:
            divs = td.find_all_next('div')
            data = {
                'name': divs[0].text,
                'date': divs[1].text,
                'status': divs[1].text,
                'sum': divs[1].text
            }
            referals.append(Referal._de_json(data))

        return referals

    @log
    async def get_history_page(self, gameid: int, category: Literal['last', 'day_most', 'all_time_most'] = 'last') -> Sequence[HistoryItem]:
        """Получить страницу истории продаж.

        Args:
            gameid (int): AppID игры.
            category (str): Категория истории.
                'last': Последние покупки. По умолчанию.
                'day_most': Самые дорогие за 24 часа.
                'all_time_most': Самые дорогие за все время.

        Returns:
            Sequence[HistoryItem]: Последовательность предметов из истории.
        """

        try:
            game_name = constants.NAME_BY_APPID[gameid]
        except KeyError:
            raise UnsupportedAppID('Указан недействительный AppID.')

        match category:
            case 'last':
                i = 0
            case 'day_most':
                i = 1
            case 'all_time_most':
                i = 2
            case _:
                raise ValueError('Указано недопустимое значение category.')

        url = f'{self.base_url}{game_name}/history/'
        page = await self._get_request(url, de_json=False)

        html = bs4.BeautifulSoup(page.content, 'lxml')

        history = html.find_all('div', {'class': 'items'})
        history_items = history[i].find_all('a')

        result = []
        for item in history_items:
            result.append(HistoryItem.de_json(item))
        return result
