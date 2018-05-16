
import json, datetime
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except:
            return str(obj)
