import sqlite3

from flask import g

import fixtures
from settings import app


def connect():
    session = sqlite3.connect(app.config['DATABASE'])
    session.row_factory = sqlite3.Row
    session.text_factory = str

    return session


def open_session():
    if not hasattr(g, 'database_session'):
        g.sqlite_db = connect()

    return g.sqlite_db


@app.teardown_appcontext
def close_session(error):
    '''
    Auto cleanup of database connection at the end of every request
    '''

    if hasattr(g, 'database_session'):
        g.database_session.close()


def create_tables():
    with app.app_context():
        database_session = open_session()

        # Create schema
        with app.open_resource('database/schema.sql', mode='r') as schema:
            database_session.cursor().executescript(schema.read())
        database_session.commit()

        # Initialize data
        for text in fixtures.texts:
            database_session.execute(
                'insert into texts (identifier, content, published) values (?, ?, ?)',
                [text['identifier'], text['content'], text['published']]
            )
            database_session.commit()

        for image in fixtures.images:
            database_session.execute(
                'insert into images (identifier, filename, published) values (?, ?, ?)',
                [image['identifier'], image['filename'], image['published']]
            )
            database_session.commit()

        for container in fixtures.containers:
            database_session.execute(
                'insert into containers (identifier, size, published) values (?, ?, ?)',
                [container['identifier'], container['size'], container['published']]
            )
            database_session.commit()

        database_session.execute(
            'insert into mapbox (geojson) values (?)',
            [fixtures.mapbox['geojson']]
        )
        database_session.commit()
