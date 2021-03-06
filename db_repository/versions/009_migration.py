from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
addon = Table('addon', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('automaticmode', BOOLEAN),
    Column('license', String(length=60)),
    Column('author', String(length=60)),
    Column('title', String(length=60)),
    Column('description', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['addon'].columns['description'].create()
    post_meta.tables['addon'].columns['name'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['addon'].columns['description'].drop()
    post_meta.tables['addon'].columns['name'].drop()
