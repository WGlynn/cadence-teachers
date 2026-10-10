import atlas from './data/atlas.json'

export const EXPS = atlas
export const byId = Object.fromEntries(EXPS.map((e) => [e.id, e]))
export const TRACKS = [...new Set(EXPS.map((e) => e.track))]
export const GH = 'https://github.com/WGlynn/cadence-teachers'
export const mdUrl = (id) => `${GH}/blob/main/experiments/${id}.md`

export const VERDICTS = ['CROSSED', 'SUPPORTIVE', 'BOUNDARY', 'NULL', 'SUPERSEDED', 'VOID', 'RETRACTED']
// Colour carries meaning: gold = milestone met, teal = supports, blue = boundary found,
// greys = nothing (yet), coral = broken / withdrawn.
export const VCOLOR = {
  CROSSED: '#f5b942', SUPPORTIVE: '#3fc1b0', BOUNDARY: '#7aa7ff', NULL: '#9aa0aa',
  SUPERSEDED: '#6b7382', VOID: '#ff6b5b', RETRACTED: '#ff8f80',
}
export const VLABEL = {
  CROSSED: 'Crossed', SUPPORTIVE: 'Supportive', BOUNDARY: 'Boundary', NULL: 'Null',
  SUPERSEDED: 'Superseded', VOID: 'Void', RETRACTED: 'Retracted',
}
export const STANDING = new Set(['CROSSED', 'SUPPORTIVE', 'BOUNDARY'])

export const count = (pred) => EXPS.filter(pred).length
export const STATS = [
  { n: EXPS.length, label: 'experiments' },
  { n: count((e) => e.verdict === 'CROSSED'), label: 'milestones crossed', color: VCOLOR.CROSSED },
  { n: count((e) => e.verdict === 'SUPPORTIVE' || e.verdict === 'BOUNDARY'), label: 'supportive', color: VCOLOR.SUPPORTIVE },
  { n: count((e) => ['NULL', 'VOID', 'RETRACTED'].includes(e.verdict)), label: 'nulls & voids, kept', color: VCOLOR.VOID },
  { n: count((e) => e.process_issues.includes('bug in script')), label: 'own bugs caught' },
]

// The mistake -> rule ledger (mirrors ISSUE_RULES in experiments/build_atlas.py).
export const RULES = {
  'under-powered': 'Power the run for the pilot\'s effect size.',
  'at ceiling': 'Pilot the knob first; the effect must sit away from 0% and 100%.',
  'bug in script': 'Surprising result? Audit the accounting path before theorising.',
  'stale records': 'Every experiment ships a Summary + Reflection.',
  'metric gameable': 'A do-nothing policy must not pass the score.',
  'nothing varied': 'Check the compared thing actually varies.',
  'pilot != run conditions': 'A smoke test is not a pilot. Print every link of the chain.',
  'effect window too small': 'Order the sweep so a timeout still leaves the decisive number.',
  'version drift': 'Never overwrite outputs; stamp the library version.',
}

export const ISSUES = (() => {
  const c = {}
  EXPS.forEach((e) => e.process_issues.forEach((i) => { if (i !== 'none') c[i] = (c[i] || 0) + 1 }))
  return Object.entries(c).sort((a, b) => b[1] - a[1])
})()

// Scroll story. Numbers are NOT typed here: every chart reads its bars from atlas.json.
export const STORY = [
  { id: 'EXP-28', kicker: 'Teaching', claim: 'A teacher beats the world.', big: '8 / 8', vs: 'vs 1 / 8 alone', kind: 'dots', pick: [0, 1] },
  { id: 'EXP-08', kicker: 'Worth', claim: "Fakes can't fake worth.", big: '+0.42', vs: 'genuine vs -0.58 fake', kind: 'bars' },
  { id: 'EXP-19', kicker: 'Teamwork', claim: 'Two halves make a whole.', big: '+0.58', vs: 'together, ~0 apart', kind: 'bars', pick: [0, 1, 2, 3] },
  { id: 'EXP-22', kicker: 'Generations', claim: 'Skill survives the bloodline.', big: '94%', vs: 'per generation; labels 0%', kind: 'lineage' },
  { id: 'EXP-30', kicker: 'Restraint', claim: 'Too much teaching hurts.', big: '8 → 1', vs: 'students passing as drilling grows', kind: 'line' },
  { id: 'EXP-33', kicker: 'Memory', claim: 'Stale teaching was the ceiling.', big: '.79 → .99', vs: 'a bigger brain only got .82', kind: 'bars' },
  { id: 'EXP-37', kicker: 'Signals', claim: "Weights can't tell real from fake.", big: '2.59 ≈ 2.44', vs: 'genuine vs opposite-rule lesson', kind: 'bars' },
  { id: 'EXP-36', kicker: 'Attacks', claim: 'Self-reports are an 80x hole.', big: '13.09', vs: 'fake pay; probe + ledger: 0.04', kind: 'bars', log: true },
  { id: 'EXP-38', kicker: 'Defence', claim: 'Never pay twice for one lesson.', big: '69% → 30%', vs: 'lessons soaked by attackers', kind: 'bars' },
  { id: 'EXP-35b', kicker: 'Discovery', claim: 'A royalty makes brains explore.', big: '.51 → .63', vs: 'late discovery, share 0 vs 0.9', kind: 'bars' },
]
