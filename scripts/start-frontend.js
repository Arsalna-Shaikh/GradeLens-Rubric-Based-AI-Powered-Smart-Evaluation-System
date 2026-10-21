/**
 * Starts the Next.js frontend on the port requested by the platform preview.
 * Falls back to 3000 for local development so `npm run dev` works everywhere.
 *
 * Usage:
 *   node scripts/start-frontend.js [dev|start]
 */
const { spawn } = require("child_process")
const path = require("path")

const command = process.argv[2] || "dev"
const port = process.env.PORT || "3000"

// Resolve the Next.js CLI entry so this works on Windows, macOS and Linux.
const nextBin = require.resolve("next/dist/bin/next")

const args = [nextBin, command, "-p", port, "-H", "0.0.0.0"]
const child = spawn(process.execPath, args, {
  stdio: "inherit",
  cwd: path.resolve(__dirname, ".."),
})

child.on("exit", (code) => {
  process.exit(code ?? 0)
})
