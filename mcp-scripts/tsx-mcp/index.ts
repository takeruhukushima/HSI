import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { registerPptxTools } from "./packages/pptx-generator/src/index.ts";

const server = new McpServer({
  name: "tsx-mcp",
  version: "0.1.0",
});

registerPptxTools(server);

server.registerTool(
  "lookup_doi",
  {
    description: "Fetch paper metadata from a DOI using Crossref API",
    inputSchema: z.object({ doi: z.string().describe("DOI (e.g. 10.1038/nature12373)") }),
  },
  async ({ doi }: { doi: string }) => {
    const url = `https://api.crossref.org/works/${encodeURIComponent(doi)}`;
    const resp = await fetch(url);
    if (!resp.ok) {
      return { content: [{ type: "text", text: `Error: DOI not found (${resp.status})` }] };
    }
    const data = (await resp.json()) as { message: any };
    const m = data.message;
    const paper = {
      title: m.title?.[0] ?? "N/A",
      authors: m.author
        ? m.author.map((a: any) => [a.given, a.family].filter(Boolean).join(" ")).join(", ")
        : "N/A",
      journal: m["container-title"]?.[0] ?? "N/A",
      year: String(m["published-print"]?.["date-parts"]?.[0]?.[0] ?? m["created"]?.["date-parts"]?.[0]?.[0] ?? "N/A"),
      doi,
    };
    return { content: [{ type: "text", text: JSON.stringify(paper, null, 2) }] };
  }
);

server.registerTool(
  "format_bibtex",
  {
    description: "Generate BibTeX citation from paper metadata",
    inputSchema: z.object({
      title: z.string().describe("Paper title"),
      authors: z.string().describe("Authors (comma separated)"),
      journal: z.string().describe("Journal name"),
      year: z.string().describe("Publication year"),
      doi: z.string().optional().describe("DOI (optional)"),
    }),
  },
  async ({ title, authors, journal, year, doi }: { title: string; authors: string; journal: string; year: string; doi?: string }) => {
    const firstAuthor = authors.split(",")[0]?.trim().split(" ").pop()?.toLowerCase() ?? "unknown";
    const key = `${firstAuthor}${year}`;
    const esc = (s: string) => s.replace(/[{}&%$#_^~\\]/g, "\\$&");
    const bib = `@article{${key},
  title   = {${esc(title)}},
  author  = {${esc(authors)}},
  journal = {${esc(journal)}},
  year    = {${year}},${doi ? `\n  doi     = {${doi}},` : ""}
}`;
    return { content: [{ type: "text", text: bib }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
