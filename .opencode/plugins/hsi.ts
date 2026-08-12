import { type Plugin, tool } from "@opencode-ai/plugin"

type ModelSelection = {
  providerID: string
  modelID: string
}

type ChatMessage = {
  role?: string
  content?: string | null | Array<{ type?: string; text?: string }>
  name?: string
  tool_call_id?: string
  tool_calls?: Array<{
    id?: string
    function?: { name?: string; arguments?: string }
  }>
}

type ChatTool = {
  type?: string
  function?: {
    name?: string
    description?: string
    parameters?: Record<string, unknown>
  }
}

type ChatCompletionRequest = {
  model?: string
  messages?: ChatMessage[]
  stream?: boolean
  tools?: ChatTool[]
  tool_choice?: string | { type?: string; function?: { name?: string } }
  response_format?: {
    type?: string
    json_schema?: { schema?: Record<string, unknown> }
  }
}

const json = (body: unknown, status = 200) =>
  Response.json(body, {
    status,
    headers: { "Cache-Control": "no-store" },
  })

const messageText = (message: ChatMessage) => {
  if (typeof message.content === "string") return message.content
  if (!Array.isArray(message.content)) return ""
  return message.content
    .filter((part) => part.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("\n")
}

const serializeMessage = (message: ChatMessage) => {
  const text = messageText(message)
  const calls = message.tool_calls
    ?.map((call) => `${call.function?.name ?? "unknown"}(${call.function?.arguments ?? "{}"})`)
    .join(", ")
  const label = message.name ? `${message.role ?? "user"} (${message.name})` : (message.role ?? "user")
  return `${label}: ${[text, calls && `tool calls: ${calls}`].filter(Boolean).join("\n")}`
}

export const HsiPlugin: Plugin = async ({ client, directory }) => {
  const models = new Map<string, ModelSelection>()

  const server = Bun.serve({
    hostname: "127.0.0.1",
    port: 0,
    idleTimeout: 255,
    async fetch(request) {
      const url = new URL(request.url)

      if (request.method === "GET" && url.pathname === "/health") {
        return json({ status: "ok" })
      }

      if (request.method === "GET" && url.pathname === "/v1/models") {
        return json({
          object: "list",
          data: [{ id: "hsi-opencode", object: "model", owned_by: "hsi" }],
        })
      }

      if (request.method !== "POST" || url.pathname !== "/v1/chat/completions") {
        return json({ error: { message: "Not found", type: "invalid_request_error" } }, 404)
      }

      try {
        const body = (await request.json()) as ChatCompletionRequest
        if (body.stream) {
          return json({ error: { message: "Streaming is not supported", type: "invalid_request_error" } }, 400)
        }

        const authorization = request.headers.get("authorization")
        const sessionID = request.headers.get("x-hsi-session-id")
          ?? (authorization?.startsWith("Bearer ") ? authorization.slice(7) : null)
        if (!sessionID) {
          return json({ error: { message: "Missing x-hsi-session-id header", type: "invalid_request_error" } }, 400)
        }

        const model = models.get(sessionID)
        if (!model) {
          return json({ error: { message: "No model recorded for this OpenCode session", type: "invalid_request_error" } }, 409)
        }

        const messages = body.messages ?? []
        const system = messages
          .filter((message) => message.role === "system")
          .map(messageText)
          .filter(Boolean)
          .join("\n\n")
        const transcript = messages
          .filter((message) => message.role !== "system")
          .map(serializeMessage)
          .join("\n\n")

        if (!transcript) {
          return json({ error: { message: "messages must contain text", type: "invalid_request_error" } }, 400)
        }

        const child = await client.session.create({
          query: { directory },
          body: { parentID: sessionID, title: "HSI model bridge" },
        })
        if (!child.data?.id) throw new Error("OpenCode did not create a child session")

        try {
          const availableTools = (body.tools ?? []).filter(
            (candidate) => candidate.type === "function" && candidate.function?.name,
          )
          const forcedTool = typeof body.tool_choice === "object"
            ? body.tool_choice.function?.name
            : undefined
          const selectableTools = forcedTool
            ? availableTools.filter((candidate) => candidate.function?.name === forcedTool)
            : availableTools
          const toolSchema = selectableTools.length
            ? {
                type: "object",
                oneOf: selectableTools.map((candidate) => ({
                  type: "object",
                  properties: {
                    name: { const: candidate.function!.name },
                    arguments: candidate.function!.parameters ?? { type: "object" },
                  },
                  required: ["name", "arguments"],
                  additionalProperties: false,
                })),
              }
            : undefined
          const requestedSchema = body.response_format?.type === "json_schema"
            ? body.response_format.json_schema?.schema
            : undefined
          const formatSchema = toolSchema ?? requestedSchema
          const toolInstructions = selectableTools.length
            ? [
                "Select exactly one tool to call. Return only the structured tool selection.",
                ...selectableTools.map((candidate) =>
                  `${candidate.function!.name}: ${candidate.function?.description ?? "No description"}`,
                ),
              ].join("\n")
            : ""
          const response = await client.session.prompt({
            path: { id: child.data.id },
            query: { directory },
            body: {
              model,
              system: system || undefined,
              tools: {
                bash: false,
                edit: false,
                task: false,
                skill: false,
                hsi_bridge_status: false,
              },
              parts: [{ type: "text", text: [transcript, toolInstructions].filter(Boolean).join("\n\n") }],
              ...(formatSchema
                ? {
                    format: {
                      type: "json_schema" as const,
                      schema: formatSchema,
                    },
                  }
                : {}),
            },
          })

          if (response.error) throw new Error(String(response.error))
          let structured = response.data?.info && "structured" in response.data.info
            ? response.data.info.structured as { name?: string; arguments?: unknown } | undefined
            : undefined
          const content = response.data?.parts
            ?.filter((part) => part.type === "text")
            .map((part) => part.text)
            .join("\n")
          if (!structured && formatSchema && content) {
            try {
              structured = JSON.parse(content) as { name?: string; arguments?: unknown }
            } catch {
              // The error below reports an invalid structured response.
            }
          }
          if (selectableTools.length && (!structured?.name || structured.arguments === undefined)) {
            throw new Error("OpenCode returned no structured tool selection")
          }
          if (!selectableTools.length && !content && structured === undefined) {
            throw new Error("OpenCode returned no content")
          }

          const toolCall = structured?.name
            ? {
                id: `call_hsi_${crypto.randomUUID()}`,
                type: "function",
                function: {
                  name: structured.name,
                  arguments: JSON.stringify(structured.arguments),
                },
              }
            : undefined

          return json({
            id: `chatcmpl-hsi-${crypto.randomUUID()}`,
            object: "chat.completion",
            created: Math.floor(Date.now() / 1000),
            model: body.model ?? "hsi-opencode",
            choices: [{
              index: 0,
              message: toolCall
                ? { role: "assistant", content: null, tool_calls: [toolCall] }
                : { role: "assistant", content: content ?? JSON.stringify(structured) },
              finish_reason: toolCall ? "tool_calls" : "stop",
            }],
            usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
          })
        } finally {
          await client.session.delete({
            path: { id: child.data.id },
            query: { directory },
          })
        }
      } catch (error) {
        return json({
          error: {
            message: error instanceof Error ? error.message : String(error),
            type: "server_error",
          },
        }, 500)
      }
    },
  })

  const bridgeURL = `http://${server.hostname}:${server.port}`

  return {
    dispose: async () => server.stop(true),
    "chat.message": async (input) => {
      if (input.model) models.set(input.sessionID, input.model)
    },
    "shell.env": async (input, output) => {
      output.env.HSI_BRIDGE_URL = `${bridgeURL}/v1`
      if (input.sessionID) output.env.HSI_SESSION_ID = input.sessionID
    },
    tool: {
      hsi_bridge_status: tool({
        description: "Check whether the local HSI OpenCode model bridge is ready",
        args: {},
        async execute(_args, context) {
          const model = models.get(context.sessionID)
          return JSON.stringify({
            url: `${bridgeURL}/v1`,
            sessionID: context.sessionID,
            model: model ? `${model.providerID}/${model.modelID}` : null,
          })
        },
      }),
    },
  }
}
