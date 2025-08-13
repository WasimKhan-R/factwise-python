import json
from ..storage import JSONTable
from ..exceptions import BadRequest, NotFound, Conflict
from .utils import now_iso, new_id

# This will ensure that '.json' exists inside the 'db' directory.
from team_base import TeamBase

USERS = JSONTable('users.json')
TEAMS = JSONTable('teams.json')

class TeamController(TeamBase):
    def create_team(self, request: str) -> str:
        data = json.loads(request or '{}')
        name = (data.get('name') or '').strip()
        desc = (data.get('description') or '').strip()
        admin = data.get('admin')
        if not name:
            raise BadRequest('name is required')
        if len(name) > 64:
            raise BadRequest('name max 64 chars')
        if len(desc) > 128:
            raise BadRequest('description max 128 chars')
        if not admin:
            raise BadRequest('admin user id is required')
        if not USERS.get_by_id(admin):
            raise BadRequest('admin user does not exist')
        for t in TEAMS.read():
            if t['name'].lower() == name.lower():
                raise Conflict('team name must be unique')
        team = {
            'id': new_id('team'),
            'name': name,
            'description': desc,
            'admin': admin,
            'users': [],
            'creation_time': now_iso(),
        }
        TEAMS.upsert(team)
        return json.dumps({'id': team['id']})

    def list_teams(self) -> str:
        return json.dumps([
            {
                'name': t['name'],
                'description': t.get('description', ''),
                'creation_time': t.get('creation_time'),
                'admin': t.get('admin')
            }
            for t in TEAMS.read()
        ])

    def describe_team(self, request: str) -> str:
        data = json.loads(request or '{}')
        tid = data.get('id')
        if not tid:
            raise BadRequest('id is required')
        t = TEAMS.get_by_id(tid)
        if not t:
            raise NotFound('team not found')
        return json.dumps({
            'name': t['name'],
            'description': t.get('description', ''),
            'creation_time': t.get('creation_time'),
            'admin': t.get('admin')
        })

    def update_team(self, request: str) -> str:
        data = json.loads(request or '{}')
        tid = data.get('id')
        if not tid:
            raise BadRequest('id is required')
        t = TEAMS.get_by_id(tid)
        if not t:
            raise NotFound('team not found')
        payload = data.get('team') or {}
        name = (payload.get('name') or t['name']).strip()
        desc = (payload.get('description') or t.get('description', '')).strip()
        admin = payload.get('admin', t.get('admin'))
        if len(name) > 64:
            raise BadRequest('name max 64 chars')
        if len(desc) > 128:
            raise BadRequest('description max 128 chars')
        if admin and not USERS.get_by_id(admin):
            raise BadRequest('admin user does not exist')
        for other in TEAMS.read():
            if other['id'] != tid and other['name'].lower() == name.lower():
                raise Conflict('team name must be unique')
        t.update({'name': name, 'description': desc, 'admin': admin})
        TEAMS.upsert(t)
        return json.dumps({'id': tid})

    def add_users_to_team(self, request: str):
        data = json.loads(request or '{}')
        tid = data.get('id')
        users = data.get('users') or []
        if not tid:
            raise BadRequest('id is required')
        if not isinstance(users, list):
            raise BadRequest('users must be a list')
        t = TEAMS.get_by_id(tid)
        if not t:
            raise NotFound('team not found')
        members = set(t.get('users', []))
        for uid in users:
            if not USERS.get_by_id(uid):
                raise BadRequest(f'user does not exist: {uid}')
            members.add(uid)
            if len(members) > 50:
                raise BadRequest('max 50 users allowed per team')
        t['users'] = list(members)
        TEAMS.upsert(t)
        return json.dumps({'user count': len(t['users'])})

    def remove_users_from_team(self, request: str):
        data = json.loads(request or '{}')
        tid = data.get('id')
        users = set(data.get('users') or [])
        if not tid:
            raise BadRequest('id is required')
        t = TEAMS.get_by_id(tid)
        if not t:
            raise NotFound('team not found')
        members = [u for u in t.get('users', []) if u not in users]
        t['users'] = members
        TEAMS.upsert(t)
        return json.dumps({'user count': len(t['users'])})

    def list_team_users(self, request: str):
        data = json.loads(request or '{}')
        tid = data.get('id')
        if not tid:
            raise BadRequest('id is required')
        t = TEAMS.get_by_id(tid)
        if not t:
            raise NotFound('team not found')
        out = []
        user_map = {u['id']: u for u in USERS.read()}
        for uid in t.get('users', []):
            u = user_map.get(uid)
            if u:
                out.append({'id': u['id'], 'name': u['name'], 'display_name': u.get('display_name', '')})
        return json.dumps(out)
