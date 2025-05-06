from sqlalchemy.orm import Mapped, mapped_column
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]

    # converts a Goal instance into a dict 
    # for generating JSON response
    def to_dict(self): 
        goal_as_dict = {}
        goal_as_dict["id"] = self.id
        goal_as_dict["title"] = self.title

        return goal_as_dict
    
    # creates a new Goal model instance from a dictionary
    @classmethod 
    def from_dict(cls, goal_data):
        new_goal = Goal(title=goal_data["title"]
                        )
        return new_goal
    
