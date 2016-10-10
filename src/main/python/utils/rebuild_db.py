if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from webapp.models.models import db

db.engine.execute("TRUNCATE TABLE vote, comment, pin_tag, tag, pin, \"user\" RESTART IDENTITY")
db.configure_mappers()
db.create_all()
db.session.commit()
