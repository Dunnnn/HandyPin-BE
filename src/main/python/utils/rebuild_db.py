if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from webapp.models.models import db

db.engine.execute("DROP TABLE IF EXISTS vote, comment, pin_tag, tag, pin, \"user\"")
db.engine.execute("DROP FUNCTION IF EXISTS tag_search_vector_update()")
db.engine.execute("DROP FUNCTION IF EXISTS user_search_vector_update()")
db.engine.execute("DROP FUNCTION IF EXISTS pin_search_vector_update()")
db.engine.execute("DROP SEQUENCE IF EXISTS vote_id_seq, comment_id_seq, pin_tag_id_seq, tag_id_seq, pin_id_seq, user_id_seq")


db.configure_mappers()
db.create_all()
db.session.commit()
