from enum import Enum


class UserType(str, Enum):
    SUPER_ADMIN = "Super Admin"
    Admin = "Admin"
    User = "User"


class Permissions(str, Enum):
    MANAGE_USERS = "Manage Users"
    MANAGE_BLOGS = "Manage Blogs"


class OtpPurpose(str, Enum):
    VERIFY_EMAIL = "Verify Email"
    RESET_PASSWORD = "Reset Password"
