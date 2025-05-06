from datetime import datetime
import os
from flask import Blueprint, abort, make_response, request, Response
import requests
from app.models.task import Task
from ..db import db

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)
        
    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

@bp.get("")
def get_all_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    # Handle sorting
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.id)
    
    # Execute query
    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())

    return tasks_response

@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)
    return {"task": task.to_dict()}

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    task.completed_at = request_body.get("completed_at")
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_task(task_id)
    task.completed_at = datetime.now()

    send_slack_message(f"Someone just completed the task {task.title}")

    db.session.commit()
    return Response(status=204, mimetype="application/json")

@bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_task(task_id)
    task.completed_at = None

    db.session.commit()
    return Response(status=204, mimetype="application/json")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"details": "Invalid data"}   
        abort(make_response(response, 400))
    
    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": f"task {task_id} not found"}
        abort(make_response(response, 404))
    return task

def send_slack_message(message_text):
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_CHANNEL_ID")

    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": channel,
        "text": message_text
    }

    response = requests.post(
        "https://slack.com/api/chat.postMessage", headers=headers, json=payload
        )