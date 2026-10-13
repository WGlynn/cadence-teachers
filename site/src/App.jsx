import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react'
import { motion, useScroll, useTransform } from 'motion/react'
import { STATS, VERDICTS, GH, EXPS } from './data'
import { Counter, SectionHead, VerdictChips, SpecimenGrid, Story, River, Mistakes, Drawer, Reveal } from './components/Sections'

const Hero3D = lazy(() => import('./components/Hero3D'))
const Constellation3D = lazy(() => import('./components/Constellation3D'))

// Pause a WebGL scene when it scrolls out of view (saves GPU + battery).
function useOnScreen(ref, margin = '0px') {
  const [on, setOn] = useState(true)
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => setOn(e.isIntersecting), { rootMargin: margin })
    if (ref.current) io.observe(ref.current)
    return () => io.disconnect()
  }, [ref, margin])
  return on
}

const webgl = (() => {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')) } catch { return false }
})()

export default function App() {
  const [pick, setPick] = useState(null)
  const [filter, setFilter] = useState(new Set(VERDICTS))
  const [view, setView] = useState(webgl ? '3d' : 'grid')
  const onPick = useCallback((id) => setPick(id), [])
  const heroRef = useRef(), galaxyRef = useRef()
  const heroOn = useOnScreen(heroRef), galaxyOn = useOnScreen(galaxyRef, '200px')
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 160])
  // Deep links (#story etc.): the target renders after the browser's own anchor jump, so jump again.
  useEffect(() => {
    const h = window.location.hash.slice(1)
    if (!h) return
    const t = setTimeout(() => document.getElementById(h)?.scrollIntoView({ behavior: 'instant' }), 350)
    return () => clearTimeout(t)
  }, [])
  const heroO = useTransform(scrollYProgress, [0, 0.8], [1, 0])

  return (
    <>
      <header className="nav">
        <a className="brand" href="#top">Cadence <i>Lab Atlas</i></a>
        <nav>
          <a href="#explore">Explore</a><a href="#story">Findings</a><a href="#river">Timeline</a><a href="#mistakes">Mistakes</a>
          <a className="gh" href={GH} target="_blank" rel="noreferrer">GitHub ↗</a>
        </nav>
      </header>

      <section className="hero" id="top" ref={heroRef}>
        {webgl && <div className="hero-canvas"><Suspense fallback={null}><Hero3D active={heroOn} /></Suspense></div>}
        <motion.div className="hero-copy" style={{ y: heroY, opacity: heroO }}>
          <div className="wrap">
            <motion.div className="eyebrow" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
              An open lab notebook · built on Cadence
            </motion.div>
            <motion.h1 initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1.1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}>
              Small brains, <em>teaching</em> each other.
            </motion.h1>
            {/* Front-page intro: keep verbatim (Will 2026-10-10, "keep this on front page"). */}
            <motion.p className="lede" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9, delay: 0.6 }}>
              We grow small <b>Cadence</b> brains and ask whether one can measurably teach another, and whether the worth of that teaching can be priced from outcomes instead of from what the brain looks like inside. The goal is a market that pays for <b>teaching ability passed down generations</b>, where credit follows the lineage of what was learned. This atlas collects every reflection so far, the wins and, just as proudly, the nulls, voids and our own retracted mistakes.
            </motion.p>
            <div className="stats">
              {STATS.map((s, i) => (
                <motion.div className="stat" key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 + i * 0.12 }}>
                  <div className="n"><Counter to={s.n} delay={0.8 + i * 0.12} /></div>
                  <div className="l">{s.color && <i style={{ background: s.color }} />}{s.label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
        <div className="scrollcue">SCROLL ↓</div>
      </section>

      <section className="block" id="explore">
        <div className="wrap">
          <SectionHead num="01" title="Every experiment, a star." sub="Clustered by research track. Gold = milestone crossed. Rings = no standing result. Drag to orbit, click to open." />
          <Reveal>
            {view === '3d' ? (
              <div className="galaxy" ref={galaxyRef}>
                <div className="galaxy-ui"><VerdictChips filter={filter} setFilter={setFilter} /></div>
                <Suspense fallback={null}><Constellation3D filter={filter} onPick={onPick} active={galaxyOn} /></Suspense>
                <div className="galaxy-hint">drag · scroll to zoom · click a star</div>
              </div>
            ) : (
              <>
                <div className="galaxy-ui" style={{ position: 'static' }}><VerdictChips filter={filter} setFilter={setFilter} /></div>
                <SpecimenGrid filter={filter} onPick={onPick} />
              </>
            )}
          </Reveal>
          <div className="toggle-row">
            {webgl && <button className="ghost" onClick={() => setView(view === '3d' ? 'grid' : '3d')}>{view === '3d' ? 'Show as cards' : 'Show as constellation'}</button>}
          </div>
        </div>
      </section>

      <section className="block" id="story">
        <div className="wrap">
          <SectionHead num="02" title="What we found." sub="Scroll. Every number is read live from the lab's data file." />
          <Story onPick={onPick} />
        </div>
      </section>

      <section className="block" id="river">
        <div className="wrap">
          <SectionHead num="03" title={`${EXPS.length} runs, in order.`} sub="Run order, one lane per track. Scroll sideways for the latest; hover a dot, click to open." />
          <Reveal><River onPick={onPick} /></Reveal>
        </div>
      </section>

      <section className="block" id="mistakes">
        <div className="wrap">
          <SectionHead num="04" title="Every mistake became a rule." sub="Process failures tagged across all reflections. Hover one." />
          <Mistakes />
        </div>
      </section>

      <footer>
        <div className="wrap">
          <Reveal><div className="big">Run the next one. <em>Nulls welcome.</em></div></Reveal>
          <div className="links">
            <a className="cta" href={GH} target="_blank" rel="noreferrer">GitHub repo →</a>
            <a className="cta" href={`${GH}/blob/main/CONTRIBUTING.md`} target="_blank" rel="noreferrer">How to contribute →</a>
            <a className="cta" href={`${GH}/blob/main/experiments/atlas.json`} target="_blank" rel="noreferrer">Raw data →</a>
          </div>
          <p className="fine">
            {EXPS.length} experiments on small Cadence brains (github.com/muellerberndt/cadence, by Bernhard Mueller), small tasks, one PC.
            Nothing here is shown at scale. Verdicts are current after reruns; voids and retractions are kept on purpose.
            Code GPL-3.0, write-ups CC BY 4.0.
          </p>
        </div>
      </footer>

      <Drawer id={pick} onClose={() => setPick(null)} />
    </>
  )
}
