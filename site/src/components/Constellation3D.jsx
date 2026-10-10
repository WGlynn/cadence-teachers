import { useMemo, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html, Billboard } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import * as THREE from 'three'
import { EXPS, TRACKS, VCOLOR, STANDING } from '../data'

/** Layout: one cluster per research track on a ring; experiments spiral out of their cluster in run order. */
function useLayout() {
  return useMemo(() => {
    const R = 6.2, T = TRACKS.length
    const centers = TRACKS.map((t, i) => {
      const a = (i / T) * Math.PI * 2
      return new THREE.Vector3(Math.cos(a) * R, Math.sin(i * 1.7) * 1.1, Math.sin(a) * R)
    })
    const pos = {}, perTrack = {}
    EXPS.forEach((e) => {
      const ti = TRACKS.indexOf(e.track), k = (perTrack[e.track] = (perTrack[e.track] ?? -1) + 1)
      const r = 0.55 * Math.sqrt(k + 0.6), a = k * 2.39996
      pos[e.id] = centers[ti].clone().add(new THREE.Vector3(Math.cos(a) * r, ((k % 3) - 1) * 0.45, Math.sin(a) * r))
    })
    return { centers, pos }
  }, [])
}

function Star({ e, p, dim, hovered, onHover, onPick }) {
  const ref = useRef()
  const color = VCOLOR[e.verdict]
  const standing = STANDING.has(e.verdict)
  const base = e.verdict === 'CROSSED' ? 0.24 : standing ? 0.17 : 0.15
  useFrame((s, dt) => {
    if (!ref.current) return
    const target = hovered ? 1.7 : 1
    const s0 = ref.current.scale.x
    ref.current.scale.setScalar(s0 + (target - s0) * Math.min(1, dt * 10))
    if (e.verdict === 'CROSSED') ref.current.rotation.y += dt * 0.8
  })
  const op = dim ? 0.12 : 1
  return (
    <group position={p}>
      <group ref={ref}
        onPointerOver={(ev) => { ev.stopPropagation(); onHover(e.id); document.body.style.cursor = 'pointer' }}
        onPointerOut={() => { onHover(null); document.body.style.cursor = '' }}
        onClick={(ev) => { ev.stopPropagation(); onPick(e.id) }}>
        {standing ? (
          <mesh>
            <icosahedronGeometry args={[base, e.verdict === 'CROSSED' ? 0 : 2]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={dim ? 0.1 : e.verdict === 'CROSSED' ? 3 : 1.6}
              transparent opacity={op} roughness={0.3} flatShading={e.verdict === 'CROSSED'} />
          </mesh>
        ) : (
          <Billboard>
            <mesh>
              <ringGeometry args={[base * 0.72, base, 32]} />
              <meshBasicMaterial color={color} transparent opacity={dim ? 0.1 : 0.9} side={THREE.DoubleSide} toneMapped={false} />
            </mesh>
            {e.verdict === 'RETRACTED' || e.verdict === 'VOID' ? (
              <mesh rotation={[0, 0, Math.PI / 4]}>
                <planeGeometry args={[base * 2.2, 0.025]} />
                <meshBasicMaterial color={color} transparent opacity={dim ? 0.1 : 0.9} toneMapped={false} />
              </mesh>
            ) : null}
          </Billboard>
        )}
        <mesh visible={false}><sphereGeometry args={[0.38, 8, 8]} /></mesh>
      </group>
      {hovered && (
        <Html zIndexRange={[20, 0]} style={{ pointerEvents: 'none' }}>
          <div className="star-tip"><b style={{ color }}>{e.id}</b>{e.name}</div>
        </Html>
      )}
    </group>
  )
}

function Threads({ pos }) {
  const geo = useMemo(() => {
    const pts = []
    TRACKS.forEach((t) => {
      const ids = EXPS.filter((e) => e.track === t).map((e) => e.id)
      for (let i = 1; i < ids.length; i++) pts.push(pos[ids[i - 1]], pos[ids[i]])
    })
    return new THREE.BufferGeometry().setFromPoints(pts)
  }, [pos])
  return (
    <lineSegments geometry={geo}>
      <lineBasicMaterial color="#3b4560" transparent opacity={0.55} />
    </lineSegments>
  )
}

function Scene({ filter, onPick }) {
  const { centers, pos } = useLayout()
  const [hover, setHover] = useState(null)
  const spin = useRef()
  useFrame((s, dt) => { if (spin.current && !hover) spin.current.rotation.y += dt * 0.04 })
  return (
    <group ref={spin}>
      <Threads pos={pos} />
      {TRACKS.map((t, i) => (
        <Html key={t} position={centers[i].clone().add(new THREE.Vector3(0, 1.9, 0))} center zIndexRange={[10, 0]}>
          <div className="track-label">{t}</div>
        </Html>
      ))}
      {EXPS.map((e) => (
        <Star key={e.id} e={e} p={pos[e.id]} dim={!filter.has(e.verdict)} hovered={hover === e.id} onHover={setHover} onPick={onPick} />
      ))}
    </group>
  )
}

export default function Constellation3D({ filter, onPick, active = true }) {
  return (
    <Canvas frameloop={active ? 'always' : 'never'} dpr={[1, 1.75]} camera={{ position: [0, 6.5, 15], fov: 50 }}>
      <ambientLight intensity={0.4} />
      <pointLight position={[0, 8, 0]} intensity={60} color="#ffe2a8" />
      <Scene filter={filter} onPick={onPick} />
      <OrbitControls enablePan={false} minDistance={7} maxDistance={26} enableDamping dampingFactor={0.08} rotateSpeed={0.6} />
      <EffectComposer>
        <Bloom intensity={1.1} luminanceThreshold={0.3} mipmapBlur />
      </EffectComposer>
    </Canvas>
  )
}
