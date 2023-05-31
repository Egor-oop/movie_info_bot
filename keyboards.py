from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram_bot_pagination import InlineKeyboardPaginator
from random import choice
from config import cd_walk


class MoviePaginator(InlineKeyboardPaginator):
    first_page_label = '<<{}'
    previous_page_label = '{}'
    next_page_label = '{}'
    last_page_label = '{}>>'
    current_page_label = '- {} -'


def get_main_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)\
        .add(KeyboardButton(text='/random'), KeyboardButton(text='/search'))


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True)\
        .add(KeyboardButton(text='Отмена'))


def get_movie_inline_keyboard(movie: dict):
    try:
        movie_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Похожий фильм',
                                 callback_data=cd_walk.new(
                                     similar_movie_id=choice(movie['similarMovies'])['id']
                                 )))
    except IndexError:
        movie_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Похожий фильм',
                                 callback_data=cd_walk.new(
                                     similar_movie_id=0
                                 )))
    return movie_kb


def get_movies_pagination_keyboard(pages_count: int,
                                   current_page: int,
                                   data_pattern: str,
                                   movie_id: int) -> MoviePaginator:
    paginator = MoviePaginator(
        page_count=pages_count,
        current_page=current_page,
        data_pattern=data_pattern
    )
    paginator.add_after(
        InlineKeyboardButton(text='Узнать больше',
                             callback_data=f'more_about_movie#{movie_id}')
    )
    return paginator
