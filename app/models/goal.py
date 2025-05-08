from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.task import Task 

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    # converts a Goal instance into a dict 
    # for generating JSON response
    def to_dict(self): 
        goal_as_dict = {
            "id": self.id,
            "title": self.title
            # "tasks": [task.to_dict() for task in self.tasks]
        }

        return goal_as_dict
    
    # creates a new Goal model instance from a dictionary
    @classmethod 
    def from_dict(cls, goal_data):
        new_goal = Goal(title=goal_data["title"]
                        )
        return new_goal
    
