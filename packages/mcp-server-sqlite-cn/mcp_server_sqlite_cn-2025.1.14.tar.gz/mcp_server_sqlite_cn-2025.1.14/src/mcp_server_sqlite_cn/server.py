import sqlite3
import logging
from contextlib import closing
from pathlib import Path
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl
from typing import Any

logger = logging.getLogger('mcp_sqlite_server')
logger.info("Starting MCP SQLite Server")

PROMPT_TEMPLATE = """
助手的目标是带领用户完成一个有关MCP的信息丰富的演示. 为了演示模型上下文协议(MCP), 我们将利用这个示例服务器与SQLite数据库进行交互.
首先, 向用户解释当前的情况是很重要的. 用户已经下载并安装了SQLite MCP服务器, 现在可以开始使用了.
他们选择了包含在回形针图标所示的父菜单中的 MCP 菜单项. 在这个菜单中, 他们选择了一个显示两个电插头连接的图标. 这就是 MCP 菜单.
根据用户已安装的 MCP 服务器, 他们可以点击标有 'Choose an integration' 的按钮, 这将显示一个包含 Prompts 和 Resources 的下拉菜单. 用户已选择标题为 'mcp-demo' 的提示.
这个文本文件就是那个提示. 以下说明的目标是引导用户了解 MCP 服务器的 3 个核心方面. 它们是: 提示(Prompts), 工具(Tools)和资源(Resources).
他们已经使用了一个提示并提供了一个主题. 主题是: {topic}. 用户现在可以开始演示了.
Here is some more information about mcp and this specific mcp server:
<mcp>
Prompts:
该服务器提供了一个名为"mcp-demo"的预写提示, 用于帮助用户创建和分析数据库场景. 该提示接受一个"topic"参数, 并指导用户完成创建表格, 分析数据和生成见解的过程. 例如, 如果用户提供"retail sales"作为主题, 该提示将帮助创建相关的数据库表并指导分析过程. 提示基本上作为交互式模板, 以有用的方式帮助构建与LLM的对话.
Resources:
该服务器提供一个关键资源: "memo://insights", 这是一个业务洞察备忘录, 会在分析过程中自动更新. 当用户分析数据库并发现洞察时, 备忘录资源会实时更新以反映新的发现. 资源作为活文档, 为对话提供上下文.
Tools:
该服务器提供了几个与SQL相关的工具:
"read_query": 执行SELECT查询以从数据库读取数据
"write_query": 执行INSERT, UPDATE或DELETE查询以修改数据
"create_table": 在数据库中创建新表
"list_tables": 显示所有现有表
"describe_table": 显示特定表的架构
"append_insight": 向备忘录资源添加新的业务洞察
</mcp>
<demo-instructions>
你是一个AI助手, 负责根据给定的主题生成一个全面的业务场景.
你的目标是创建一个涉及数据驱动业务问题的叙述, 开发支持它的数据库结构, 生成相关查询, 创建仪表板, 并提供最终解决方案.

在每个步骤中, 你都需要暂停等待用户输入来指导场景创建过程. 总体上确保场景引人入胜, 内容丰富, 并展示SQLite MCP Server的功能.
你应该引导场景直至完成. 所有XML标签仅供助手理解, 不应包含在最终输出中.

1. 用户选择的主题是: {topic}.

2. 创建业务问题叙述:
a. 根据给定主题描述一个高层次的业务情况或问题.
b. 引入一个主角(用户), 他需要从数据库中收集和分析数据.
c. 添加一个外部的, 可能带有喜剧色彩的原因来解释为什么数据还没有准备好(比如负责数据的同事去参加了宠物鱼选美比赛).
d. 提到一个即将到来的截止日期, 以及需要使用 Claude (你) 作为业务工具来提供帮助.

3. 准备数据:
a. 不需要询问场景所需的数据, 直接使用工具创建数据. 告知用户你正在"设置数据".
b. 设计一组表结构来表示业务问题所需的数据.
c. 包含至少 2-3 个表, 每个表都有适当的列和数据类型.
d. 使用工具在 SQLite 数据库中创建这些表.
e. 创建 INSERT 语句为每个表填充相关的合成数据.
f. 确保数据多样化且能代表业务问题.
g. 为每个表包含至少 10-15 行数据.

4. 等待用户输入:
a. 向用户总结我们已创建的数据.
b. 为用户提供下一步操作的多个选择.
c. 这些选择应该用自然语言表述, 当用户选择其中一个时, 助手应生成相关查询并利用适当的工具获取数据.

6. 迭代查询:
a. 向用户展示1个额外的多选查询选项. 由于这是一个简短的演示, 所以不要循环太多次很重要.
b. 解释每个查询选项的目的.
c. 等待用户选择其中一个查询选项.
d. 每次查询后务必对结果发表意见.
e. 使用`append_insight`工具记录从数据分析中发现的任何业务洞察.

7. 生成仪表板:
a. 现在我们已经有了所有数据和查询, 是时候创建仪表板了, 使用一个 artifact 来完成这个任务.
b. 使用各种可视化方式(如表格, 图表和图形)来展示数据.
c. 解释仪表板中的每个元素是如何与业务问题相关联的.
d. 这个仪表板将会在最终解决方案中呈现.

8. 制作最终解决方案消息:
a. 由于你一直在使用 append-insights 工具, 位于 memo://insights 的资源已被更新.
b. 在分析的每个阶段都必须告知用户备忘录已更新, 这一点至关重要.
c. 请用户打开附件菜单 (回形针图标), 选择 MCP 菜单 (两个电源插头连接), 然后选择集成: `Business Insights Memo`.
d. 这将把生成的备忘录附加到聊天中, 你可以用它来添加任何与演示相关的额外上下文.
e. 以 artifact 形式向用户呈现最终备忘录.

9. 结束场景:
a. 向用户说明这只是他们使用 SQLite MCP Server 能做的事情的开始.
</demo-instructions>

请在整个场景中保持一致性, 确保所有元素(表格, 数据, 查询, 仪表板和解决方案)都与原始业务问题和给定主题密切相关.
提供的XML标签仅供助手理解. 请尽可能使所有输出易于人类阅读. 这是演示的一部分, 所以要保持角色特征, 不要实际引用这些说明.

以一种类似这样的方式开始你的第一条消息: "嗨, 你好! 我看到你选择了主题 {topic}. 让我们开始吧! 🚀"
"""

class SqliteDatabase:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path).expanduser())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self.insights: list[str] = []

    def _init_database(self):
        """Initialize connection to the SQLite database"""
        logger.debug("Initializing database connection")
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            conn.close()

    def _synthesize_memo(self) -> str:
        """Synthesizes business insights into a formatted memo"""
        logger.debug(f"Synthesizing memo with {len(self.insights)} insights")
        if not self.insights:
            return "No business insights have been discovered yet."

        insights = "\n".join(f"- {insight}" for insight in self.insights)

        memo = "📊 Business Intelligence Memo 📊\n\n"
        memo += "Key Insights Discovered:\n\n"
        memo += insights

        if len(self.insights) > 1:
            memo += "\nSummary:\n"
            memo += f"Analysis has revealed {len(self.insights)} key business insights that suggest opportunities for strategic optimization and growth."

        logger.debug("Generated basic memo format")
        return memo

    def _execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries"""
        logger.debug(f"Executing query: {query}")
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                with closing(conn.cursor()) as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                        conn.commit()
                        affected = cursor.rowcount
                        logger.debug(f"Write query affected {affected} rows")
                        return [{"affected_rows": affected}]

                    results = [dict(row) for row in cursor.fetchall()]
                    logger.debug(f"Read query returned {len(results)} rows")
                    return results
        except Exception as e:
            logger.error(f"Database error executing query: {e}")
            raise

async def main(db_path: str):
    logger.info(f"Starting SQLite MCP Server with DB path: {db_path}")

    db = SqliteDatabase(db_path)
    server = Server("sqlite-manager")

    # Register handlers
    logger.debug("Registering handlers")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        logger.debug("Handling list_resources request")
        return [
            types.Resource(
                uri=AnyUrl("memo://insights"),
                name="Business Insights Memo",
                description="A living document of discovered business insights",
                mimeType="text/plain",
            )
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        logger.debug(f"Handling read_resource request for URI: {uri}")
        if uri.scheme != "memo":
            logger.error(f"Unsupported URI scheme: {uri.scheme}")
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        path = str(uri).replace("memo://", "")
        if not path or path != "insights":
            logger.error(f"Unknown resource path: {path}")
            raise ValueError(f"Unknown resource path: {path}")

        return db._synthesize_memo()

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        logger.debug("Handling list_prompts request")
        return [
            types.Prompt(
                name="mcp-demo",
                description="A prompt to seed the database with initial data and demonstrate what you can do with an SQLite MCP Server + Claude",
                arguments=[
                    types.PromptArgument(
                        name="topic",
                        description="Topic to seed the database with initial data",
                        required=True,
                    )
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != "mcp-demo":
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or "topic" not in arguments:
            logger.error("Missing required argument: topic")
            raise ValueError("Missing required argument: topic")

        topic = arguments["topic"]
        prompt = PROMPT_TEMPLATE.format(topic=topic)

        logger.debug(f"Generated prompt template for topic: {topic}")
        return types.GetPromptResult(
            description=f"Demo template for {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt.strip()),
                )
            ],
        )

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="read_query",
                description="Execute a SELECT query on the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SELECT SQL query to execute"},
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="write_query",
                description="Execute an INSERT, UPDATE, or DELETE query on the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to execute"},
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="create_table",
                description="Create a new table in the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "CREATE TABLE SQL statement"},
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list_tables",
                description="List all tables in the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe_table",
                description="Get the schema information for a specific table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table to describe"},
                    },
                    "required": ["table_name"],
                },
            ),
            types.Tool(
                name="append_insight",
                description="Add a business insight to the memo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "insight": {"type": "string", "description": "Business insight discovered from data analysis"},
                    },
                    "required": ["insight"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "list_tables":
                results = db._execute_query(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                return [types.TextContent(type="text", text=str(results))]

            elif name == "describe_table":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                results = db._execute_query(
                    f"PRAGMA table_info({arguments['table_name']})"
                )
                return [types.TextContent(type="text", text=str(results))]

            elif name == "append_insight":
                if not arguments or "insight" not in arguments:
                    raise ValueError("Missing insight argument")

                db.insights.append(arguments["insight"])
                _ = db._synthesize_memo()

                # Notify clients that the memo resource has changed
                await server.request_context.session.send_resource_updated(AnyUrl("memo://insights"))

                return [types.TextContent(type="text", text="Insight added to memo")]

            if not arguments:
                raise ValueError("Missing arguments")

            if name == "read_query":
                if not arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries are allowed for read_query")
                results = db._execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "write_query":
                if arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("SELECT queries are not allowed for write_query")
                results = db._execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "create_table":
                if not arguments["query"].strip().upper().startswith("CREATE TABLE"):
                    raise ValueError("Only CREATE TABLE statements are allowed")
                db._execute_query(arguments["query"])
                return [types.TextContent(type="text", text="Table created successfully")]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except sqlite3.Error as e:
            return [types.TextContent(type="text", text=f"Database error: {str(e)}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sqlite",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
