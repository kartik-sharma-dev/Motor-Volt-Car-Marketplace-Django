#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python -c "
import json
data = json.load(open('data.json'))
keep = [x for x in data if x['model'].startswith('login.')]
json.dump(keep, open('demo_data.json', 'w'))
print(f'Kept {len(keep)} of {len(data)} fixture objects')
"
python manage.py loaddata demo_data.json
