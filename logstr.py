'''
App entry point
'''
from app import create_app, sio

app = create_app('dev')

logstr = '{}\n\033[92m{}\033[00m\n\033[92m{}\033[00m'


if __name__ == "__main__":
    print(logstr.format('📦  LOGSTR API','[*] Ran system checks','[+] Starting api ...'))
    sio.run(
        app = app,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG')
    )