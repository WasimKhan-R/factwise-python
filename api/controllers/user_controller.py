import json
from ..storage import JSONTable
from ..exceptions import BadRequest, NotFound, Conflict
from .utils import now_iso, new_id

from user_base import UserBase

# This will ensure that '.json' exists inside the 'db' directory.
USERS = JSONTable('users.json')
TEAMS = JSONTable('teams.json')

class UserController(UserBase):
    def create_user(self, request: str) -> str:
        """Create a new user and return its ID as a JSON string."""

        # Parse request data
        data = json.loads(request or '{}')
        name = (data.get('name') or '').strip()
        display = (data.get('display_name') or '').strip()

        # Input validation
        if not name:
            raise BadRequest('name is required')
        if len(name) > 64:
            raise BadRequest('name max 64 chars')
        if len(display) > 64:
            raise BadRequest('display_name max 64 chars')
        
        # Uniqueness
        for u in USERS.read():
            if u['name'].lower() == name.lower():
                raise Conflict('user name must be unique')

        # Create user.
        user = {
            'id': new_id('usr'),
            'name': name,
            'display_name': display,
            'creation_time': now_iso(),
            'description': data.get('description') or ''
        }
        USERS.upsert(user)
        return json.dumps({'id': user['id']})

    def list_users(self) -> str:
        """Return all users as a JSON string for the UsersView GET endpoint."""

        users = USERS.read()
        result = [
            {
                'name': u['name'],
                'display_name': u.get('display_name', ''),
                'creation_time': u.get('creation_time')
            }
            for u in users
        ]
        return json.dumps(result)

    def describe_user(self, request: str) -> str:
        """Return details of a user as a JSON string based on user ID."""

        data = json.loads(request or '{}')
        uid = data.get('id')
        if not uid:
            raise BadRequest('id is required')
        u = USERS.get_by_id(uid)
        if not u:
            raise NotFound('user not found')
        return json.dumps({
            'name': u['name'],
            'description': u.get('description', ''),
            'creation_time': u.get('creation_time')
        })

    def update_user(self, request: str) -> str:
        """Update an existing user's details and return confirmation as JSON."""

        data = json.loads(request or '{}')
        uid = data.get('id')
        payload = data.get('user') or {}
        if not uid:
            raise BadRequest('id is required')
        u = USERS.get_by_id(uid)
        if not u:
            raise NotFound('user not found')
        # Name cannot be updated
        if 'name' in payload and payload['name'] != u['name']:
            raise BadRequest('user name cannot be updated')
        display = (payload.get('display_name') or u.get('display_name', '')).strip()
        if len(u.get('name', '')) > 64:
            raise BadRequest('name max 64 chars')
        if len(display) > 128:
            raise BadRequest('display_name max 128 chars')
        u['display_name'] = display
        if 'description' in payload:
            u['description'] = (payload.get('description') or '').strip()
        USERS.upsert(u)
        return json.dumps({'id': uid})

    def get_user_teams(self, request: str) -> str:
        data = json.loads(request or '{}')
        uid = data.get('id')
        if not uid:
            raise BadRequest('id is required')
        teams = []
        seen = set()
        for t in TEAMS.read():
            members = set(t.get('users', []))
            if uid == t.get('admin') or uid in members:
                if t['id'] in seen:
                    continue
                seen.add(t['id'])
                teams.append({
                    'name': t['name'],
                    'description': t.get('description', ''),
                    'creation_time': t.get('creation_time')
                })
        return json.dumps(teams)
