from flask import Blueprint, request, make_response
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
    if msg.type == 'text':
        openid = msg.source
        content = msg.content
        logger.info(f"Received text message from {openid}: {content}")
        
        from src.wechat.parser import parser
        from src.wechat.commands import CommandType
        from src.services.room_service import room_service
        from src.exceptions.base import BaseGameException
        from src.repositories.user_repository import user_repo

        # 1. Ensure user exists
        user_repo.create_or_update(openid)

        # 2. Parse Command
        cmd = parser.parse(content, openid)
        
        reply_text = ""
        try:
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
                    reply_text = "你当前不在任何房间中，请先创建或加入房间。"
                else:
                    from src.services.game_service import game_service
                    game_service.start_game(room.room_number, openid)
                    reply_text = f"游戏开始！房间 {room.room_number} 已进入组队阶段。身份已私发（模拟）。"
            
            elif cmd.command_type == CommandType.STATUS:
                room = user_repo.get_current_room(openid)
                if not room:
                    reply_text = "你当前不在任何房间中。"
                else:
                    players_count = len(room.game_state.players)
                    reply_text = f"【房间 {room.room_number} 状态】\n- 状态: {room.status}\n- 阶段: {room.game_state.phase}\n- 玩家人数: {players_count}/10"
                    if room.status == 'PLAYING':
                        reply_text += f"\n- 当前轮次: 第 {room.game_state.round_num} 局"

            elif cmd.command_type == CommandType.HELP:
                reply_text = "【阿瓦隆指令帮助】\n- 建房: 创建新房间\n- 加入 房间号: 进入房间\n- /start: 开始游戏\n- /status: 查看状态"
            
            else:
                reply_text = f"收到消息: {content}。发送 '帮助' 查看可用指令。"

        except BaseGameException as e:
            reply_text = f"提示: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            reply_text = "系统繁忙，请稍后再试"

        reply = create_reply(reply_text, msg)
    else:
        reply = create_reply("目前仅支持文本消息交互", msg)
        
    return reply.render()
