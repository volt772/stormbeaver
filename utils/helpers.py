import random
import string
from datetime import datetime


def generate_random_name(email: str) -> str:
    """이메일을 기반으로 랜덤한 5글자를 추가하여 유니크한 이름을 생성"""
    email_id = email.split("@")[0]
    random_chars = "".join(random.choices(string.ascii_uppercase, k=5))
    return f"{email_id}{random_chars}"


def get_current_hour_timestamp() -> datetime:
    return datetime.now().replace(minute=0, second=0, microsecond=0)
