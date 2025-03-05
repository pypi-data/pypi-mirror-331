
from co6co_web_db.view_model import BaseMethodView
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
import uuid


class drap_verify_view(BaseMethodView):

    async def post(self, request: Request):
        """
        拖动验证
        """
        json: dict = request.json
        start = json.get("start", 0)
        end = json.get("end", 0)
        if (end-start) > 300 and (end-start) < 500:
            s = str(uuid.uuid4())
            _, sDict = self.get_Session(request)
            sDict["verifyCode"] = s
            return JSON_util.response(Result.success(data=s, message="验证成功"))
        else:
            return JSON_util.response(Result.fail(message="验证失败"))
