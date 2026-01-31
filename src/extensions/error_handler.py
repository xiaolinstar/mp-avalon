from flask import g, jsonify, make_response

from src.exceptions.base import AppException, ClientException, BizException, ServerException
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ClientException)
    def handle_client_exception(e):
        # 客户端异常：记录警告日志，但不作为系统错误
        logger.warning(f"Client error: {e.error_code} - {e.message}, details: {e.details}")
        return _format_error_reply(e.message, e.http_status)

    @app.errorhandler(BizException)
    def handle_biz_exception(e):
        # 业务异常：记录业务警告日志
        logger.warning(f"Business logic error: {e.error_code} - {e.message}, details: {e.details}")
        return _format_error_reply(e.message, e.http_status)

    @app.errorhandler(ServerException)
    def handle_server_exception(e):
        # 服务端异常：记录错误日志
        logger.error(f"Server error: {e.error_code} - {e.message}, details: {e.details}, cause: {e.cause}", exc_info=True)
        # 返回通用错误信息，避免暴露系统细节
        msg = "服务器内部错误，请稍后再试"
        if app.config.get("DEBUG") or app.config.get("TESTING"):
            msg = f"服务器错误: {e.message}"
        return _format_error_reply(msg, e.http_status)

    @app.errorhandler(AppException)
    def handle_app_exception(e):
        # 通用异常处理：对于未分类的应用异常，按服务端异常处理（因为可能是未预期的异常情况）
        logger.error(f"Unknown app exception: {e.error_code} - {e.message}, details: {e.details}", exc_info=True)
        msg = "服务器内部错误，请稍后再试"
        if app.config.get("DEBUG") or app.config.get("TESTING"):
            msg = f"服务器错误: {e.message}"
        return _format_error_reply(msg, e.http_status)

    @app.errorhandler(404)
    def handle_not_found(e):
        return _format_error_reply("接口不存在", 404)

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        # 在开发模式下返回更多信息，在生产环境返回通用消息
        msg = "系统繁忙，请稍后再试"
        if app.config.get("DEBUG") or app.config.get("TESTING"):
            msg = f"系统错误: {str(e)}"

        return _format_error_reply(msg, 500)


def _format_error_reply(message, status_code):
    wechat_msg = getattr(g, "wechat_msg", None)
    if wechat_msg:
        from wechatpy import create_reply

        # 根据状态码确定前缀
        if status_code == 400:
            prefix = "请求错误"
        elif status_code == 200:
            prefix = "提示"
        else:
            prefix = "错误"
        
        reply = create_reply(f"{prefix}: {message}", message=wechat_msg)
        return make_response(reply.render(), 200)

    return jsonify({"status": "error", "message": message, "code": status_code}), status_code
