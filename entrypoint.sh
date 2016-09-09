#! /bin/bash
python3 github-webhook.py &
uwsgi --master --pidfile=/tmp/project-master.pid --http 0.0.0.0:5000 --wsgi-file src/son_editor/app/__main__.py --callable app --processes 1 --threads 8 &
