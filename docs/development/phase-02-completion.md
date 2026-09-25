# 岗位管理与信息提取功能开发记录

日期：2026-09-24

## 开发成果

项目完成岗位管理的完整业务链路：SQLAlchemy 持久化、输入校验、CRUD、筛选、分页、示例数据初始化、浏览器工作台、职位信息提取和 40 项自动化测试。

## 数据库与测试隔离

- 本地数据库：由 `DATABASE_URL` 配置，默认使用 `sqlite:///./career_assistant.db`。
- 示例数据：10 条岗位，覆盖六种状态、多家公司和多个地点。
- 测试数据库：通过 FastAPI 依赖覆盖，为每项 pytest 用例创建独立 SQLite 文件。
- 数据表初始化：当前使用 `Base.metadata.create_all()`，后续随 Schema 演进引入 Alembic。

## 岗位生命周期、筛选和分页

岗位状态包括 `saved`、`applied`、`interview`、`offer`、`rejected` 和 `closed`。其中 `closed` 用于表示岗位过期或主动结束，与申请未通过保持语义区分。列表接口支持页码、每页数量、公司、状态和地点参数。

## 工作台设计

`GET /demo` 返回由 FastAPI 托管的 HTML/CSS/JavaScript 工作台。页面通过现有 REST API 读取和保存数据，提供岗位统计、筛选、岗位列表，以及“粘贴 → 提取 → 核对 → 保存”流程，没有另建第二套业务实现。

## Extraction Provider 设计

- `rule_based`：基础解析方案，可识别带标签的职位、公司、地点和技能关键词。
- `deepseek`：可配置外部 Provider，处理超时、鉴权、限流、服务端错误、网络异常和格式异常。
- 测试 Provider：用于开发与测试环境，隔离外部网络依赖。
- Provider 切换后，响应通过 `extraction_method` 记录实际执行方式。

信息提取只生成预览；岗位持久化仍由用户确认后调用 Job API 完成。

## DeepSeek 配置

项目通过 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL` 和超时参数配置 DeepSeek Provider。当前默认运行配置未启用外部模型服务，系统使用规则解析流程。Provider 的成功响应、`401`、`429`、`5xx`、超时和异常响应均通过 HTTP 测试替身覆盖。

## 验证结果

- `python -m pytest -v`：40 项测试通过。
- Uvicorn 验收：运行状态、Swagger、列表、创建、详情、更新、筛选、分页、信息提取、删除和删除后 `404` 均通过。
- 浏览器验收：`/demo` 和 `/docs` 正常渲染，控制台无错误；完成一次职位描述提取、人工核对和岗位保存流程。
- 数据初始化幂等性：重复执行后输出 `created=0, skipped=10`。

## 问题与经验

问题排查记录保留了依赖镜像、HTTPX 测试方式、OpenAPI 错误 Schema、浏览器本地文件限制、favicon 请求和测试结果证据生成等实际问题及解决过程。

## 后续扩展

- MySQL 连接与部署配置
- Alembic 数据库迁移
- Application、Interview 等业务实体
- 用户认证、部署和可观测性
- 模型辅助岗位分析与质量评估
