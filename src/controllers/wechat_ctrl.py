from flask import Blueprint, request, make_response, g
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from src.config.settings import settings
from src.utils.logger import get_logger

wechat_bp = Blueprint("wechat", __name__)
logger = get_logger(__name__)

@wechat_bp.route("/", methods=["GET", "POST"])
def wechat():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echo_str = request.args.get("echostr", "")

    try:
        check_signature(settings.WECHAT_TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        logger.error("Invalid signature from WeChat")
        return make_response("Invalid Signature", 403)

    if request.method == "GET":
        return echo_str

    # POST - Message handling
    msg = parse_message(request.data)
    # Store message in g for global error handler access
    g.wechat_msg = msg
    
    if msg.type == 'text':
        openid = msg.source
        content = msg.content
        logger.info(f"Received text message from {openid}: {content}")
        
        from src.wechat.parser import parser
        from src.wechat.commands import CommandType
        from src.services.room_service import room_service
        from src.repositories.user_repository import user_repo
        from src.services.game_service import game_service

        # 1. Ensure user exists
        user_repo.create_or_update(openid)

        # 2. Parse Command
        cmd = parser.parse(content, openid)
        
        reply_text = ""
        if cmd.command_type == CommandType.CREATE_ROOM:
            room = room_service.create_room(openid)
            reply_text = f"房间创建成功！房间号: {room.room_number}\n发送 /join {room.room_number} 让朋友们加入吧。"
        
        elif cmd.command_type == CommandType.JOIN_ROOM:
            room_num = cmd.args[0] if cmd.args else ""
            room_service.join_room(room_num, openid)
            reply_text = f"成功加入房间 {room_num}！"

        elif cmd.command_type == CommandType.START_GAME:
            room = user_repo.get_current_room(openid)
            if not room:
                reply_text = "你当前不在任何房间中。"
            else:
                room = game_service.start_game(room.room_number, openid)
                role_info = game_service.get_player_info(room, openid)
                reply_text = f"游戏开始！房间号: {room.room_number}\n\n{role_info}\n\n当前阶段: {room.game_state.phase}\n当前队长: 玩家{room.game_state.leader_idx + 1}"
        
        elif cmd.command_type == CommandType.STATUS:
            room = user_repo.get_current_room(openid)
            if not room:
                reply_text = "你当前不在任何房间中。"
            else:
                players = room.game_state.players
                players_count = len(players)
                reply_text = f"【房间 {room.room_number} 状态】\n- 状态: {room.status}\n- 阶段: {room.game_state.phase}\n- 玩家人数: {players_count}/10"
                
                if room.status == 'PLAYING':
                    leader_name = f"玩家{room.game_state.leader_idx + 1}"
                    reply_text += f"\n- 当前轮次: 第 {room.game_state.round_num} 局"
                    reply_text += f"\n- 连续失败: {room.game_state.vote_track}/5"
                    reply_text += f"\n- 当前队长: {leader_name}"
                    
                    if room.game_state.phase in ['TEAM_VOTE', 'QUEST_PERFORM']:
                        team_indices = [players.index(p)+1 for p in room.game_state.current_team]
                        reply_text += f"\n- 当前队伍: {team_indices}"
                        
                    role_info = game_service.get_player_info(room, openid)
                    reply_text += f"\n\n{role_info}"

        elif cmd.command_type == CommandType.PICK_TEAM:
            room = user_repo.get_current_room(openid)
            if not room:
                reply_text = "你当前不在任何房间中。"
            else:
                indices = [int(i) for i in cmd.args]
                game_service.pick_team(room.room_number, openid, indices)
                reply_text = f"组队成功！请全体玩家对队伍 {indices} 进行投票。\n发送 '/vote yes' 或 '/vote no'。"

        elif cmd.command_type == CommandType.VOTE:
            room = user_repo.get_current_room(openid)
            if not room:
                reply_text = "你当前不在任何房间中。"
            else:
                vote = cmd.args[0] if cmd.args else ""
                game_service.cast_vote(room.room_number, openid, vote)
                reply_text = f"投票成功 ({vote})！请等待其他玩家投票。"

        elif cmd.command_type == CommandType.QUEST:
            room = user_repo.get_current_room(openid)
            if not room:
                reply_text = "你当前不在任何房间中。"
            else:
                q_vote = cmd.args[0] if cmd.args else ""
                game_service.perform_quest(room.room_number, openid, q_vote)
                reply_text = f"任务投票成功 ({q_vote})！请等待结果发布。"

        elif cmd.command_type == CommandType.SHOOT:
            room = user_repo.get_current_room(openid)
            if not room:
                reply_text = "你当前不在任何房间中。"
            else:
                target_idx = int(cmd.args[0]) if cmd.args else 0
                result_msg = game_service.shoot_player(room.room_number, openid, target_idx)
                reply_text = result_msg

        elif cmd.command_type == CommandType.PROFILE:
            reply_text = game_service.get_user_stats(openid)

        elif cmd.command_type == CommandType.HELP:
            reply_text = "【阿瓦隆指令帮助】\n- 建房: 创建房间\n- 加入 {房号}: 加入房间\n- /start: 开始游戏\n- /status: 状态查询\n- /profile: 个人战绩\n- /pick 1 2 3: 队长组队\n- /vote yes/no: 组队投票\n- /quest success/fail: 任务执行\n- /shoot {编号}: 刺杀梅林"
        
        else:
            reply_text = f"收到消息: {content}。发送 '帮助' 查看可用指令。"

        reply = create_reply(reply_text, message=msg)
        return reply.render()
    else:
        reply = create_reply("目前仅支持文本消息交互", message=msg)
        return reply.render()
