from app import app, db
from app.models import User, Item, Group, GroupMembership

@app.shell_context_processor
def make_shell_context():
    return {'db'             : db,
            'User'           : User,
            'Item'           : Item,
            'Group'          : Group,
            'GroupMembership': GroupMembership}