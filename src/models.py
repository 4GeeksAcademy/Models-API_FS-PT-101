from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Float, Integer, DateTime
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLAEnum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    firstname: Mapped[str] = mapped_column(String)
    lastname: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    followers_from: Mapped[list["Follower"]] = relationship("Follower", foreign_keys="[Follower.user_from_id]")
    followers_to: Mapped[list["Follower"]] = relationship("Follower", foreign_keys="[Follower.user_to_id]")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
        }

class Follower(db.Model):
    __tablename__ = "follower"
    user_from_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)
    
    user_from = relationship("User", foreign_keys=[user_from_id])
    user_to = relationship("User", foreign_keys=[user_to_id])
    
    def serialize(self):
        return {
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id,
        }
class enumPost(PyEnum):
    Character = "Character Post"
    Planet = "Planet Post"

class Post(db.Model):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String)
    type: Mapped[enumPost] = mapped_column(SQLAEnum(enumPost))
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    planet_id: Mapped[int] = mapped_column(Integer, ForeignKey("planet.id"))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("character.id"))

    user: Mapped["User"] = relationship("User", back_populates="posts")
    character: Mapped["Character"] = relationship("Character", back_populates="posts")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="posts")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type.value,
            "creation_date": self.creation_date,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
        }
    
class Media(db.Model):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    planet_id: Mapped[int] = mapped_column(Integer, ForeignKey("planet.id"))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("character.id"))
    
    character: Mapped["Character"] = relationship("Character", back_populates="medias")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="medias")

    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
        }

class enumFaction(PyEnum):
    republic = "Galactic Republic"
    separatists = "Separatists (CIS)"
    empire = "Galactic Empire"
    rebels = "Rebel Alliance"
    f_order = "First Order"
    resistance = "Resistance"

class enumRole(PyEnum):
    villain = "Villain"
    antihero = "Anti-hero"
    hero = "Hero"
    neutral = "Neutral"

class Character(db.Model):
    __tablename__ = "character"
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    faction: Mapped[enumFaction] = mapped_column(SQLAEnum(enumFaction))
    type: Mapped[enumRole] = mapped_column(SQLAEnum(enumRole))

    medias: Mapped[list["Media"]] = relationship("Media", back_populates="character")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="character")
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "age": self.age,
            "faction": self.faction.value,
            "type": self.type.value,
        }
    
class Planet(db.Model):
    __tablename__ = "planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    size: Mapped[float] = mapped_column(Float, nullable=False)
    inhabited: Mapped[bool] = mapped_column(Boolean, nullable=False)
    distance: Mapped[float] = mapped_column(Float, nullable=False)

    medias: Mapped[list["Media"]] = relationship("Media", back_populates="planet")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="planet")
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "inhabited": self.inhabited,
            "distance": self.distance,
        }
    
class Favorite(db.Model):
    __tablename__ = "favorite"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    planet_id: Mapped[int] = mapped_column(Integer, ForeignKey("planet.id"))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("character.id"))

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorites")
    character: Mapped["Character"] = relationship("Character", back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet": self.planet.serialize() if self.planet else None,
            "character": self.character.serialize() if self.character else None,
        }
