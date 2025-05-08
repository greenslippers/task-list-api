from flask import Blueprint, abort, make_response, request, Response
import os
from flask import Blueprint, abort, make_response, request, Response
import requests
from app.models.goal import Goal
from app.models.task import Task
from app.routes.task_routes import validate_task
from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)
        
    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201

@bp.get("")
def get_all_goals():
    query = db.select(Goal)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Goal.title.ilike(f"%{title_param}%"))

    # Handle sorting
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Goal.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Goal.title.desc())
    else:
        query = query.order_by(Goal.id)
    
    # Execute query
    goals = db.session.scalars(query)

    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response

@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_goal(goal_id)
    return {"goal": goal.to_dict()}

@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_goal(goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.post("/<goal_id>/tasks")
def create_task_to_goal(goal_id):
    goal = validate_goal(goal_id)

    request_body = request.get_json()
    task_ids = request_body.get("task_ids")

    if not task_ids or not isinstance(task_ids, list):
        return {"message": f"Invalid request: missing task_ids"}, 400

    # Fetch tasks from DB
    query = db.select(Task).where(Task.id.in_(task_ids))
    tasks = db.session.scalars(query).all()

    # Clear existing tasks and assign only these
    goal.tasks = tasks

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": task_ids
    }, 200

@bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):
    goal = validate_goal(goal_id)
    tasks = [task.to_dict() for task in goal.tasks]
    
    return {
        "id": goal.id,
        "title": goal.title,
        "tasks": tasks
    }, 200

def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except:
        response = {"details": "Invalid data"}   
        abort(make_response(response, 400))
    
    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)

    if not goal:
        response = {"message": f"goal {goal_id} not found"}
        abort(make_response(response, 404))
    return goal
