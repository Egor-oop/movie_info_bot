from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BadRequest
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from os import environ
from random import choice

from states import SearchMovie
from keyboards import (
    get_main_keyboard,
    get_cancel_keyboard,
    get_movie_inline_keyboard,
    get_movies_pagination_keyboard,
)
from config import cd_walk
import api

load_dotenv()

API_TOKEN = environ.get('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def start_help(message: types.Message):
    await message.reply('*Команды*\n'
                        '/random — выдаёт случайный фильм\n'
                        '/search — поиск фильмов\n'
                        'Под каждым фильмом есть кнопка "Похожий фильм"',
                        reply_markup=get_main_keyboard(),
                        parse_mode='Markdown')
    await message.delete()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Отмена', reply_markup=get_main_keyboard())
    await message.delete()


async def send_movie(message: types.Message, movie: dict):
    movie_countries, movie_genres = [], []
    for i in movie['countries']:
        movie_countries.append(i['name'])
    for i in movie['genres']:
        movie_genres.append(i['name'])
    try:
        await bot.send_photo(message.chat.id, movie['poster']['url'],
                             caption=f'*{movie["name"]}*\n'
                                     f'Год: {movie["year"]}\n'
                                     f'Страна: {", ".join(movie_countries)}\n'
                                     f'Жанры: {", ".join(movie_genres)}\n'
                                     f'Длительность: {movie["movieLength"]} мин.\n\n'
                                     f'{movie["description"]}',
                             parse_mode='Markdown',
                             reply_markup=get_movie_inline_keyboard(movie))
        print(f"\"{movie['name']}\" is recieved by "
              f"{message.from_user.username} ({message.from_user.full_name})")
    except BadRequest:
        await message.reply('Что-то пошло не так. Попробуйте ещё раз.')


async def send_similar_movie(message: types.Message, movie_id: int):
    movie = api.get_movie_by_id(movie_id)
    await send_movie(message, movie)


@dp.message_handler(commands=['random'])
async def cmd_random_movie(message: types.Message):
    movie = api.get_random_movie()
    await send_movie(message, movie)
    await message.delete()


@dp.message_handler(commands=['search'])
async def cmd_search_movie(message: types.Message):
    await message.reply(
        'Введите название фильма',
        reply_markup=get_cancel_keyboard()
    )
    await message.delete()
    await SearchMovie.name.set()


@dp.message_handler(state=SearchMovie.name)
async def process_movie_name_search(message: types.Message,
                                    state: FSMContext):
    print(f'{message.from_user.username} ({message.from_user.full_name}) '
          f'looked for {message.text}')
    global movies_pagination
    async with state.proxy() as data:
        data['name'] = message.text
    movies_pagination = api.search_movies(data['name'])
    await message.answer(
        '.', reply_markup=get_main_keyboard()
    )
    await send_movie_page(message, movies_pagination)
    await message.delete()
    await state.finish()


async def send_movie_page(message: types.Message,
                          movies: dict,
                          page: int = 1):
    paginator = get_movies_pagination_keyboard(
        len(movies['docs']),
        current_page=page,
        data_pattern='movie#{page}',
        movie_id = movies['docs'][page-1]['id']
    )
    msg = f"*{movies['docs'][page-1]['name']}* — {movies['docs'][page-1]['year']}"
    await message.answer(
        msg,
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


@dp.callback_query_handler(lambda callback: callback.data.split('#')[0] == 'movie')
async def movie_page_callback(callback):
    page = int(callback.data.split('#')[1])
    await bot.delete_message(
        callback.message.chat.id,
        callback.message.message_id
    )
    await send_movie_page(callback.message, movies_pagination, page)


@dp.callback_query_handler(lambda callback: callback.data.split('#')[0] == 'more_about_movie')
async def more_about_movie_callback(callback: types.CallbackQuery):
    int(callback.data.split('#')[1])
    await send_movie(
        callback.message,
        api.get_movie_by_id(int(callback.data.split('#')[1]))
    )


@dp.callback_query_handler(cd_walk.filter())
async def callback_similar_movie(callback: types.CallbackQuery,
                                 callback_data: dict):
    if int(callback_data.get('similar_movie_id')) > 0:
        await send_similar_movie(callback.message,
                                 callback_data.get('similar_movie_id'))
    else:
        await callback.answer('Нет похожих фильмов')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
