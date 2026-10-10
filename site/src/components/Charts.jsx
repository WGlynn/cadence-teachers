import { motion } from 'motion/react'

const fmt = (v) => (Math.abs(v) >= 10 ? v.toFixed(Number.isInteger(v) ? 0 : 1) : Number.isInteger(v) ? String(v) : v.toFixed(Math.abs(v) < 0.1 ? 3 : 2).replace(/^(-?)0\./, '$1.'))
const ease = [0.22, 1, 0.36, 1]

/** Horizontal bars, polarity-aware, optional log scale and SEM whiskers. */
export function Bars({ chart, pick, log = false, color = '#f5b942', compact = false }) {
  const bars = (pick ? pick.map((i) => chart.bars[i]) : chart.bars).filter(Boolean)
  if (!bars.length) return null
  const W = 640, ROW = compact ? 30 : 46, BH = compact ? 14 : 22, LABEL = compact ? 150 : 190, PAD = 64
  const tf = (v) => (log ? Math.sign(v) * Math.log10(1 + Math.abs(v) * 100) : v)
  const vals = bars.flatMap((b) => [tf(b.value - (b.sem || 0)), tf(b.value + (b.sem || 0))])
  const lo = Math.min(0, ...vals), hi = Math.max(0, ...vals) || 1
  const x0 = LABEL + (lo < 0 ? PAD : 8), x1 = W - PAD
  const sx = (v) => x0 + ((tf(v) - lo) / (hi - lo)) * (x1 - x0)
  const zx = sx(0), H = ROW * bars.length + 10
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={chart.title}>
      <line x1={zx} x2={zx} y1={0} y2={H} stroke="#3a4252" />
      {bars.map((b, i) => {
        const y = 6 + i * ROW, xe = sx(b.value), neg = b.value < 0
        const left = Math.min(zx, xe), w = Math.max(2, Math.abs(xe - zx))
        const fill = neg ? '#ff6b5b' : color
        return (
          <g key={b.label + i}>
            <text x={LABEL - 12} y={y + BH / 2 + 4} textAnchor="end">{b.label.length > 26 ? b.label.slice(0, 25) + '…' : b.label}</text>
            <motion.rect y={y} height={BH} rx={4} fill={fill}
              initial={{ x: zx, width: 0 }} animate={{ x: left, width: w }}
              transition={{ duration: 0.9, delay: 0.08 * i, ease }} />
            {b.sem ? (
              <motion.line y1={y + BH / 2} y2={y + BH / 2} x1={sx(b.value - b.sem)} x2={sx(b.value + b.sem)} stroke="#efe8d8" strokeWidth={1.4}
                initial={{ opacity: 0 }} animate={{ opacity: 0.9 }} transition={{ delay: 0.9 + 0.08 * i }} />
            ) : null}
            <motion.text className="val" y={y + BH / 2 + 4} x={neg ? left - 8 : left + w + 8} textAnchor={neg ? 'end' : 'start'}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 + 0.08 * i }}>
              {fmt(b.value)}
            </motion.text>
          </g>
        )
      })}
    </svg>
  )
}

/** Students as figures: who passed, world alone vs teacher (EXP-28 style, counts of 8). */
export function Dots({ chart, pick }) {
  const rows = pick.map((i) => chart.bars[i])
  const total = 8
  return (
    <svg className="chart" viewBox="0 0 640 300" role="img" aria-label={chart.title}>
      {rows.map((r, ri) => (
        <g key={r.label} transform={`translate(0 ${30 + ri * 140})`}>
          <text x={0} y={0} style={{ fontSize: 13 }}>{r.label.replace('M=40 ', '40 trips: ').replace('world', 'learning alone').replace('teacher', 'with a teacher')}</text>
          {Array.from({ length: total }).map((_, k) => {
            const on = k < r.value
            return (
              <motion.g key={k} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + k * 0.07 + ri * 0.5, ease }}>
                <circle cx={36 + k * 74} cy={44} r={14} fill={on ? '#f5b942' : 'none'} stroke={on ? '#f5b942' : '#4a5263'} strokeWidth={2} />
                <path d={`M${36 + k * 74 - 22},${92} q22,-34 44,0`} fill={on ? '#f5b942' : 'none'} stroke={on ? '#f5b942' : '#4a5263'} strokeWidth={2} />
              </motion.g>
            )
          })}
          <text className="val" x={640} y={0} textAnchor="end" style={{ fontSize: 14 }}>{r.value} / {total}</text>
        </g>
      ))}
    </svg>
  )
}

/** Line over a budget axis (EXP-30: passing students vs teaching trips). */
export function Line({ chart }) {
  const pts = chart.bars
  const W = 640, H = 330, L = 50, R = 30, T = 30, B = 50
  const max = Math.max(...pts.map((p) => p.value))
  const sx = (i) => L + (i / (pts.length - 1)) * (W - L - R)
  const sy = (v) => T + (1 - v / max) * (H - T - B)
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${sx(i)},${sy(p.value)}`).join(' ')
  const area = `${d} L${sx(pts.length - 1)},${H - B} L${sx(0)},${H - B} Z`
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={chart.title}>
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#f5b942" stopOpacity=".35" /><stop offset="1" stopColor="#f5b942" stopOpacity="0" /></linearGradient>
      </defs>
      <line x1={L} x2={W - R} y1={H - B} y2={H - B} stroke="#3a4252" />
      <motion.path d={area} fill="url(#lg)" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8, duration: 0.8 }} />
      <motion.path d={d} fill="none" stroke="#f5b942" strokeWidth={3} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.3, ease }} />
      {pts.map((p, i) => (
        <motion.g key={p.label} initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.25 + i * 0.3 }}>
          <circle cx={sx(i)} cy={sy(p.value)} r={7} fill="#0a0c10" stroke="#f5b942" strokeWidth={3} />
          <text className="val" x={sx(i)} y={sy(p.value) - 16} textAnchor="middle" style={{ fontSize: 15 }}>{p.value}/8</text>
          <text x={sx(i)} y={H - B + 24} textAnchor="middle">{p.label.replace('M=', '')} trips</text>
        </motion.g>
      ))}
    </svg>
  )
}

/** Lineage: grading carries the skill down generations; labels never take hold (EXP-22). */
export function Lineage({ chart }) {
  const grade = chart.bars[0]?.value ?? 0, label = chart.bars[2]?.value ?? 0
  const G = 5, W = 640
  const row = (y, pass, title, delay) => (
    <g transform={`translate(0 ${y})`}>
      <text x={0} y={-26} style={{ fontSize: 13 }}>{title}</text>
      {Array.from({ length: G + 1 }).map((_, g) => {
        const x = 30 + g * ((W - 60) / G)
        const alive = g === 0 || pass > 0
        return (
          <g key={g}>
            {g > 0 && (
              <motion.line x1={x - (W - 60) / G + 16} x2={x - 16} y1={0} y2={0} stroke={alive ? '#f5b942' : '#4a5263'} strokeWidth={2}
                strokeDasharray={alive ? '0' : '4 5'} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: delay + g * 0.25, duration: 0.3 }} />
            )}
            <motion.circle cx={x} cy={0} r={14} fill={alive ? '#f5b942' : 'none'} fillOpacity={alive ? Math.pow(pass / 100, g) : 0}
              stroke={alive ? '#f5b942' : '#4a5263'} strokeWidth={2}
              initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: delay + g * 0.25, type: 'spring', stiffness: 260, damping: 16 }} />
            <text x={x} y={36} textAnchor="middle">{g === 0 ? 'parent' : `gen ${g}`}</text>
          </g>
        )
      })}
      <text className="val" x={W} y={-26} textAnchor="end" style={{ fontSize: 14 }}>{pass}% per generation</text>
    </g>
  )
  return (
    <svg className="chart" viewBox="0 0 640 300" role="img" aria-label={chart.title}>
      {row(70, grade, 'Teacher grades the child (+1 for the right move)', 0.1)}
      {row(220, label, 'Teacher hands over answers (labels)', 0.9)}
    </svg>
  )
}

/** Tiny sparkline of an experiment's bars, for specimen tiles. */
export function Spark({ chart, color }) {
  const bars = chart?.bars || []
  if (!bars.length) return <svg viewBox="0 0 100 26" />
  const max = Math.max(...bars.map((b) => Math.abs(b.value))) || 1
  const w = 100 / bars.length
  return (
    <svg viewBox="0 0 100 26" preserveAspectRatio="none">
      <line x1="0" x2="100" y1="13" y2="13" stroke="#262d3a" />
      {bars.map((b, i) => {
        const h = (Math.abs(b.value) / max) * 12
        return <rect key={i} x={i * w + w * 0.18} width={w * 0.64} y={b.value >= 0 ? 13 - h : 13} height={Math.max(1, h)} rx={1.5} fill={b.value >= 0 ? color : '#ff6b5b'} opacity={0.85} />
      })}
    </svg>
  )
}
