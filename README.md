# Team Project Planner API

## Overview

This project implements a **Team Project Planner** using Django.  
It provides APIs to manage:
- Users
- Teams
- Project boards and tasks  

Data is persisted in **local JSON files** inside the `db/` folder.  
The user interacts only via API endpoints and is not exposed to the underlying file storage.

---

## Python Version Compatibility: Python 3.12+

---

## Features

- Create, list, describe, and update users
- Create, list, describe, and update teams
- Create and manage project boards
- Add tasks to boards and update task status
- Export boards to a presentable `.txt` file
- JSON file-based local persistence with file locking

---

## Project Structure

factwise-python/
├── api/                     # Django API views and controllers
├── db/                      # JSON files (users.json, teams.json, boards.json)
├── out/                     # Exported board files
├── factwise_python_project/ # Django project settings
├── project_board_base.py     # Base abstract classes
├── team_base.py              # Base class for teams
├── user_base.py              # Base class for users
├── manage.py
├── README.md
├── requirements.txt
└── venv/                    # Python virtual environment

---

## Design Choices / Thought Process

## 1. Separation of Concerns:
Views handle HTTP requests; controllers/services handle all business logic.

## 2. Unique ID Generation:
All entities (users, teams, boards) have unique IDs (usr_, team_, board_).
Existing IDs are checked before creating a new one to prevent collisions.

## 3.API Design:
Consistent JSON input/output.
POST requests used for actions requiring data, including describe/update actions.

## 4. Extensibility & Modularity:
Base classes (UserBase, TeamBase, ProjectBoardBase) allow future extensions.
Adding new entities or APIs follows the same structured pattern.

---

## Installation

## 1. Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

## 2. Install dependencies:

pip install -r requirements.txt

## 3. Run the Django server:

python manage.py runserver


---
