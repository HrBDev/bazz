from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileInfo(Base):
    __tablename__ = "file_info"
    pkg_name = Column(String, primary_key=True)
    sha256 = Column(String)
