import os

from flask import session, request
from flask.ext.restful import Resource, abort, reqparse

import database
from settings import api, app


class Text(Resource):
    def get(self, identifier):
        if not session.get('logged_in'):
            abort(401, message='Login required.')

        database_session = database.open_session()
        cursor = database_session.execute(
            'select content from texts where identifier=? and published=0',
            [identifier]
        )
        content = cursor.fetchone()

        if content is None:
            abort(404, message='Invalid text identifier %s.' % identifier)
        else:
            content = content[0]

        return {
            'identifier': identifier,
            'content': content
        }, 200

    def post(self, identifier):
        if not session.get('logged_in'):
            abort(401, message='Login required.')

        database_session = database.open_session()
        cursor = database_session.execute(
            'select content from texts where identifier=? and published=0',
            [identifier]
        )
        content = cursor.fetchone()

        if content is None:
            abort(404, message='Invalid text identifier %s.' % identifier)
        else:
            content = content[0]

        request_parser = reqparse.RequestParser()
        request_parser.add_argument('content', type=unicode)
        post_data = request_parser.parse_args()
        content = post_data.get('content', None)

        if content is None:
            abort(400, message='JSON key "content" is required.')

        database_session.execute(
            'update texts set content=? where identifier=? and published=0',
            [content, identifier]
        )
        database_session.commit()

        return {
            'identifier': identifier,
            'content': content
        }, 201


class Image(Resource):
    def post(self, identifier):
        if not session.get('logged_in'):
            abort(401, message='Login required.')

        file = request.files['files[]']
        filename = file.filename

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        database_session = database.open_session()
        database_session.execute(
            'update images set filename=? where identifier=? and published=0',
            [filename, identifier]
        )
        database_session.commit()

        return {
            'identifier': identifier,
            'filename': filename
        }, 201


class Container(Resource):
    def post(self, identifier):
        if not session.get('logged_in'):
            abort(401, message='Login required.')

        request_parser = reqparse.RequestParser()
        request_parser.add_argument('mode', type=unicode)
        post_data = request_parser.parse_args()
        mode = post_data.get('mode', None)

        if mode is None:
            abort(400, message='JSON key "mode" is required.')

        if mode not in ('+', '-'):
            abort(400, message='Valid "mode" values are "+" or "-".')

        database_session = database.open_session()
        cursor = database_session.execute(
            'select size from containers where identifier=? and published=0',
            [identifier]
        )
        size = cursor.fetchone()

        if size is None:
            abort(404, message='Invalid container identifier %s.' % identifier)
        else:
            size = size[0]

        if (mode == '+') and (size < 6):
            size += 1
        elif (mode == '-') and (size > 1):
            size -= 1

        database_session.execute(
            'update containers set size=? where identifier=? and published=0',
            [size, identifier]
        )
        database_session.commit()

        return {
            'identifier': identifier,
            'mode': mode
        }, 201


class MapBox(Resource):
    def get(self):
        if not session.get('logged_in'):
            abort(401, message='Login required.')

        database_session = database.open_session()
        cursor = database_session.execute(
            'select geojson from mapbox where id=1')
        geojson = cursor.fetchone()[0]

        return {
            'geojson': geojson
        }, 200

    def post(self):
        if not session.get('logged_in'):
            abort(401, message='Login required.')

        database_session = database.open_session()
        cursor = database_session.execute(
            'select geojson from mapbox where id=1')
        content = cursor.fetchone()[0]

        request_parser = reqparse.RequestParser()
        request_parser.add_argument('geojson', type=unicode)
        post_data = request_parser.parse_args()
        geojson = post_data.get('geojson', None)

        database_session.execute(
            'update mapbox set geojson=? where id=1', [geojson])
        database_session.commit()

        return {
            'geojson': geojson
        }, 201


api.add_resource(Text, '/edit/text/<string:identifier>')
api.add_resource(Image, '/edit/image/<string:identifier>')
api.add_resource(Container, '/edit/container/<string:identifier>')
api.add_resource(MapBox, '/edit/mapbox/geojson')
