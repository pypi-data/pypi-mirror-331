# -*- coding: utf8 -*-

"hikepy工具类"

__author__ = "hnck2000@126.com"
import os
import pkgutil
import importlib
import inspect
from datetime import datetime,timedelta
import redis
import jwt
from redis import ConnectionPool, Redis, RedisError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, Executable,func,select
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase

from .hklogger import hklog
from .model import SqlModel,PageList,AuthInfo
from .config import config

def create_token(data:AuthInfo,days:int=config.ACCESS_TOKEN_EXPIRE_DAYS)->str:
    """生成认证token"""
    pdict=data.model_dump()
    pdict["exp"]=datetime.now() + timedelta(days=days)
    return jwt.encode(pdict, config.SECRET_KEY, algorithm=config.ALGORITHM)

class HkCache:
    """缓存客户端工具栏"""

    def __init__(self):
        self.pool: ConnectionPool = None

    def __del__(self):
        if self.pool:
            self.pool.disconnect()

    def init(self, host: str, port: int, password: str, decode_responses=True,db:int=0):
        """缓存连接池初始化"""
        try:
            self.pool = redis.ConnectionPool(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=decode_responses
            )
        except RedisError as ext:
            hklog.error(f"cache init faild error:{str(ext)}")

    def client(self) -> Redis:
        """获取redis客户端"""
        if self.pool:
            return redis.Redis(connection_pool=self.pool)


hkcache = HkCache()


class HkDatabaseManager:
    """数据库连接管理类"""

    def __init__(self):
        self.engine: AsyncEngine = None
        self.async_session_factory: sessionmaker = None
        self.models: list[SqlModel] = []

    # def __del__(self):
    #     if self.engine is not None:
    #         self.engine.dispose()

    def init(self, url: str, pool_size: int = 5, max_overflow=10, pool_timeout=30):
        """数据库初始化"""
        try:
            self.engine = create_async_engine(
                url,
                echo=True,
                future=True,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
            )
            self.async_session_factory = async_sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
        except SQLAlchemyError as ext:
            hklog.error(f"database init faild error:{str(ext)}")

    def create_session(self) -> AsyncSession:
        """获取sql工具类"""
        return self.async_session_factory()

    def scan_models(self, model_root: str, pkg_path: str):
        """扫描指定包下的路由文件"""
        for module in pkgutil.walk_packages([model_root], pkg_path + "."):
            if module.ispkg:
                self.scan_models(os.path.join(model_root, module.name), module.name)
            else:
                if module.name.split(".")[-1] == "models":
                    module = importlib.import_module(module.name)
                    for name, value in module.__dict__.items():
                        if (
                            name != "SqlModel"
                            and inspect.isclass(value)
                            and issubclass(value, SqlModel)
                        ):
                            self.models.append(value)

          

    async def register_database(self, model_root: str, pkg_path: str):
        """初始化创建数据库"""
        if self.engine:
            self.scan_models(model_root, pkg_path)
            async with self.engine.begin() as conn:
                for md in self.models:
                    await conn.run_sync(md.__table__.create, checkfirst=True)


hk_db_manager = HkDatabaseManager()

class HkMongoManager:
    """Mongo连接管理类"""
    def __init__(self):
        self.client:AsyncIOMotorClient=None
        self.db:Mogo=None
        self.database:str=""

    def __del__(self):
        if self.client is not None:
            self.client.close()

    def init(self, url: str,database:str):
        """mogo初始化"""
        try:
            self.client= AsyncIOMotorClient(url)
            self.database=database
            self.db=self.client[database]
        except Exception as error:
            hklog.error(f"mogo init faild error:{str(error)}")




hk_mogo_manager = HkMongoManager()

class Sql:
    """数据库操作工具类"""

    def __init__(self, session: AsyncSession):
        self.session = session
        hklog.info("reject session width autocommit")

    async def exec(self, sql: str, param: dict | None = None):
        """执行原生SQL"""
        return await self.session.execute(text(sql), param)

    async def execute(
        self, statement: Executable, params: _CoreAnyExecuteParams | None = None
    ):
        """execute"""
        return await self.session.execute(statement, params)

    async def scalars(
        self, statement: Executable, params: _CoreAnyExecuteParams | None = None
    ):
        """scalars"""
        return await self.session.scalars(statement, params)

    async def scalar(
        self, statement: Executable, params: _CoreAnyExecuteParams | None = None
    ):
        """scalars"""
        return await self.session.scalar(statement, params)

    async def get(self, *args, **kwargs):
        """get"""
        return await self.session.get(*args, **kwargs)

    def add(self, instance: object, _warn: bool = True):
        """add"""
        return self.session.add(instance, _warn)

    async def delete(self, instance: object):
        """add"""
        return await self.session.delete(instance)

    async def merge(self, *args, **kwargs):
        """merge"""
        return await self.session.merge(*args, **kwargs)

    async def run_sync(self, *args, **kwargs):
        """run_sync"""
        return await self.session.run_sync(*args, **kwargs)
    
    async def page(self, statement: Executable, params: _CoreAnyExecuteParams | None = None,current_page:int=1,page_size:int=20):
        """分页查询"""
        if statement.is_select:
            total_count=await self.session.scalar(select(func.count("*")).select_from(statement),params)
            result=await self.scalars(statement.offset((current_page - 1) * page_size).limit(page_size), params)
            return PageList.create(datas=result.fetchall(),current_page=current_page,total_size=total_count,page_size=page_size)
        else:
            return PageList.create([])
        

class Mogo(AsyncIOMotorDatabase):
    """Mogodb操作工具类"""
