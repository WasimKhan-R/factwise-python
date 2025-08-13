from django.urls import path
from .views import (
    UsersView, UserDetailView, UserTeamsView,
    TeamsView, TeamDetailView, TeamUsersView, TeamUsersAddView, TeamUsersRemoveView,
    BoardsCreateView, TeamOpenBoardsView, BoardCloseView, BoardAddTaskView, TaskStatusView, BoardExportView,
)

urlpatterns = [
    # Users
    path('users/', UsersView.as_view()),  # GET list, POST create
    path('users/<str:user_id>/', UserDetailView.as_view()),
    path('users/<str:user_id>/teams/', UserTeamsView.as_view()),

    # Teams
    path('teams/', TeamsView.as_view()),   # GET list, POST create
    path('teams/<str:team_id>/', TeamDetailView.as_view()),
    path('teams/<str:team_id>/users/', TeamUsersView.as_view()),
    path('teams/<str:team_id>/users/add/', TeamUsersAddView.as_view()),
    path('teams/<str:team_id>/users/remove/', TeamUsersRemoveView.as_view()),

    # Boards
    path('boards/', BoardsCreateView.as_view()),   # POST create
    path('teams/<str:team_id>/boards/', TeamOpenBoardsView.as_view()),
    path('boards/<str:board_id>/close/', BoardCloseView.as_view()),
    path('boards/<str:board_id>/tasks/', BoardAddTaskView.as_view()),
    path('tasks/<str:task_id>/status/', TaskStatusView.as_view()),
    path('boards/<str:board_id>/export/', BoardExportView.as_view()),
]
