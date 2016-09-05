import contextlib

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from son.editor.app.util import CONFIG

# DB URI
DATABASE_SQLITE_URI = "sqlite:///%s" % CONFIG['database']['location']
print("DBSQLITE_URI: " + DATABASE_SQLITE_URI)

engine = create_engine(DATABASE_SQLITE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import son.editor.models.project
    import son.editor.models.user
    import son.editor.models.workspace
    import son.editor.models.service
    import son.editor.models.function
    Base.metadata.create_all(bind=engine)


# Resets the database
def reset_db():
    meta = MetaData()

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()
