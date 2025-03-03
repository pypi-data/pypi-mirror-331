# SQLite MCP 服务器

## 概述
这是一个基于 SQLite 的模型上下文协议(MCP)服务器实现,提供数据库交互和商业智能功能。该服务器支持运行 SQL 查询、分析业务数据以及自动生成业务洞察备忘录。

## 组件

### 资源
服务器提供一个动态资源:
- `memo://insights`: 持续更新的业务洞察备忘录,用于汇总分析过程中发现的见解
  - 通过 append-insight 工具发现新见解时自动更新

### 提示
服务器提供一个演示提示:
- `mcp-demo`: 交互式提示,引导用户完成数据库操作
  - 必需参数: `topic` - 要分析的业务领域
  - 生成适当的数据库模式和示例数据
  - 引导用户完成分析和见解生成
  - 与业务洞察备忘录集成

### 工具
服务器提供六个核心工具:

#### 查询工具
- `read_query`
   - 执行 SELECT 查询以从数据库读取数据
   - 输入:
     - `query` (字符串): 要执行的 SELECT SQL 查询
   - 返回: 查询结果对象数组

- `write_query`
   - 执行 INSERT、UPDATE 或 DELETE 查询
   - 输入:
     - `query` (字符串): SQL 修改查询
   - 返回: `{ affected_rows: number }`

- `create_table`
   - 在数据库中创建新表
   - 输入:
     - `query` (字符串): CREATE TABLE SQL 语句
   - 返回: 表创建确认

#### 模式工具
- `list_tables`
   - 获取数据库中所有表的列表
   - 无需输入
   - 返回: 表名数组

- `describe-table`
   - 查看特定表的模式信息
   - 输入:
     - `table_name` (字符串): 要描述的表名
   - 返回: 包含列名和类型的列定义数组

#### 分析工具
- `append_insight`
   - 向备忘录资源添加新的业务见解
   - 输入:
     - `insight` (字符串): 从数据分析中发现的业务见解
   - 返回: 见解添加确认
   - 触发 memo://insights 资源的更新


## 在 Claude Desktop 中使用

### uv

```bash
# 在 claude_desktop_config.json 中添加服务器
"mcpServers": {
  "sqlite": {
    "command": "uv",
    "args": [
      "--directory",
      "parent_of_servers_repo/servers/src/sqlite",
      "run",
      "mcp-server-sqlite-cn",
      "--db-path",
      "~/test.db"
    ]
  }
}
```

### Docker

```json
# 在 claude_desktop_config.json 中添加服务器
"mcpServers": {
  "sqlite": {
    "command": "docker",
    "args": [
      "run",
      "--rm",
      "-i",
      "-v",
      "mcp-test:/mcp",
      "mcp/sqlite",
      "--db-path",
      "/mcp/test.db"
    ]
  }
}
```

## 构建

Docker:

```bash
docker build -t mcp/sqlite .
```

## 许可证

本 MCP 服务器采用 MIT 许可证。这意味着您可以自由使用、修改和分发本软件,但需遵守 MIT 许可证的条款和条件。详情请参阅项目仓库中的 LICENSE 文件。
