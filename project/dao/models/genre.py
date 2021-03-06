from project.dao.models.base import BaseMixin
from project.setup_db import db
from sqlalchemy import Column, String, Integer


class Genre(BaseMixin, db.Model):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre '{self.name.title()}'>"
