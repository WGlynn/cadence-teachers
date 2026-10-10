import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence, useInView, animate } from 'motion/react'
import { EXPS, TRACKS, VCOLOR, VLABEL, VERDICTS, STANDING, STORY, ISSUES, RULES, byId, mdUrl } from '../data'
import { Bars, Dots, Line, Lineage, Spark } from './Charts'

const ease = [0.22, 1, 0.36, 1]

export function Counter({ to, delay = 0 }) {
  const ref = useRef()
  const inView = useInView(ref, { once: true })
  useEffect(() => {
    if (!inView) return
    const c = animate(0, to, { duration: 1.6, delay, ease, onUpdate: (v) => { if (ref.current) ref.current.textContent = Math.round(v) } })
    return () => c.stop()
  }, [inView, to, delay])
  return <span ref={ref}>0</span>
}

export function Reveal({ children, delay = 0, y = 24, className }) {
  return (
    <motion.div className={className} initial={{ opacity: 0, y }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-10% 0px' }}
      transition={{ duration: 0.8, delay, ease }}>
      {children}
    </motion.div>
  )
}

export function SectionHead({ num, title, sub }) {
  return (
    <Reveal className="sec-head">
      <span className="sec-num">{num}</span>
      <h2>{title}</h2>
      {sub && <p>{sub}</p>}
    </Reveal>
  )
}

/* ---------------- verdict filter chips ---------------- */
export function VerdictChips({ filter, setFilter }) {
  const counts = Object.fromEntries(VERDICTS.map((v) => [v, EXPS.filter((e) => e.verdict === v).length]))
  const toggle = (v) => {
    const n = new Set(filter)
    if (n.size === VERDICTS.length) { n.clear(); n.add(v) } else if (n.has(v)) n.delete(v); else n.add(v)
    setFilter(n.size ? n : new Set(VERDICTS))
  }
  return VERDICTS.filter((v) => counts[v]).map((v) => (
    <button key={v} className="chip" aria-pressed={filter.has(v)} onClick={() => toggle(v)} style={{ color: VCOLOR[v] }}>
      <span className={'dot' + (STANDING.has(v) ? '' : ' ring')} style={{ background: VCOLOR[v] }} />
      <span style={{ color: 'var(--paper)' }}>{VLABEL[v]} {counts[v]}</span>
    </button>
  ))
}

/* ---------------- specimen grid (list view of the constellation) ---------------- */
export function SpecimenGrid({ filter, onPick }) {
  const items = EXPS.filter((e) => filter.has(e.verdict))
  return (
    <motion.div layout className="grid">
      <AnimatePresence>
        {items.map((e, i) => (
          <motion.button layout key={e.id} className={'tile' + (STANDING.has(e.verdict) ? '' : ' hollow')} style={{ '--c': VCOLOR[e.verdict] }}
            initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.35, delay: Math.min(i * 0.012, 0.3) }} whileHover={{ y: -4 }} onClick={() => onPick(e.id)}>
            <div className="tid">{e.id} · {VLABEL[e.verdict]}</div>
            <div className="tname">{e.name}</div>
            <Spark chart={e.chart} color={VCOLOR[e.verdict]} />
          </motion.button>
        ))}
      </AnimatePresence>
    </motion.div>
  )
}

/* ---------------- scrollytelling ---------------- */
function StoryViz({ step }) {
  const e = byId[step.id]
  const chart = e.chart
  let viz
  if (step.kind === 'dots') viz = <Dots chart={chart} pick={step.pick} />
  else if (step.kind === 'line') viz = <Line chart={chart} />
  else if (step.kind === 'lineage') viz = <Lineage chart={chart} />
  else viz = <Bars chart={chart} pick={step.pick} log={step.log} />
  return (
    <motion.div key={step.id} initial={{ opacity: 0, y: 30, filter: 'blur(8px)' }} animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, y: -30, filter: 'blur(8px)' }} transition={{ duration: 0.55, ease }}>
      {viz}
      <p style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--muted)', marginTop: 14 }}>
        {chart.title}{step.log ? ' · log scale' : ''}
      </p>
    </motion.div>
  )
}

export function Story({ onPick }) {
  const [active, setActive] = useState(0)
  const refs = useRef([])
  useEffect(() => {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) setActive(Number(en.target.dataset.i)) })
    }, { rootMargin: '-45% 0px -45% 0px' })
    refs.current.forEach((r) => r && io.observe(r))
    return () => io.disconnect()
  }, [])
  const step = STORY[active]
  return (
    <div className="story">
      <div className="story-viz">
        <div className="viz-top"><span>{step.id}</span><span>{String(active + 1).padStart(2, '0')} / {String(STORY.length).padStart(2, '0')}</span></div>
        <div className="viz-body"><AnimatePresence mode="wait"><StoryViz step={step} /></AnimatePresence></div>
        <motion.div style={{ height: 3, background: 'var(--gold)', transformOrigin: 'left' }} animate={{ scaleX: (active + 1) / STORY.length }} transition={{ ease }} />
      </div>
      <div>
        {STORY.map((s, i) => (
          <div key={s.id} ref={(r) => (refs.current[i] = r)} data-i={i} className={'step' + (i === active ? ' on' : '')}>
            <div className="k">{s.kicker}</div>
            <h3>{s.claim}</h3>
            <div className="big">{s.big}</div>
            <div className="vs">{s.vs}</div>
            <button className="src" onClick={() => onPick(s.id)}>{s.id} · {VLABEL[byId[s.id].verdict]} →</button>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ---------------- timeline river ---------------- */
export function River({ onPick }) {
  const ref = useRef()
  const inView = useInView(ref, { once: true, margin: '-15% 0px' })
  const LEFT = 200, STEP = 26, ROWH = 46, TOP = 30
  const W = LEFT + STEP * EXPS.length + 30, H = TOP + ROWH * TRACKS.length
  const [tip, setTip] = useState(null)
  const days = []
  EXPS.forEach((e, i) => { const d = e.date.slice(5, 10); if (!days.length || days[days.length - 1].d !== d) days.push({ d, i }) })
  return (
    <div className="river" ref={ref} style={{ position: 'relative' }}>
      <svg viewBox={`0 0 ${W} ${H}`}>
        {days.map((d) => (
          <g key={d.d + d.i}>
            <line x1={LEFT + STEP * d.i - 4} x2={LEFT + STEP * d.i - 4} y1={16} y2={H} stroke="#262d3a" strokeDasharray="2 4" />
            <text x={LEFT + STEP * d.i} y={14}>{d.d}</text>
          </g>
        ))}
        {TRACKS.map((t, ti) => {
          const y = TOP + ti * ROWH + ROWH / 2
          return (
            <g key={t}>
              <text x={LEFT - 14} y={y + 4} textAnchor="end" style={{ fill: 'var(--paper)', fontSize: 12 }}>{t}</text>
              <motion.line x1={LEFT} x2={W - 16} y1={y} y2={y} stroke="#262d3a" strokeWidth={2}
                initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}} transition={{ duration: 1.2, delay: ti * 0.06 }} />
            </g>
          )
        })}
        {EXPS.map((e, i) => {
          const y = TOP + TRACKS.indexOf(e.track) * ROWH + ROWH / 2, x = LEFT + STEP * i + STEP / 2
          const c = VCOLOR[e.verdict], solid = STANDING.has(e.verdict)
          return (
            <motion.circle key={e.id} cx={x} cy={y} r={8} fill={solid ? c : '#10141b'} stroke={c} strokeWidth={solid ? 0 : 2.5}
              initial={{ scale: 0, opacity: 0 }} animate={inView ? { scale: 1, opacity: 1 } : {}} transition={{ delay: 0.4 + i * 0.03, type: 'spring', stiffness: 300, damping: 18 }}
              whileHover={{ scale: 1.6 }} onMouseEnter={() => setTip({ e, x, y })} onMouseLeave={() => setTip(null)} onClick={() => onPick(e.id)} />
          )
        })}
      </svg>
      {tip && (
        <div className="star-tip" style={{ position: 'absolute', left: `${(tip.x / W) * 100}%`, top: `${(tip.y / H) * 100}%`, marginTop: 20 }}>
          <b style={{ color: VCOLOR[tip.e.verdict] }}>{tip.e.id}</b>{tip.e.name}
        </div>
      )}
    </div>
  )
}

/* ---------------- mistakes -> rules ---------------- */
export function Mistakes() {
  const [sel, setSel] = useState(ISSUES[0][0])
  const max = ISSUES[0][1]
  return (
    <div className="mist">
      <div>
        {ISSUES.map(([k, n], i) => (
          <button key={k} className={'mrow' + (sel === k ? ' on' : '')} onMouseEnter={() => setSel(k)} onClick={() => setSel(k)}>
            <span className="lab">{k}</span>
            <motion.span className="bar" initial={{ scaleX: 0 }} whileInView={{ scaleX: n / max }} viewport={{ once: true }} transition={{ duration: 1, delay: i * 0.07, ease }} />
            <span className="n">{n}</span>
          </button>
        ))}
      </div>
      <div className="rulebox">
        <AnimatePresence mode="wait">
          <motion.div key={sel} className="rule" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.35 }}>
            <small>{sel} → the rule now</small>
            {RULES[sel] || 'Logged as a lesson.'}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}

/* ---------------- drawer ---------------- */
export function Drawer({ id, onClose }) {
  useEffect(() => {
    const k = (ev) => ev.key === 'Escape' && onClose()
    window.addEventListener('keydown', k)
    return () => window.removeEventListener('keydown', k)
  }, [onClose])
  const e = id && byId[id]
  return (
    <AnimatePresence>
      {e && (
        <>
          <motion.div className="scrim" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} />
          <motion.aside className="drawer" role="dialog" aria-label={e.name} initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 260, damping: 32 }}>
            <button className="close" onClick={onClose} aria-label="Close">×</button>
            <div className="did">{e.id} · {e.track} · {e.date}</div>
            <h3>{e.name}</h3>
            <span className="vbadge" style={{ color: VCOLOR[e.verdict], borderColor: VCOLOR[e.verdict] }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: STANDING.has(e.verdict) ? VCOLOR[e.verdict] : 'transparent', border: `2px solid ${VCOLOR[e.verdict]}` }} />
              {VLABEL[e.verdict]}
            </span>
            <p className="headline">{e.headline}</p>
            {e.chart?.bars?.length ? <><p style={{ fontSize: 13, color: 'var(--muted)', margin: '0 0 6px' }}>{e.chart.title}</p><Bars chart={e.chart} compact /></> : null}
            <dl>
              <dt>Question</dt><dd>{e.question}</dd>
              <dt>Lesson</dt><dd>{e.lesson}</dd>
              <dt>Status</dt><dd>{e.verdict_note}</dd>
              <dt>Issues</dt><dd className="tags">{e.process_issues.filter((x) => x !== 'none').map((x) => <span key={x} className="tag">{x}</span>)}{e.process_issues.every((x) => x === 'none') ? 'none' : null}</dd>
            </dl>
            <a className="cta" href={mdUrl(e.id)} target="_blank" rel="noreferrer">Full summary + reflection →</a>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
