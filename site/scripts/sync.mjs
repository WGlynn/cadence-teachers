// Copy the lab's single source of truth into the app before dev/build.
import { copyFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
const here = dirname(fileURLToPath(import.meta.url))
mkdirSync(join(here, '..', 'src', 'data'), { recursive: true })
copyFileSync(join(here, '..', '..', 'experiments', 'atlas.json'), join(here, '..', 'src', 'data', 'atlas.json'))
console.log('synced experiments/atlas.json')
