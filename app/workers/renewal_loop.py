import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.adapters.payments.yookassa_api import YookassaAPI
from app.workers.subs_checker import SubscriptionChecker
from app.config import Settings
from app.db.base import create_engine_and_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Settings()
engine, session_factory = create_engine_and_session(config)
yookassa_api = YookassaAPI(config.yookassa_shop_id, config.yookassa_secret_key)

class SubsScheduler:
    @staticmethod
    async def process():
        async with session_factory() as session:
            await SubscriptionChecker.process(session=session, yookassa_api=yookassa_api)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(SubsScheduler.process, CronTrigger(minute="*"))
    scheduler.start()
    await SubsScheduler.process()
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())
