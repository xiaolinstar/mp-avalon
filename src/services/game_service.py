import random
from typing import List, Dict, Optional
from src.repositories.room_repository import room_repo
from src.repositories.user_repository import user_repo
from src.fsm.avalon_fsm import AvalonFSM, GamePhase
from src.exceptions.room import RoomStateError
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GameService:
    def __init__(self):
        self.fsm = AvalonFSM()

    def start_game(self, room_number: str, operator_openid: str):
        room = room_repo.get_by_number(room_number)
        if not room:
            raise RoomStateError("房间不存在")
        
        if room.owner_id != operator_openid:
            raise RoomStateError("只有房主可以开始游戏")
            
        players = list(room.game_state.players)
        player_count = len(players)
        if player_count < 5:
            raise RoomStateError(f"人数不足，当前 {player_count} 人，至少需要 5 人")

        # 1. Shuffle players for leader order
        random.shuffle(players)
        room.game_state.players = players
        
        # 2. Distribute Roles
        roles = self._assign_roles(players)
        room.game_state.roles_config = roles
        
        # 3. Set initial state
        room.game_state.phase = GamePhase.TEAM_SELECTION.value
        room.game_state.round_num = 1
        room.game_state.vote_track = 0
        room.game_state.leader_idx = 0
        room.game_state.quest_results = []
        room.status = 'PLAYING'
        
        room_repo.save(room)
        logger.info(f"Game started in room {room_number}")
        return room

    def _assign_roles(self, players: List[str]) -> Dict[str, str]:
        count = len(players)
        good_count, evil_count = self.fsm.get_role_distribution(count)
        
        # Minimal set: Merlin, Assassin vs others
        # Simplified for now: Just GOOD and EVIL
        all_roles = (['MERLIN'] + ['LOYAL'] * (good_count - 1) + 
                     ['ASSASSIN'] + ['MINION'] * (evil_count - 1))
        random.shuffle(all_roles)
        
        return {players[i]: all_roles[i] for i in range(count)}

game_service = GameService()
