import { z } from "zod";

export function registerPptxTools(server: any) {
  server.registerTool(
    "create_pptx",
    {
      description: "Generate a PowerPoint presentation from markdown content",
      inputSchema: z.object({
        title: z.string().describe("Presentation title"),
        slides: z.array(z.object({
          title: z.string().describe("Slide title"),
          content: z.string().describe("Slide content (markdown text)"),
        })).describe("Array of slides"),
        output: z.string().describe("Output file path (.pptx)"),
      }),
    },
    async ({ title, slides, output }: { title: string; slides: { title: string; content: string }[]; output: string }) => {
      const pptxgen = await import("pptxgenjs");
      const pptx = new pptxgen.default();
      pptx.defineLayout({ name: "WIDE", width: 13.33, height: 7.5 });
      pptx.layout = "WIDE";

      const slideMaster = pptx.addSlide();
      slideMaster.background = { fill: "FFFFFF" };

      slides.forEach((slide) => {
        const s = pptx.addSlide();
        s.background = { fill: "F5F5F5" };
        s.addText(slide.title, {
          x: 0.5, y: 0.3, w: 12.33, h: 0.8,
          fontSize: 28, bold: true, color: "1A1A2E",
        });
        s.addText(slide.content, {
          x: 0.5, y: 1.3, w: 12.33, h: 5.5,
          fontSize: 16, color: "333333",
          valign: "top", lineSpacingMultiple: 1.5,
        });
      });

      await pptx.writeFile({ fileName: output });
      return { content: [{ type: "text", text: `Presentation saved to ${output}` }] };
    }
  );
}
