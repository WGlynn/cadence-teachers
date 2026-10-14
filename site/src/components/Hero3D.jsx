import { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import * as THREE from 'three'
import { EXPS, VCOLOR, STANDING } from '../data'

// Deterministic RNG so the lineage looks the same on every visit.
function rng(seed) {
  return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 }
}

/** The experiments themselves: one node per experiment, run days left to right, coloured by verdict; edges join
 *  consecutive experiments of the same track (each question led to the next); pulses = lessons in flight.
 *  The node count is the experiment count, so the picture grows with the atlas. */
function Lineage({ reduced }) {
  const group = useRef()
  const pulses = useRef()
  const { nodes, edges } = useMemo(() => {
    const r = rng(11), byDay = new Map(), nodes = [], edges = [], at = {}, last = {}
    EXPS.forEach((e) => { const d = e.date.slice(0, 10); if (!byDay.has(d)) byDay.set(d, []); byDay.get(d).push(e) })
    const days = [...byDay.keys()].sort(), G = days.length, gap = G > 1 ? Math.min(2.4, 12 / (G - 1)) : 0   // span <= 12 keeps the newest day in frame
    days.forEach((d, g) => {
      const day = byDay.get(d), n = day.length
      day.forEach((e, i) => {
        const a = (i / n) * Math.PI * 2 + g * 0.7, rad = 0.8 + Math.min(1.7, n * 0.1) + r() * 0.4
        at[e.id] = nodes.length
        nodes.push({ p: new THREE.Vector3((g - (G - 1) / 2) * gap, Math.sin(a) * rad, Math.cos(a) * rad),
                     c: VCOLOR[e.verdict], crossed: e.verdict === 'CROSSED', solid: STANDING.has(e.verdict) })
      })
    })
    EXPS.forEach((e) => { if (last[e.track] !== undefined) edges.push([at[last[e.track]], at[e.id]]); last[e.track] = e.id })
    return { nodes, edges }
  }, [])

  const lineGeo = useMemo(() => {
    const pos = new Float32Array(edges.length * 6)
    edges.forEach(([a, b], i) => { nodes[a].p.toArray(pos, i * 6); nodes[b].p.toArray(pos, i * 6 + 3) })
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); return g
  }, [nodes, edges])

  const P = 48
  const pulseState = useMemo(() => Array.from({ length: P }, (_, i) => ({ e: i % edges.length, t: (i * 0.137) % 1, v: 0.18 + (i % 5) * 0.05 })), [edges.length])
  const tmp = useMemo(() => new THREE.Object3D(), [])
  const v = useMemo(() => new THREE.Vector3(), [])

  useFrame((state, dt) => {
    const t = state.clock.elapsedTime
    if (group.current) {
      group.current.rotation.x = Math.sin(t * 0.07) * 0.18 + state.pointer.y * 0.15
      group.current.rotation.y = (reduced ? 0 : t * 0.045) + state.pointer.x * 0.25
    }
    if (!pulses.current) return
    pulseState.forEach((s, i) => {
      if (!reduced) s.t += dt * s.v
      if (s.t > 1) { s.t = 0; s.e = (s.e * 7 + 3) % edges.length }
      const [a, b] = edges[s.e]
      v.copy(nodes[a].p).lerp(nodes[b].p, s.t)
      tmp.position.copy(v)
      tmp.scale.setScalar(0.06 + Math.sin(s.t * Math.PI) * 0.05)
      tmp.updateMatrix()
      pulses.current.setMatrixAt(i, tmp.matrix)
    })
    pulses.current.instanceMatrix.needsUpdate = true
  })

  return (
    <group ref={group}>
      <lineSegments geometry={lineGeo}>
        <lineBasicMaterial color="#5b6a86" transparent opacity={0.35} />
      </lineSegments>
      {nodes.map((n, i) => (
        <mesh key={i} position={n.p}>
          <icosahedronGeometry args={[n.crossed ? 0.26 : 0.17, 2]} />
          <meshStandardMaterial color={n.c} emissive={n.c}
            emissiveIntensity={n.crossed ? 2.2 : n.solid ? 0.9 : 0.3} roughness={0.35} metalness={0.2} />
        </mesh>
      ))}
      <instancedMesh ref={pulses} args={[null, null, P]}>
        <sphereGeometry args={[1, 10, 10]} />
        <meshBasicMaterial color="#ffd27a" toneMapped={false} />
      </instancedMesh>
    </group>
  )
}

function Dust() {
  const ref = useRef()
  const geo = useMemo(() => {
    const r = rng(3), n = 900, pos = new Float32Array(n * 3)
    for (let i = 0; i < n; i++) { pos[i * 3] = (r() - 0.5) * 40; pos[i * 3 + 1] = (r() - 0.5) * 22; pos[i * 3 + 2] = (r() - 0.5) * 30 - 6 }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); return g
  }, [])
  useFrame((s) => { if (ref.current) ref.current.rotation.y = s.clock.elapsedTime * 0.01 })
  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial size={0.035} color="#b9b2a3" transparent opacity={0.55} sizeAttenuation />
    </points>
  )
}

export default function Hero3D({ active = true }) {
  const reduced = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  return (
    <Canvas style={{ width: "100%", height: "100%" }} frameloop={active ? 'always' : 'never'} dpr={[1, 1.75]}
      camera={{ position: [0, 0.6, 11.5], fov: 45 }} gl={{ antialias: true, powerPreference: 'high-performance' }}>
      <color attach="background" args={['#0a0c10']} />
      <fog attach="fog" args={['#0a0c10', 10, 26]} />
      <ambientLight intensity={0.35} />
      <pointLight position={[6, 5, 6]} intensity={40} color="#ffd27a" />
      <pointLight position={[-7, -3, 4]} intensity={25} color="#3fc1b0" />
      <group position={[2.2, 1.1, 0]}>
        <Lineage reduced={reduced} />
      </group>
      <Dust />
      <EffectComposer>
        <Bloom intensity={1.25} luminanceThreshold={0.25} luminanceSmoothing={0.3} mipmapBlur />
        <Vignette eskil={false} offset={0.2} darkness={0.85} />
      </EffectComposer>
    </Canvas>
  )
}
