import jwt
from datetime import datetime, timedelta
import config as config

ACCESS_SECRET = config.JWT_ACCESS_SECRET
REFRESH_SECRET = config.JWT_REFRESH_SECRET
ALGORITHM = config.JWT_ALGORITHM
ACCESS_EXPIRE = timedelta(minutes=int(config.JWT_ACCESS_MINUTES))
REFRESH_EXPIRE = timedelta(days=int(config.JWT_REFRESH_DAYS))

def access_token(id: int, role: str) -> str:
    payload = {"expire": (datetime.today() + ACCESS_EXPIRE).ctime(), "id": id, "role": role}
    return jwt.encode(payload, ACCESS_SECRET, ALGORITHM)

def refresh_token(id: int, role: str) -> str:
    payload = {"expire": (datetime.today() + REFRESH_EXPIRE).ctime(), "id": id, "role": role}
    return jwt.encode(payload, REFRESH_SECRET, ALGORITHM)

def access_decode(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
        return decoded_token if datetime.strptime(decoded_token["expire"], '%a %b  %d %H:%M:%S %Y') >= datetime.today() else None
    except:
        return None
    
def refresh_decode(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])
        return decoded_token if datetime.strptime(decoded_token["expire"], '%a %b  %d %H:%M:%S %Y') >= datetime.today() else None
    except Exception as e:
        print(e)
        return None