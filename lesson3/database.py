from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import gbmodels

engine = create_engine('sqlite:///gb_blog.db')
gbmodels.Base.metadata.create_all(bind=engine)

SessionMaker = sessionmaker(bind=engine)

if __name__ == '__main__':
    db = SessionMaker()
