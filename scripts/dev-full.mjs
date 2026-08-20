/* Runs the FastAPI backend (:8000) and Vite frontend (:5173) together. */
import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const venvPython = path.join(root, 'backend', '.venv', 'Scripts', 'python.exe')

const backend = spawn(venvPython, ['-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'], {
  cwd: path.join(root, 'backend'),
  stdio: ['ignore', 'inherit', 'inherit'],
  shell: false,
})
const frontend = spawn('npm', ['run', 'dev'], { cwd: root, stdio: 'inherit', shell: true })

const shutdown = () => {
  backend.kill('SIGTERM')
  frontend.kill('SIGTERM')
  process.exit(0)
}
process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
backend.on('exit', (code) => {
  if (code !== 0) frontend.kill('SIGTERM')
})
