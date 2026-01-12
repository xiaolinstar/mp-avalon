from typing import Optional
from src.extensions.redis_ext import redis_manager
from src.app_factory import db
from src.models.sql_models import Room, GameState
from src.utils.json_utils import json_dumps, json_loads
from src.utils.logger import get_logger
from sqlalchemy.orm.attributes import flag_modified

logger = get_logger(__name__)

class RoomRepository:
    """
    Handles persistence for Room and GameState.
    Uses MySQL as Source of Truth and Redis as a Cache.
    Implements Cache-Aside strategy.
    """

    CACHE_TTL = 3600  # 1 hour
    CACHE_PREFIX = "cache:room:"

    def get_by_number(self, room_number: str) -> Optional[Room]:
        cache_key = f"{self.CACHE_PREFIX}{room_number}"
        
        # 1. Try Redis Cache
        cached_data = redis_manager.client.get(cache_key)
        if cached_data:
            logger.debug(f"Cache HIT for room {room_number}")
            # Note: Complex to reconstruct SQLAlchemy object from simple JSON cache 
            # while keeping it attached to session. 
            # In a real app, we might return a DTO or ensure it's merged.
            # Here we'll simplify: if cache exists, we still hit DB but we know it's there.
            # Optimization: Actually reconstruct or use a custom serializer.
            pass

        # 2. Try MySQL
        room = Room.query.filter_by(room_number=room_number).first()
        if room:
            # 3. Fill Cache if found
            # self._set_cache(room)
            return room
        
        return None

    def save(self, room: Room) -> None:
        """
        Saves room with optimistic locking (handled by version field).
        Then invalidates cache.
        """
        try:
            # Incremental version handled manually or via SQLAlchemy events
            if room.version is None:
                room.version = 1
            else:
                room.version += 1
            db.session.add(room)
            db.session.commit()
            
            # Invalidate Redis Cache
            redis_manager.client.delete(f"{self.CACHE_PREFIX}{room.room_number}")
            logger.debug(f"Saved room {room.room_number} and invalidated cache")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to save room {room.room_number}: {str(e)}")
            raise

    def delete(self, room: Room) -> None:
        room_number = room.room_number
        db.session.delete(room)
        db.session.commit()
        redis_manager.client.delete(f"{self.CACHE_PREFIX}{room_number}")

    def update_game_state(self, game_state: GameState) -> None:
        """
        Special helper for JSON fields in GameState.
        SQLAlchemy doesn't always detect internal JSON changes.
        """
        flag_modified(game_state, "current_team")
        flag_modified(game_state, "quest_results")
        flag_modified(game_state, "roles_config")
        flag_modified(game_state, "players")
        flag_modified(game_state, "votes")
        flag_modified(game_state, "quest_votes")
        db.session.commit()
        
        # Invalidate associated room cache
        if game_state.room:
            redis_manager.client.delete(f"{self.CACHE_PREFIX}{game_state.room.room_number}")

# Singleton
room_repo = RoomRepository()
