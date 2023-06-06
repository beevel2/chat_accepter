from aiogram.utils import executor

from handlers import setup_handlers
from settings import dp
import middleware
from scheduler import scheduler, add_scheduler_tasks


def on_startup():
    setup_handlers(dp)
    scheduler.start()


if __name__ == '__main__':
    on_startup()
    dp.middleware.setup(middleware.UserIsAdminMiddleware())
    dp.middleware.setup(middleware.AlbumMiddleware())

    executor.start_polling(dp, on_startup=add_scheduler_tasks)
