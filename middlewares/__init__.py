from loader import dp

from .database import GetDBUser
from .check_access import IsPrivateChat, IsUserHaveAccess
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(IsPrivateChat())
    dp.middleware.setup(GetDBUser())
    dp.middleware.setup(IsUserHaveAccess())
