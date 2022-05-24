
from flask_restful import Resource
from util.cache.channel import AllChannelsCache


class ChannelView(Resource):
    """获取所有的频道"""
    def get(self):
        ret = AllChannelsCache.get()
        return {'channels': ret}