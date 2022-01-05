'''
App entry point
'''
from flask import redirect, url_for
from app import create_app, graphql, sio
from flask_graphql import GraphQLView
from app.graphql.schema import schema

app = create_app('dev')

logstr = '{}\n\033[92m{}\033[00m\n\033[92m{}\033[00m'

@app.route('/')
def docs():
    return redirect(url_for('api.doc'))

app.add_url_rule('/api/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
    graphiql_version = '',
    graphiql_html_title = 'Logstr-Graphql',
    #graphiql_template = '<link rel="stylesheet" href="/static/css/styles.css"/>'
))

if __name__ == "__main__":
    print(logstr.format('📦  LOGSTR API','[*] Ran system checks','[+] Starting api ...'))
    sio.run(
        app = app,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG')
    )