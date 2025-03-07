# fastapi_tortoise_crud

## 项目概述

fastapi_tortoise_crud 是一个基于 FastAPI 和 Tortoise ORM 的 CRUD 快速开发框架，帮助开发者以最小的代码量构建功能完整的 REST API。

## 安装依赖

项目默认会安装以下依赖：
- fastapi
- tortoise-orm
- fastapi_pagination
- redis (可选，用于缓存)


## 兼容性说明

- 目前只支持 pydantic-v2

## 主要功能

- **快速CRUD**: 通过`ModelCrud`类，轻松为模型生成增删改查API
- **灵活配置**: 支持为不同操作配置不同的schema
- **自定义依赖**: 可为各种操作添加自定义依赖项
- **内置分页**: 集成了fastapi_pagination的分页功能
- **排序支持**: 支持多字段排序功能
- **自定义路由**: 可以在CRUD基础上添加自定义路由
- **数据关系**: 支持一对多、多对多等复杂关系
- **钩子函数**: 提供before_create、after_create等钩子函数
- **缓存系统**: 
  - 多级缓存（本地缓存+Redis）
  - 缓存标签系统
  - 缓存键生成器
  - 缓存失效策略

## 使用示例

### 定义模型

```python:models.py
from fastapi_tortoise_crud import BaseModel as TortoiseBaseModel
from tortoise import fields

class Category(TortoiseBaseModel):
    """分类模型"""
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)
    posts: fields.ReverseRelation["Post"]
    
    class Meta:
        table = "categories"
        table_title = "分类"

class Post(TortoiseBaseModel):
    """文章模型"""
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    category = fields.ForeignKeyField('models.Category', related_name='posts')
    
    class Meta:
        table = "posts"
        table_title = "文章"
```

### 创建CRUD实例

```python:main.py
from fastapi_tortoise_crud import ModelCrud

# 创建带缓存的CRUD实例
post_crud = ModelCrud(
    Post,
    use_cache=True,
    cache_namespace="posts",
    cache_ttl=3600,
    schema_create=PostCreate,
    schema_read=PostRead
)

# 注册路由
app.include_router(post_crud, prefix="/posts", tags=["文章管理"])
```

### 缓存配置

```python:main.py
from fastapi_tortoise_crud import CacheManager, CacheType

# 初始化缓存管理器
CacheManager.init(
    redis_url="redis://localhost:6379/0",
    prefix="myapp:",
    default_ttl=300,
    cache_type=CacheType.BOTH,  # 使用本地缓存+Redis
)
```

### 钩子函数

```python:main.py
async def after_create_post(*, instance: Post, data: dict):
    """创建文章后的钩子"""
    # 可以进行额外操作，如发送通知
    return data

# 注册钩子
post_crud.register_hook('after_create', after_create_post)
```

## ModelCrud 参数说明

- **model**: 数据模型类
- **schema_create**: 创建数据的pydantic模型
- **schema_read**: 读取数据的pydantic模型
- **schema_list**: 列表数据的pydantic模型
- **schema_update**: 更新数据的pydantic模型
- **schema_filters**: 过滤条件的pydantic模型
- **use_cache**: 是否启用缓存
- **cache_namespace**: 缓存命名空间
- **cache_ttl**: 缓存过期时间
- **cache_tags**: 缓存标签列表

## 缓存系统说明

### 缓存类型

- **CacheType.NONE**: 禁用缓存
- **CacheType.LOCAL**: 仅使用本地缓存
- **CacheType.REDIS**: 仅使用Redis缓存
- **CacheType.BOTH**: 同时使用本地和Redis缓存

### 缓存标签

缓存标签用于组织和管理缓存数据，支持按标签清除缓存：

```python
# 使用缓存标签
post_crud = ModelCrud(
    Post,
    use_cache=True,
    cache_namespace="posts",
    cache_tags=["post", f"category:{category_id}"]
)

# 清除特定标签的缓存
await CacheManager.clear_by_tags(["category:123"])
```

### 缓存键生成

系统会自动根据查询参数生成唯一的缓存键：

```python
from fastapi_tortoise_crud.cache import generate_cache_key

cache_key = generate_cache_key(
    namespace="posts",
    prefix="list",
    filters=filters,
    page=page,
    size=size
)
```

## 最佳实践

1. **缓存使用**:
   - 为读多写少的数据启用缓存
   - 合理设置缓存过期时间
   - 使用缓存标签进行精确失效

2. **性能优化**:
   - 使用适当的缓存类型
   - 合理设置预加载字段
   - 避免过度缓存

3. **开发建议**:
   - 合理使用钩子函数
   - 注意异常处理
   - 保持代码整洁

## 许可证

[待补充]
