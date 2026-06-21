from database import sudo
import config

def is_sudo(user_id: int):
    if user_id == config.OWNER_ID:
        return True
    return sudo.find_one({"user_id": user_id}) is not None
