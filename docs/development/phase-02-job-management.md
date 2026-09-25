# Job Management API 与 SQLAlchemy 开发记录

日期：2026-09-24

## 开发目标

- 设计聚焦的 Job 领域模型。
- 增加 SQLAlchemy 2.x 持久化和环境变量数据库配置。
- 实现带校验的 CRUD、筛选和分页。
- 隔离自动化测试数据库与本地运行数据库。
- 验证 OpenAPI 和真实 HTTP 行为。
- 补充架构、数据库结构和运行截图。

## 环境信息

- Python：3.13.14
- FastAPI：0.141.1
- SQLAlchemy：2.0.54
- Pydantic：2.13.5
- pytest：9.1.1
- HTTPX：0.28.1

本地运行使用 SQLite，未安装额外的系统级数据库软件。

## 数据库方案

SQLAlchemy 引擎从 `DATABASE_URL` 创建，本地默认采用 SQLite。SQLite 专属连接选项按 URL 类型条件配置，使 ORM、Session 和 Service 层保持数据库无关性，为扩展其他关系型数据库保留清晰边界。

## 模型设计

Job 模型包含 `id`、`title`、`company`、`location`、`description`、`source_url`、`status`、`created_at` 和 `updated_at`。`title` 与 `company` 必填且不能只包含空白；`location`、`description` 和 `source_url` 可为空。

六种状态为 `saved`、`applied`、`interview`、`offer`、`rejected` 和 `closed`。最后一种状态用于表达过期、撤回或其他结束情况。

## API 设计

- `POST /api/v1/jobs`：创建岗位，返回 `201`。
- `GET /api/v1/jobs`：返回分页信息，支持公司、状态和地点筛选。
- `GET /api/v1/jobs/{job_id}`：查询岗位，不存在时返回 `404`。
- `PATCH /api/v1/jobs/{job_id}`：只更新已提交字段，并拒绝空请求体。
- `DELETE /api/v1/jobs/{job_id}`：删除成功返回 `204`。
- 参数校验失败返回带统一 `ErrorResponse` 的 `422`。

## 测试策略

测试使用 HTTPX `ASGITransport` 调用 ASGI 应用。Fixture 为每项测试创建 SQLite 文件和 SQLAlchemy Engine，覆盖 `get_db` 后在结束时释放资源，从而避免测试顺序依赖并保护本地数据库。

岗位 API 首次完成时包含 17 项测试；加入工作台、数据初始化和信息提取后，测试集扩展为 40 项。

## 手工验收

Uvicorn 在 `127.0.0.1:8000` 启动，真实请求验证 `/health`、`/docs`、`/demo`、岗位 CRUD、组合筛选、职位信息提取以及异常响应。详见 [API 验收记录](api-acceptance-phase-02.md)和[岗位管理与信息提取功能开发记录](phase-02-completion.md)。

## 后续扩展

- MySQL 驱动与连接配置
- Alembic 迁移
- Job 之外的业务实体
- 用户认证与权限
- 外部模型服务配置与质量评估
