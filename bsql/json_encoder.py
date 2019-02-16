import json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        """Try to encode JSON with super(); fallback to string encoding."""
        try:
            return super().default(obj)
        except:
            return str(obj)
