# 开发环境配置

## 基础环境

- Windows 开发环境
- Python 3.13.14
- Git 2.53.0
- GitHub CLI 2.95.0
- 仓库级 Git 身份配置

## 安装与运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
python -m uvicorn app.main:app --reload
```

`.venv` 目录和本地 `.env` 文件已被 Git 忽略。仅在需要本地配置时复制 `.env.example`，生成的 `.env` 不应提交。

## Python 包索引记录

项目初始化时，系统配置的清华 PyPI 镜像未返回 FastAPI 版本。保持全局配置不变，单次安装命令切换至官方索引后成功完成依赖安装：

```powershell
python -m pip install --index-url https://pypi.org/simple -r requirements.txt
```
