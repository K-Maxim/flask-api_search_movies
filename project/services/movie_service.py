from project.dao.movie import MovieDAO
from project.exceptions import ItemNotFound
from project.schemas.movie import MovieSchema

from project.services.base import BaseService


class MovieService(BaseService):
    def get_item_by_id(self, pk):
        """
        Получаем фильм по его id
        """
        movie = MovieDAO(self._db_session).get_by_id(pk)
        if not movie:
            raise ItemNotFound
        return MovieSchema().dump(movie)

    def get_all_movies(self):
        """
        Получаем список фильмов
        """
        movies = MovieDAO(self._db_session).get_all()
        return MovieSchema(many=True).dump(movies)
