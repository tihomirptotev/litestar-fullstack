/**
 * Build script for email templates.
 *
 * Uses Maizzle (@maizzle/framework) to render Vue SFC email templates to
 * static HTML with all styles processed for email client compatibility.
 *
 * Output goes to src/py/app/server/static/email/ for wheel bundling.
 *
 * Usage: bun run build-emails.ts (or node build-emails.ts)
 */

import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs"
import { basename, resolve } from "node:path"
import { render } from "@maizzle/framework"

// Output directory (inside Python package for wheel bundling)
const OUTPUT_DIR = resolve(process.cwd(), "../../py/app/server/static/email")

// Optional global CSS file for additional styles
const GLOBAL_CSS_PATH = resolve(process.cwd(), "src/styles/global.css")

// Ensure output directory exists
mkdirSync(OUTPUT_DIR, { recursive: true })

// Discover email templates
const emailsDir = resolve(process.cwd(), "src/emails")

// Maizzle render options: resolve components from src/components/
const RENDER_OPTIONS = {
  root: process.cwd(),
  components: { source: [{ path: "src/components" }] },
}

/**
 * Inline CSS into HTML head if a global CSS file exists.
 * Maizzle already inlines component styles, but this allows
 * for additional global styles if needed.
 */
function inlineGlobalCSS(html: string): string {
  if (!existsSync(GLOBAL_CSS_PATH)) {
    return html
  }

  const css = readFileSync(GLOBAL_CSS_PATH, "utf-8")
  if (!css.trim()) {
    return html
  }

  // Insert CSS into head
  const styleTag = `<style type="text/css">\n${css}\n</style>`
  return html.replace("</head>", `${styleTag}\n</head>`)
}

async function buildTemplates() {
  console.log("📧 Building email templates...\n")

  const templateFiles = readdirSync(emailsDir).filter((f) => f.endsWith(".vue") && !f.startsWith("_"))

  let successCount = 0
  let failCount = 0

  for (const file of templateFiles) {
    const name = basename(file, ".vue")
    const templatePath = resolve(emailsDir, file)

    try {
      // Render to static HTML with Maizzle (styles inlined, doctype added)
      const { html } = await render(templatePath, RENDER_OPTIONS)

      // Optionally inline global CSS
      const output = inlineGlobalCSS(html)

      const outputPath = resolve(OUTPUT_DIR, `${name}.html`)
      writeFileSync(outputPath, output, "utf-8")
      console.log(`   ✓ ${name}.html`)
      successCount++
    } catch (error) {
      console.error(`   ✗ ${file}:`, error instanceof Error ? error.message : error)
      failCount++
    }
  }

  console.log(`\n✅ ${successCount} templates built to: ${OUTPUT_DIR}`)

  if (failCount > 0) {
    console.error(`❌ ${failCount} template(s) failed to build`)
    process.exit(1)
  }
}

buildTemplates()