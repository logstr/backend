[![Python](https://img.shields.io/badge/python-2.7%2C%203.5%2C%203.6--dev-blue.svg)]()
[![Docker](https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg?maxAge=2592000)]()

# Logstr Api
Logstr api is the api backend for the `logstr team`. It collects data from npm package linked on a website. It handles request authprization and authentication, data storage from heatmap.
## Rules

- Do not share code with unauthorized personnels.
- Make sure you send commits to branches with proper commit messages.
- Comment code properly before commit.
- Create pull requests and talk with teams.
- **DO NOT PUSH** to **MASTER** Branch.


## Getting started

Install [Python](https://www.python.org/downloads/) and run code below, for the standalone web service:

```shell
pipenv install -r requirements.txt
python logstr.py
```

-- Visit [http://localhost:5000/api/docs](http://localhost:5000/api/docs)

To create models run the following command:

For Windows
```shell
set FLASK_APP=logstr.py
flask db init
flask db migrate
flask db upgrade
```
For MacOs and Linux
```shell

export FLASK_APP=logstr.py

flask db init
flask db migrate
flask db upgrade
```

## Development

Create a new branch off the **master** branch for features or fixes.

After making changes rebuild images and run the app:

```shell
docker-compose build
docker-compose run -p 5000:5000 web python logstr.py
```

## Tests

Tests are not a priority so skip tests if possible.
Standalone unit tests run with:

```shell
pip install pytest pytest-cov pytest-flask
pytest --cov=web/ --ignore=tests/integration tests
```

Integration with docker:

```shell
docker-compose build
docker-compose up
```

Integration and unit tests run with:

```shell
docker-compose -f test.yml -p ci build
docker-compose -f test.yml -p ci run test python -m pytest --cov=web/ tests
# docker stop ci_redis_1 ci_web_1
```

After testing, submit a pull request to merge changes with **master**.