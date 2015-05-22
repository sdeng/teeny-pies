from flask import render_template, url_for, redirect, flash, session

import database
from settings import app


@app.route('/edit')
def edit(edit_mode=True):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    database_session = database.open_session()
    cursor = database_session.execute(
        'select identifier, content from texts where published=0')
    texts = cursor.fetchall()
    cursor = database_session.execute(
        'select identifier, filename from images where published=0')
    images = cursor.fetchall()
    cursor = database_session.execute(
        'select identifier, size from containers where published=0')
    containers = cursor.fetchall()
    cursor = database_session.execute(
        'select geojson from mapbox where id=1')
    geojson = cursor.fetchone()[0]

    context = {
        'edit_mode': edit_mode,
        'geojson': geojson
    }
    for identifier, content in texts:
        context[identifier] = content.decode('utf-8')
    for identifier, filename in images:
        context[identifier] = filename.decode('utf-8')
    for identifier, size in containers:
        context[identifier] = []
        if identifier == 'pie_container_1':
            offset = 0
        else:
            offset = 6
        for i in range(1, 7):
            index = i + offset
            context[identifier].append({
                'index': index,
                'pie_picture': context['pie_picture_%s' % index],
                'pie_name': context['pies_name_%s' % index],
                'pie_price': context['pies_price_%s' % index],
                'hidden': True if (i > size) else False
            })

    print 'Finished processing'
    return render_template(
        'index.html',
        context=context
    )


@app.route('/edit/reset')
def reset():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Fetch currently published text blurbs
    database_session = database.open_session()
    cursor = database_session.execute(
        'select identifier, content from texts where published=1'
    )
    published_texts = cursor.fetchall()

    # Replace unpublished blurbs with published counterparts
    for identifier, content in published_texts:
        database_session.execute(
            'update texts set content=? where identifier=? and published=0',
            [content, identifier]
        )
        database_session.commit()

    # Redirect back to edit page, with flash message
    flash('Starting over!')
    return redirect(url_for('edit'))


@app.route('/publish')
def publish():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Update publisehd blurbs in the database with edited versions
    database_session = database.open_session()
    cursor = database_session.execute(
        'select identifier, content from texts where published=0'
    )
    unpublished_texts = cursor.fetchall()

    for identifier, content in unpublished_texts:
        database_session.execute(
            'update texts set content=? where identifier=? and published=1',
            [content, identifier]
        )
        database_session.commit()

    response = edit(edit_mode=False)
    publish_path = app.root_path + '/../static/index.html'

    with open(publish_path, 'w') as output_html:
        unicode_response = u'%s' % response
        output_html.write(unicode_response.encode('utf-8'))

    return redirect(app.config['SITE_URL'])
