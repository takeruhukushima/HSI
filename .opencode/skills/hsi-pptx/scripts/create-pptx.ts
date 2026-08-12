import { parseArgs } from "node:util"
import { readFile } from "node:fs/promises"
import pptxgenModule from "pptxgenjs"

type Presentation = {
  title: string
  slides: Array<{ title: string; content: string }>
}

const { values } = parseArgs({
  options: {
    input: { type: "string" },
    output: { type: "string" },
  },
})

if (!values.input || !values.output) {
  throw new Error("Usage: create-pptx.ts --input presentation.json --output presentation.pptx")
}

const presentation = JSON.parse(await readFile(values.input, "utf8")) as Presentation
if (!presentation.title || !Array.isArray(presentation.slides)) {
  throw new Error("Input must contain title and slides")
}

const PptxGenJS = "default" in pptxgenModule ? pptxgenModule.default : pptxgenModule
const pptx = new PptxGenJS()
pptx.layout = "LAYOUT_WIDE"
pptx.author = "HSI"
pptx.subject = presentation.title
pptx.title = presentation.title

for (const slide of presentation.slides) {
  const page = pptx.addSlide()
  page.background = { color: "F5F5F5" }
  page.addText(slide.title, {
    x: 0.5, y: 0.3, w: 12.33, h: 0.8,
    fontSize: 28, bold: true, color: "1A1A2E",
  })
  page.addText(slide.content, {
    x: 0.5, y: 1.3, w: 12.33, h: 5.5,
    fontSize: 16, color: "333333", valign: "top",
  })
}

await pptx.writeFile({ fileName: values.output })
console.log(`Presentation saved to ${values.output}`)
