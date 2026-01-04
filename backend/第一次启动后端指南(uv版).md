# 第一次启动后端工程指南（uv版）

## 1. uv 简介

uv 是一个现代化的 Python 包管理器和开发工具，提供更快的依赖安装和项目管理体验。它兼容 pip 和 poetry 的配置格式，同时提供了更高效的性能。

## 2. 环境准备

### 2.1 安装 uv

根据你的操作系统选择合适的安装方式：

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 验证安装
```bash
uv --version
```

### 2.2 安装 Python

uv 支持管理多个 Python 版本，你可以使用 uv 安装所需的 Python 版本：

```bash
# 安装 Python 3.10（或其他版本）
uv python install 3.10

# 查看已安装的 Python 版本
uv python list
```

## 3. 项目依赖管理

### 3.1 初始化项目（如果尚未初始化）

如果项目尚未使用 uv 初始化，可以执行以下命令：

```bash
uv init
```

这将创建一个 `pyproject.toml` 文件（如果不存在）并设置虚拟环境。

### 3.2 安装依赖

使用 uv 安装项目依赖：

```bash
uv install
```

这将根据 `requirements.txt` 或 `pyproject.toml` 中的依赖配置安装所有依赖包。

### 3.3 添加新依赖（可选）

如果需要添加新的依赖包，可以使用：

```bash
uv add <package-name>
```

例如：
```bash
uv add fastapi uvicorn
```

## 4. 数据库配置

### 4.1 安装 PostgreSQL

本项目使用 PostgreSQL 数据库，请确保你的系统已经安装了 PostgreSQL。

### 4.2 配置数据库连接

修改 `.env` 文件中的数据库配置，根据你的实际情况调整：

```env
# 数据库配置（本地开发环境）
DB_HOST=localhost # 本地数据库
# DB_HOST=db # docker用
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=123456
DB_PORT=5432
```

### 4.3 初始化数据库

1. 启动 PostgreSQL 服务
2. 使用以下命令创建数据库（如果需要）：
   ```bash
   createdb postgres
   ```
3. 运行数据库初始化脚本：
   ```bash
   psql -h localhost -U postgres -d postgres -f db-init/init.sql
   ```

   或者，当你启动应用时，FastAPI 会自动创建数据库表（通过 `Base.metadata.create_all(bind=engine)`）。

## 5. 启动后端服务

### 5.1 使用 uv 启动服务

使用 uv 启动后端服务有两种方式：

#### 方式一：直接运行主入口文件

```bash
uv run uvicorn main:app --app-dir src --reload
```

#### 方式二：使用 uvicorn 直接启动（推荐）

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.2 启动参数说明

- `--host 0.0.0.0`：允许所有 IP 访问
- `--port 8000`：服务监听端口，可在 `.env` 中通过 `API_PORT` 配置
- `--reload`：开发模式，代码修改后自动重启服务

### 5.3 使用虚拟环境中的 Python 启动

```bash
# 激活虚拟环境（可选，uv run 会自动使用）
source .venv/Scripts/activate  # Windows
# 或
source .venv/bin/activate  # macOS/Linux

# 启动服务
python src/main.py
```

## 6. 验证服务是否启动成功

### 6.1 访问 API 文档

服务启动后，可以通过以下地址访问自动生成的 API 文档：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 6.2 测试 API 端点

可以使用 curl 或 Postman 等工具测试 API 端点，例如：

```bash
curl http://localhost:8000/api/health
```

## 7. 项目结构说明

```
backend/
├── src/                     # 主源码目录
│   ├── tts/                 # TTS相关功能模块
│   ├── user/                # 用户认证相关模块
│   ├── main.py              # 应用主入口
│   ├── database.py          # 数据库配置
│   └── ...
├── db-init/                 # 数据库初始化脚本
│   └── init.sql
├── .env                     # 环境变量配置
├── pyproject.toml           # uv 项目配置文件
├── requirements.txt         # 依赖列表
└── ...
```

## 8. uv 常用命令

### 8.1 依赖管理

```bash
# 安装所有依赖
uv install

# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 移除依赖
uv remove <package-name>

# 升级依赖
uv upgrade

# 导出依赖到 requirements.txt
uv export > requirements.txt
```

### 8.2 运行命令

```bash
# 使用 uv 运行 Python 脚本
uv run python <script.py>

# 使用 uv 运行命令行工具
uv run <command>
```

### 8.3 虚拟环境管理

```bash
# 激活虚拟环境
uv venv activate

# 退出虚拟环境
deval

# 查看虚拟环境路径
uv venv info
```

## 9. 常见问题与解决方案

### 9.1 依赖安装失败

- 确保 uv 版本是最新的：`uv self update`
- 尝试清理缓存：`uv cache clean`
- 检查网络连接是否正常

### 9.2 数据库连接失败

- 检查 PostgreSQL 服务是否正常运行
- 验证 `.env` 文件中的数据库配置是否正确
- 确保 PostgreSQL 允许远程连接（如果使用远程数据库）

### 9.3 端口被占用

- 修改 `.env` 文件中的 `API_PORT` 配置为其他未被占用的端口
- 或者关闭占用该端口的其他服务

### 9.4 uv 命令未找到

- 确保 uv 已正确安装
- 检查环境变量 PATH 是否包含 uv 的安装路径
- 尝试重新启动终端

## 10. 开发注意事项

1. 开发过程中，建议使用 `--reload` 参数启动服务，方便代码修改后自动重启
2. 所有环境变量配置都应放在 `.env` 文件中，不要硬编码到代码中
3. 数据库表结构变更后，FastAPI 会自动更新表结构（开发环境）
4. API 文档会根据代码中的注释自动生成，建议为每个端点添加详细注释
5. 使用 `uv run` 运行命令可以确保使用项目的虚拟环境和依赖

## 11. 后续操作

- 服务启动成功后，可以开始开发前端或其他功能模块
- 可以通过 API 文档测试各个端点的功能
- 定期备份数据库，尤其是在生产环境中
- 考虑使用 `uv build` 构建项目用于生产部署

---

**祝你开发愉快！**
