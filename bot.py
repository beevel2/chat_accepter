from aiogram.utils import executor

from handlers import setup_handlers
from handlers.default import client_pool
from settings import dp, allowed_updates
import middleware
from scheduler import scheduler, add_scheduler_tasks


def on_startup():
    setup_handlers(dp)
    scheduler.start()

async def on_shutdown(_):
    for client in client_pool:
        await client['app'].stop()

if __name__ == '__main__':
    on_startup()
    dp.middleware.setup(middleware.UserIsAdminMiddleware())
    dp.middleware.setup(middleware.AlbumMiddleware())

    executor.start_polling(dp, allowed_updates=allowed_updates, on_startup=add_scheduler_tasks, on_shutdown=on_shutdown)
