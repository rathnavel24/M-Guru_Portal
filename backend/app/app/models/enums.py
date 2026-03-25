from sqlalchemy import Enum

user_activity_enum = Enum(
    "active",
    "inactive",
    "deleted",
    name="user_activity",
    create_type=False
)

user_role_enum = Enum('admin', 
                      'student', 
                      name = "user_role",
                      create_type=False
)