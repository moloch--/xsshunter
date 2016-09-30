from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Text


class InjectionRequest(Base):

    request = Column(Text())
    injection_key = Column(String(100))
    owner_correlation_key = Column(String(100))

    def get_injection_blob(self):
        return {
            "request": self.request,
            "injection_key": self.injection_key
        }

    def __str__(self):
        return self.id
