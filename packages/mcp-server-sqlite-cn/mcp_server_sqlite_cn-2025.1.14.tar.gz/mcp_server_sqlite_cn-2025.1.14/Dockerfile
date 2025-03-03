# 使用预装了uv的Python镜像
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# 将项目安装到 `/app` 目录
WORKDIR /app

# 启用字节码编译
ENV UV_COMPILE_BYTECODE=1

# 由于是挂载卷,从缓存复制而不是链接
ENV UV_LINK_MODE=copy

# 使用lockfile和配置安装项目依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# 然后,添加剩余的项目源代码并安装
# 将依赖和项目分开安装可以优化层缓存
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm

WORKDIR /app
 
COPY --from=uv /root/.local /root/.local
COPY --from=uv --chown=app:app /app/.venv /app/.venv

# 将可执行文件路径添加到环境变量PATH的最前面
ENV PATH="/app/.venv/bin:$PATH"

# 运行容器时,添加 --db-path 参数并将主机的数据库文件挂载进来
ENTRYPOINT ["mcp-server-sqlite-cn"]
