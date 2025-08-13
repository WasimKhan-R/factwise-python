import json
from pathlib import Path
from django.conf import settings
from ..storage import JSONTable
from ..exceptions import BadRequest, NotFound, Conflict
from .utils import now_iso, new_id, ALLOWED_TASK_STATUS

# Import base interface from project root
from project_board_base import ProjectBoardBase

USERS = JSONTable('users.json')
TEAMS = JSONTable('teams.json')
BOARDS = JSONTable('boards.json')

class BoardController(ProjectBoardBase):
    def create_board(self, request: str):
        data = json.loads(request or '{}')
        name = (data.get('name') or '').strip()
        desc = (data.get('description') or '').strip()
        team_id = data.get('team_id')
        if not name:
            raise BadRequest('name is required')
        if len(name) > 64:
            raise BadRequest('board name max 64 chars')
        if len(desc) > 128:
            raise BadRequest('description max 128 chars')
        if not team_id:
            raise BadRequest('team_id is required')
        if not TEAMS.get_by_id(team_id):
            raise BadRequest('team does not exist')
        # unique per team
        for b in BOARDS.read():
            if b['team_id'] == team_id and b['name'].lower() == name.lower():
                raise Conflict('board name must be unique for the team')
        board = {
            'id': new_id('board'),
            'name': name,
            'description': desc,
            'team_id': team_id,
            'status': 'OPEN',
            'creation_time': data.get('creation_time') or now_iso(),
            'end_time': None,
            'tasks': [],
        }
        BOARDS.upsert(board)
        return json.dumps({'id': board['id']})

    def close_board(self, request: str) -> str:
        data = json.loads(request or '{}')
        bid = data.get('id')
        if not bid:
            raise BadRequest('id is required')
        b = BOARDS.get_by_id(bid)
        if not b:
            raise NotFound('board not found')
        if any(t.get('status') != 'COMPLETE' for t in b.get('tasks', [])):
            raise BadRequest('all tasks must be COMPLETE to close the board')
        b['status'] = 'CLOSED'
        b['end_time'] = now_iso()
        BOARDS.upsert(b)
        return json.dumps({'ok': True})

    def add_task(self, request: str) -> str:
        data = json.loads(request or '{}')
        bid = data.get('board_id')  # include board_id in request to target a board
        title = (data.get('title') or '').strip()
        desc = (data.get('description') or '').strip()
        uid = data.get('user_id')
        if not bid:
            raise BadRequest('board_id is required')
        b = BOARDS.get_by_id(bid)
        if not b:
            raise NotFound('board not found')
        if b.get('status') != 'OPEN':
            raise BadRequest('can only add tasks to an OPEN board')
        if not title:
            raise BadRequest('title is required')
        if len(title) > 64:
            raise BadRequest('title max 64 chars')
        if len(desc) > 128:
            raise BadRequest('description max 128 chars')
        if not uid or not USERS.get_by_id(uid):
            raise BadRequest('valid user_id is required')
        for t in b.get('tasks', []):
            if t['title'].lower() == title.lower():
                raise Conflict('task title must be unique for the board')
        task = {
            'id': new_id('task'),
            'title': title,
            'description': desc,
            'user_id': uid,
            'status': 'OPEN',
            'creation_time': data.get('creation_time') or now_iso(),
        }
        b['tasks'].append(task)
        BOARDS.upsert(b)
        return json.dumps({'id': task['id']})

    def update_task_status(self, request: str):
        data = json.loads(request or '{}')
        tid = data.get('id')
        status = data.get('status')
        if not tid or not status:
            raise BadRequest('id and status are required')
        if status not in ALLOWED_TASK_STATUS:
            raise BadRequest('invalid status')
        boards = BOARDS.read()
        updated = False
        for b in boards:
            for t in b.get('tasks', []):
                if t['id'] == tid:
                    t['status'] = status
                    updated = True
                    break
            if updated:
                break
        if not updated:
            raise NotFound('task not found')
        BOARDS.write(boards)
        return json.dumps({'ok': True})

    def list_boards(self, request: str) -> str:
        data = json.loads(request or '{}')
        team_id = data.get('id')
        if not team_id:
            raise BadRequest('team id is required')
        out = [
            {'id': b['id'], 'name': b['name']}
            for b in BOARDS.read()
            if b['team_id'] == team_id and b.get('status') == 'OPEN'
        ]
        return json.dumps(out)

    def export_board(self, request: str) -> str:
        data = json.loads(request or '{}')
        bid = data.get('id')
        if not bid:
            raise BadRequest('id is required')
        b = BOARDS.get_by_id(bid)
        if not b:
            raise NotFound('board not found')
        users = {u['id']: u for u in USERS.read()}
        team = TEAMS.get_by_id(b['team_id'])
        # Build text
        lines = []
        lines.append(f"Board: {b['name']}")
        lines.append(f"Description: {b.get('description', '')}")
        lines.append(f"Team: {team['name'] if team else b['team_id']}")
        lines.append(f"Status: {b.get('status')}")
        lines.append(f"Created: {b.get('creation_time')}")
        lines.append(f"Ended: {b.get('end_time')}")
        lines.append("")
        lines.append("Tasks:")
        tasks = b.get('tasks', [])
        if not tasks:
            lines.append("  (no tasks)")
        else:
            for i, t in enumerate(tasks, 1):
                assignee = users.get(t['user_id'], {}).get('display_name') or t['user_id']
                lines.append(f"  {i}. {t['title']} [{t['status']}] — {assignee}")
                if t.get('description'):
                    lines.append(f"     {t['description']}")
        out_dir = Path(settings.BASE_DIR) / 'out'
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = b['name'].replace(' ', '_')
        fname = f"{safe_name}_{b['id']}.txt"
        (out_dir / fname).write_text('\n'.join(lines), encoding='utf-8')
        return json.dumps({'out_file': fname})
