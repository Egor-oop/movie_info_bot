from aiogram.dispatcher.filters.state import StatesGroup, State


class SearchMovie(StatesGroup):
    name = State()


class PaginationMovies(StatesGroup):
    movies = State()

