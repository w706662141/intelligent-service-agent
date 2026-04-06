import json
from datetime import date, datetime

# class DateTimeEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, (date, datetime)):
#             return o.isoformat()
#         return super().default(o)
from decimal import Decimal


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):

        if isinstance(o, Decimal):
            return float(o)

        if isinstance(o, (date, datetime)):
            return o.isoformat()

        return super().default(o)
