import requests
from dotenv import load_dotenv
from os import environ
load_dotenv()

BASE_URL = 'https://api.kinopoisk.dev'
headers = {
    'accept': 'application/json',
    'X-API-KEY': environ.get('KINOPOISK_API_TOKEN')
}

def get_random_movie() -> dict:
    r = requests.get(
        f'{BASE_URL}/v1.3/movie/random',
        headers=headers
    )
    return r.json()


def get_movie_by_id(movie_id: int) -> dict:
    r = requests.get(
        f'{BASE_URL}/v1.3/movie/{movie_id}',
        headers=headers
    )
    return r.json()


def search_movies(movie_name: str) -> dict:
    movies = requests.get(
        f'{BASE_URL}/v1.2/movie/search?page=1&limit=10&query={movie_name}',
        headers=headers
    ).json()
    return movies
    # return get_movie_by_id(movie['docs'][0]['id'])


if __name__ == '__main__':
    # print(get_movie_by_name('Матрица'))
    pass
