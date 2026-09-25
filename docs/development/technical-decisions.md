# 技术决策记录

## TD-001：先建立最小可运行基础

项目首先实现运行状态接口和基础包结构，以真实可运行、可测试的代码验证工程骨架，再逐步增加业务能力。

## TD-002：通过 ASGI 执行接口测试

测试使用 HTTPX `ASGITransport` 和 `AsyncClient`，无需打开网络端口即可验证路由、序列化和 HTTP 契约。

## TD-003：使用仓库级 Git 身份

项目使用仓库级作者配置，避免覆盖其他项目的全局 Git 设置。提交邮箱使用与仓库所有者关联的 GitHub noreply 地址。

## TD-004：使用有边界的依赖版本范围

`requirements.txt` 为直接依赖配置兼容范围，既允许补丁更新，也避免意外升级到未来主版本。部署环境确定后可进一步引入锁定策略。

## TD-005：保持单一 Service 层

Job Router 将 CRUD 和查询委托给 `job_service.py`，Service 直接使用请求级 SQLAlchemy Session。当前规模无需叠加 Repository、DAO、Manager 和 UseCase 等重复抽象。

## TD-006：默认使用 SQLite，并保留数据库扩展边界

当前本地运行和测试采用 SQLite。`DATABASE_URL` 是数据库连接切换点，SQLAlchemy ORM、Session 与 Service 层不依赖具体数据库实现，可在部署阶段扩展 MySQL 等关系型数据库。

## TD-007：Schema 演进前使用 `create_all()`

当前只有一个表，尚不存在跨环境迁移历史。通过 SQLAlchemy Metadata 初始化更直接；当持久化环境需要连续版本升级时再引入 Alembic。

## TD-008：列表接口返回分页元数据

岗位列表响应包含 `items`、`total`、`page` 和 `page_size`，客户端无需通过当前页长度推断总数。

## TD-009：分离 ORM 与 API 契约

`JobCreate`、`JobUpdate`、`JobRead` 和 `JobList` 防止数据库模型直接成为公开接口契约。局部更新通过显式字段跟踪实现，数据库必填字段不能被更新为 `null`。

## TD-010：提取预览与持久化分离

`POST /api/v1/job-extract` 只返回结构化预览。用户核对后再调用 Job API 保存，避免信息提取过程直接改变岗位数据。
