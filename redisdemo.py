import redis
import json

redis_client=redis.Redis(host='localhost', port=6380, decode_responses=True)
bike = {
  "model": "Jigger",
  "brand": "Velorim",
  "price": 270,
  "type": "Kids bikes",
  "specs": {
    "material": "aluminium",
    "weight": "10"
  },
  "description": "Small and powerful, the Jigger is the best ride for the smallest of tikes! ..."
}

json.dumps(bikes[0], indent=2)