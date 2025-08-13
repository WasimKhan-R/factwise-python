# Create your views here.
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .controllers.user_controller import UserController
from .controllers.team_controller import TeamController
from .controllers.board_controller import BoardController
from .exceptions import BadRequest, NotFound, Conflict

U = UserController()
T = TeamController()
B = BoardController()

def _ok(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)
    return Response(payload)

# Handle Response
def _handle(fn, *args, **kwargs):
    try:
        return _ok(fn(*args, **kwargs))
    except BadRequest as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Conflict as e:
        return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
    except NotFound as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

# Users View
class UsersView(APIView):
    def get(self, request):
        return _handle(U.list_users)
    def post(self, request):
        return _handle(U.create_user, json.dumps(request.data))

class UserDetailView(APIView):
    def get(self, request, user_id):
        return _handle(U.describe_user, json.dumps({'id': user_id}))
    def patch(self, request, user_id):
        body = {'id': user_id, 'user': request.data}
        return _handle(U.update_user, json.dumps(body))

class UserTeamsView(APIView):
    def get(self, request, user_id):
        return _handle(U.get_user_teams, json.dumps({'id': user_id}))

# Teams View
class TeamsView(APIView):
    def get(self, request):
        return _handle(T.list_teams)
    def post(self, request):
        return _handle(T.create_team, json.dumps(request.data))

class TeamDetailView(APIView):
    def get(self, request, team_id):
        return _handle(T.describe_team, json.dumps({'id': team_id}))
    def patch(self, request, team_id):
        body = {'id': team_id, 'team': request.data}
        return _handle(T.update_team, json.dumps(body))

class TeamUsersView(APIView):
    def get(self, request, team_id):
        return _handle(T.list_team_users, json.dumps({'id': team_id}))

class TeamUsersAddView(APIView):
    def post(self, request, team_id):
        body = {'id': team_id, 'users': request.data.get('users', [])}
        return _handle(T.add_users_to_team, json.dumps(body))

class TeamUsersRemoveView(APIView):
    def post(self, request, team_id):
        body = {'id': team_id, 'users': request.data.get('users', [])}
        return _handle(T.remove_users_from_team, json.dumps(body))

# Boards View
class BoardsCreateView(APIView):
    def post(self, request):
        return _handle(B.create_board, json.dumps(request.data))

class TeamOpenBoardsView(APIView):
    def get(self, request, team_id):
        return _handle(B.list_boards, json.dumps({'id': team_id}))

class BoardCloseView(APIView):
    def post(self, request, board_id):
        return _handle(B.close_board, json.dumps({'id': board_id}))

class BoardAddTaskView(APIView):
    def post(self, request, board_id):
        body = dict(request.data)
        body['board_id'] = board_id
        return _handle(B.add_task, json.dumps(body))

class TaskStatusView(APIView):
    def patch(self, request, task_id):
        body = {'id': task_id, 'status': request.data.get('status')}
        return _handle(B.update_task_status, json.dumps(body))

class BoardExportView(APIView):
    def post(self, request, board_id):
        return _handle(B.export_board, json.dumps({'id': board_id}))
