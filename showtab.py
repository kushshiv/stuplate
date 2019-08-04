#!/Users/shivendra/Desktop/stuplate/venv/bin/python

from app import db
print(db.engine.table_names())
