import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from tortoise import Tortoise, fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.models import Model
import asyncio

from fastapi_tortoise_crud import ModelCrud
from fastapi_tortoise_crud.cache.cache import CacheManager
from .mock_redis import MockRedis
from ..models import User

# 测试模型
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)
    
    class Meta:
        table = "users"
        table_title = "用户"

@pytest.fixture
async def init_db():
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'models': ['tests.test_cache']}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest.fixture
def app():
    app = FastAPI()
    register_tortoise(
        app,
        db_url='sqlite://:memory:',
        modules={'models': ['tests.test_cache']},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_redis():
    return MockRedis()

@pytest.fixture
async def cache_manager():
    manager = CacheManager(
        redis_url="redis://localhost:6379/1",  # 使用测试数据库
        prefix="test:",
        default_ttl=60
    )
    await manager.initialize()
    yield manager
    await manager.close()

@pytest.fixture
async def test_user():
    user = await User.create(
        username="test_user",
        email="test@example.com",
        password="password123"
    )
    yield user
    await user.delete()

def test_cache_manager_initialization(cache_manager, mock_redis):
    assert cache_manager.redis_client == mock_redis

@pytest.mark.asyncio
async def test_cache_crud_operations(app, client, cache_manager, init_db):
    # 创建用户 CRUD 实例
    user_crud = ModelCrud(
        model=User,
        use_cache=True,
        cache_namespace="user",
        cache_ttl=300
    )
    app.include_router(user_crud, prefix="/api/users", tags=["users"])
    
    # 测试创建用户
    response = client.post(
        "/api/users/create",
        json={"username": "test_user", "email": "test@example.com"}
    )
    assert response.status_code == 200
    user_data = response.json()["data"]
    assert user_data["username"] == "test_user"
    
    # 测试获取用户列表（应该使用缓存）
    response = client.post("/api/users/list", json={"filters": {}})
    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) == 1
    
    # 验证缓存是否被使用
    cache_key = f"user:list"
    assert cache_manager.redis_client.get(cache_key) is not None
    
    # 测试读取单个用户（应该使用缓存）
    response = client.get(f"/api/users/read?id={user_data['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "test_user"
    
    # 验证缓存是否被使用
    cache_key = f"user:read:{user_data['id']}"
    assert cache_manager.redis_client.get(cache_key) is not None
    
    # 测试更新用户（应该清除缓存）
    response = client.put(
        f"/api/users/update?id={user_data['id']}",
        json={"username": "updated_user", "email": "updated@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "updated_user"
    
    # 验证缓存是否被清除
    assert cache_manager.redis_client.get(f"user:list") is None
    assert cache_manager.redis_client.get(f"user:read:{user_data['id']}") is None
    
    # 测试删除用户（应该清除缓存）
    response = client.delete(f"/api/users/delete?ids={user_data['id']}")
    assert response.status_code == 200
    
    # 验证缓存是否被清除
    assert cache_manager.redis_client.get(f"user:list") is None
    assert cache_manager.redis_client.get(f"user:read:{user_data['id']}") is None

async def test_basic_cache(cache_manager):
    """测试基本缓存功能"""
    key = "test_key"
    value = "test_value"
    
    # 设置缓存
    await cache_manager._set_cache(key, value, 60)
    
    # 获取缓存
    cached = await cache_manager._get_from_cache(key)
    assert cached == value
    
    # 本地缓存验证
    local_cached = cache_manager.local_cache.get(key)
    assert local_cached == value

async def test_cache_decorator(cache_manager, test_user):
    """测试缓存装饰器"""
    @cache_manager.cache(namespace="users")
    async def get_user(user_id: int):
        return await User.get(id=user_id)
    
    # 首次调用
    result1 = await get_user(test_user.id)
    assert result1.id == test_user.id
    
    # 再次调用应该从缓存获取
    result2 = await get_user(test_user.id)
    assert result2.id == test_user.id

async def test_cache_stampede_protection(cache_manager):
    """测试缓存击穿保护"""
    counter = 0
    
    @cache_manager.cache(
        namespace="test",
        prevent_stampede=True,
        lock_timeout=2,
        wait_timeout=1
    )
    async def slow_function():
        nonlocal counter
        await asyncio.sleep(0.5)  # 模拟慢操作
        counter += 1
        return {"count": counter}
    
    # 并发调用
    tasks = [slow_function() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    # 验证只执行了一次
    assert counter == 1
    # 所有结果应该相同
    assert all(r["count"] == 1 for r in results)

async def test_refresh_mechanism(cache_manager):
    """测试刷新机制"""
    refresh_counter = 0
    
    async def refresh_callback():
        nonlocal refresh_counter
        refresh_counter += 1
        return {"data": f"refresh_{refresh_counter}"}
    
    # 注册刷新任务
    task_name = await cache_manager.register_refresh(
        name="test_refresh",
        callback=refresh_callback,
        interval=1
    )
    
    # 等待自动刷新
    await asyncio.sleep(2)
    
    # 验证刷新次数
    assert refresh_counter >= 1
    
    # 手动触发刷新
    await cache_manager.trigger_refresh(task_name)
    assert refresh_counter >= 2

async def test_distributed_lock(cache_manager):
    """测试分布式锁"""
    key = "test_lock"
    
    # 获取锁
    lock_id = await cache_manager.lock.acquire_lock(key)
    assert lock_id is not None
    
    # 尝试再次获取同一个锁
    lock_id2 = await cache_manager.lock.acquire_lock(key)
    assert lock_id2 is None
    
    # 释放锁
    released = await cache_manager.lock.release_lock(key, lock_id)
    assert released is True

if __name__ == "__main__":
    pytest.main(["-v", "test_cache.py"]) 