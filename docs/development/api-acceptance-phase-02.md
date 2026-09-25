# API 验收记录

日期：2026-09-24

Uvicorn 在 `http://127.0.0.1:8000` 启动应用，本地 SQLite 数据库写入内置示例岗位，并通过真实 HTTP 请求完成验收。

## 接口结果

| 操作 | 结果 |
|---|---|
| `GET /health` | `200`，返回 `{"status":"ok"}` |
| `GET /docs` | `200`，Swagger UI 正常加载 |
| `GET /demo` | `200`，岗位工作台加载 10 条示例岗位 |
| `POST /api/v1/job-extract` | `200`，规则解析返回结构化预览和 5 个技能关键词 |
| `POST /api/v1/jobs` | `201`，成功创建岗位 |
| `GET /api/v1/jobs/{job_id}` | `200`，返回指定岗位 |
| 公司、状态、地点组合筛选 | `200`，结果数量正确 |
| `PATCH /api/v1/jobs/{job_id}` | `200`，状态和地点更新成功 |
| 更新后条件筛选 | `200`，返回更新后的岗位 |
| `DELETE /api/v1/jobs/{job_id}` | `204`，响应体为空 |
| 删除后再次查询 | `404` |

## 创建岗位响应示例

```json
{
  "id": 2,
  "title": "Python 后端开发实习生",
  "company": "Example Tech",
  "location": "北京",
  "description": "负责 Python Web 后端接口开发与数据处理。",
  "source_url": "https://example.com/jobs/python-backend-intern",
  "status": "saved",
  "created_at": "2026-09-23T17:36:12.768189",
  "updated_at": "2026-09-23T17:36:12.768192"
}
```

实际 Swagger 响应截图见 [`job-api-example.png`](../images/job-api-example.png)。

## OpenAPI 核验

生成的 OpenAPI 文档包含：

- 路径：`/health`、`/api/v1/jobs`、`/api/v1/jobs/{job_id}`、`/api/v1/job-extract`
- 操作：创建、列表查询、详情查询、更新、删除、职位信息提取
- Schema：Job CRUD/列表/状态、提取请求/预览、统一错误和运行状态
- 状态码：`200`、`201`、`204`、`404` 和自定义 `422` 响应说明
