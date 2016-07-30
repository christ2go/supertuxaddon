from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
addon = Table('addon', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('automaticmode', BOOLEAN),
    Column('license', String(length=60)),
    Column('author', String(length=60)),
    Column('title', String(length=60)),
)

addon_version = Table('addon_version', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('addon_id', Integer),
    Column('version', String(length=10)),
    Column('changes', Text),
    Column('source', Text),
)

super_tux_versions = Table('super_tux_versions', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('version', String(length=10)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['addon'].create()
    post_meta.tables['addon_version'].create()
    post_meta.tables['super_tux_versions'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['addon'].drop()
    post_meta.tables['addon_version'].drop()
    post_meta.tables['super_tux_versions'].drop()