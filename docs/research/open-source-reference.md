# 开源项目参考记录

调研日期：2026-09-24。通过 GitHub API 阅读仓库元数据与 README，未大规模克隆仓库，也未直接复制第三方源代码。

| Repository | License | 参考内容 | 本项目采用的思路 | 本项目未采用的内容 |
|---|---|---|---|---|
| [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops) | MIT | 本地优先定位、能力边界和基于运行证据的项目展示 | 清晰区分当前能力与后续扩展，展示完整用户流程 | 自动搜索岗位、简历定制、评分与 Agent 工作流超出当前范围 |
| [Gsync/jobsync](https://github.com/Gsync/jobsync) | MIT | 投递跟踪、统计工作台、职位信息保存前确认 | “粘贴 → 提取 → 核对 → 保存”流程和状态统计 | 简历、联系人、任务、自动发现、MCP 和完整部署栈会扩大当前项目边界 |
| [DanielPan12/JobHuntBot](https://github.com/DanielPan12/JobHuntBot) | MIT | 轻量本地工作台、隐私边界和初始化数据设计 | 无前端框架构建的岗位工作台，以及示例数据与个人数据分离 | 浏览器驱动投递和 CSV 自动化不属于当前后端项目范围 |
| [offercontext/offerPilot](https://github.com/offercontext/offerPilot) | AGPL-3.0 | 本地优先的岗位生命周期展示和真实界面文档 | 六阶段岗位状态与基于运行版本的截图 | 多领域产品范围和 AGPL 实现未被复用，本项目保持独立 MIT 实现 |

## 设计决策

- 在扩展更多实体前，先完成 Job 数据模型和业务闭环。
- 未配置外部模型服务时，规则解析仍可完成基础信息提取。
- 信息提取与持久化之间保留人工核对步骤。
- 使用 FastAPI 托管的轻量工作台，避免引入独立前端工程。
- README 展示测试、接口和数据库结构等可复现证据。

仓库名称、描述和 License 标识均在调研日期通过 GitHub 核对；参考思路根据本项目 API 与技术边界独立实现。
