# 问题排查记录

## 2026-09-24：Python 包镜像未返回 FastAPI 版本

**现象：** 通过系统配置的清华 PyPI 镜像安装 `requirements.txt` 时出现 “No matching distribution found”。

**原因：** 镜像未返回可用的 FastAPI 版本，项目依赖范围本身有效。

**处理：** 保持全局 pip 配置不变，仅在本次安装命令中指定官方 PyPI 索引，依赖安装成功。

## 2026-09-24：TestClient 触发上游弃用警告

**现象：** 首个通过的接口测试使用 FastAPI `TestClient`，Starlette 对其 HTTPX 兼容路径发出弃用警告。

**处理：** 改用 HTTPX `ASGITransport` 和 `AsyncClient`，重新运行测试后警告消失。

## 2026-09-24：自定义校验响应与 OpenAPI 不一致

**现象：** 运行时校验错误已使用项目统一错误结构，但 OpenAPI 仍展示默认 `HTTPValidationError`。

**原因：** 替换异常处理器不会自动替换每个路由文档中的 `422` 响应模型。

**处理：** 增加 `ErrorDetail` 和 `ErrorResponse`，并为 Job Router 显式配置 `422` 响应；重新生成 OpenAPI 后引用正确。

## 2026-09-24：SQLite DDL 检查命令出现引号嵌套错误

**现象：** 首次执行 SQLite DDL 读取命令时，Python 在打开数据库前即报告语法错误。

**原因：** PowerShell 与 Python 字符串引号嵌套不正确。

**处理：** 使用 PowerShell 单引号包裹命令，并在 Python SQL 中使用双引号，成功读取表和索引 DDL。

## 2026-09-24：浏览器自动化禁止访问本地 `file:` 地址

**现象：** Playwright 无法直接打开本地 ER 图 HTML 文件。

**原因：** 浏览器自动化安全策略禁止 `file:` 协议导航。

**处理：** 在 `127.0.0.1` 启动本地静态服务完成页面核对与截图，文件未上传到外部服务。

## 2026-09-24：工作台出现 favicon 404

**现象：** 页面功能正常，但浏览器控制台记录 `/favicon.ico` 的 `404`。

**原因：** 浏览器会自动请求 favicon。

**处理：** 为工作台和测试结果页面加入内联 `data:` favicon，重新验收后控制台无错误和警告。

## 2026-09-24：测试结果截图缺少稳定的复现方式

**现象：** 直接截取终端输出难以保持统一尺寸和清晰排版。

**处理：** pytest 生成 JUnit XML，项目脚本读取真实测试数量、失败数和运行时间，再由浏览器截图。XML 保存在 Git 忽略的构建输出目录中。
