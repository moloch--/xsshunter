
from sqlalchemy import Column
from sqlalchemy.types import BigInteger, Integer, String, Text

from models.base import DatabaseObject


class Injection(DatabaseObject):

    content_type = Column(String(100))  # JavaScript/Image
    vulnerable_page = Column(String(3000))
    victim_ip = Column(String(100))
    referer = Column(String(3000))
    user_agent = Column(String(3000))
    cookies = Column(String(5000))
    dom = Column(Text())
    origin = Column(String(300))
    screenshot = Column(String(300))
    owner_id = Column(String(100))
    browser_time = Column(BigInteger())
    correlated_request = Column(Text())

    def get_injection_blob(self):
        return {
            "id": self.id,
            "vulnerable_page": self.vulnerable_page,
            "victim_ip": self.victim_ip,
            "referer": self.referer,
            "user_agent": self.user_agent,
            "cookies": self.cookies,
            "dom": self.dom,
            "origin": self.origin,
            "screenshot": self.screenshot,
            "injection_timestamp": str(self.created),
            "correlated_request": self.correlated_request,
            "browser_time": self.browser_time
        }

    def __str__(self):
        return self.vulnerable_page
