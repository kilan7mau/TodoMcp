import logging
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """Kết nối tới MongoDB Atlas"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.db = cls.client[settings.DATABASE_NAME]
            # Kiểm tra kết nối bằng lệnh ping
            await cls.client.admin.command('ping')
            logger.info("Đã kết nối thành công tới MongoDB Atlas")
        except Exception as e:
            logger.error(f"Lỗi khi kết nối tới MongoDB: {e}")
            raise e

    @classmethod
    async def close(cls):
        """Đóng kết nối MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("Đã đóng kết nối MongoDB")

    @classmethod
    def get_collection(cls):
        """Lấy collection tasks"""
        return cls.db[settings.COLLECTION_NAME]

db = MongoDB()
