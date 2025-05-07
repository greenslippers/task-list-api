from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..db import db
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.goal import Goal 

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    # converts a Task instance into a dict 
    # for generating JSON response
    def to_dict(self): 
        task_as_dict = {}
        task_as_dict["id"] = self.id
        task_as_dict["title"] = self.title
        task_as_dict["description"] = self.description
        task_as_dict["is_complete"] = self.completed_at is not None

        if self.goal:
            task_as_dict["goal"] = self.goal.name

        return task_as_dict
    
    # creates a new Task model instance from a dictionary
    @classmethod 
    def from_dict(cls, task_data):
        goal_id = task_data.get("goal_id")

        new_task = cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=task_data.get("completed_at"), # use .get() to allow missing field
            goal_id=goal_id
            )

        return new_task
    