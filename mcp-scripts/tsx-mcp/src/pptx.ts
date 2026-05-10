import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerPptxTools } from "../packages/pptx-generator/src/index.ts";

/**
 * MCP Hub Server
 * 全ての個別パッケージからツールを集約して起動します。
 */
const server = new McpServer({
  name: "my-agent_mcp_tsx",
  version: "1.0.0",
});

// 各パッケージのツールを登録
registerPptxTools(server);

// 将来的にツールを追加する場合は、ここに登録関数を並べるだけです
// registerNewTool(server);

async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Hub Server running on stdio");
}

run().catch(console.error);
