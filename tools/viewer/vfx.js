// Simulador de efectos para el visor (three.js). Lee los efectos de assets/vfx/western/*.json, escritos con los
// nombres de propiedad de Roblox (ParticleEmitter, PointLight) y los atributos de emisión de roclicks (EmitDelay,
// EmitCount, EmitDuration, Rate). Es una aproximación para revisar timing, forma, color y tamaño: el render final
// es el de Roblox.
//
// Ejes: un efecto se pega a un nodo del modelo (pieza o marcador). Las direcciones del efecto (EmissionDirection,
// ShapeSize, offset) están en los ejes del juego (-Z adelante, +X derecha). En el GLB final (03_export) el modelo
// está girado 180°: ahí el frente del nodo es su +Z local, por eso `flip`.

import * as THREE from 'three';

const DIRS = { Top: [0, 1, 0], Bottom: [0, -1, 0], Front: [0, 0, -1], Back: [0, 0, 1], Right: [1, 0, 0], Left: [-1, 0, 0] };
const MAX_PARTICLES = 900;
const rnd = (r) => (Array.isArray(r) ? r[0] + Math.random() * (r[1] - r[0]) : r || 0);

function seq(keys, t) {                       // NumberSequence: [[t, v], ...] lineal por tramos
  if (!Array.isArray(keys)) return keys ?? 0;
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1], [t1, v1] = keys[i];
      return v0 + (v1 - v0) * ((t - t0) / Math.max(1e-6, t1 - t0));
    }
  }
  return keys[keys.length - 1][1];
}

const tmpA = new THREE.Color(), tmpB = new THREE.Color();
function colorSeq(keys, t, out) {             // ColorSequence: [[t, "#hex"], ...]
  if (!Array.isArray(keys)) return out.set(keys || '#ffffff');
  if (t <= keys[0][0] || keys.length === 1) return out.set(keys[0][1]);
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const u = (t - keys[i - 1][0]) / Math.max(1e-6, keys[i][0] - keys[i - 1][0]);
      return out.copy(tmpA.set(keys[i - 1][1])).lerp(tmpB.set(keys[i][1]), u);
    }
  }
  return out.set(keys[keys.length - 1][1]);
}

export class VFX {
  constructor(scene, camera) {
    this.scene = scene; this.camera = camera;
    this.data = { effects: {}, bindings: [], textures: '/assets/vfx/textures/' };
    this.loader = new THREE.TextureLoader(); this.tex = {};
    this.handles = []; this.particles = [];
    this.flip = true; this.enabled = true;
    this.group = new THREE.Group(); scene.add(this.group);
  }

  setData(vfx) { if (vfx) this.data = vfx; }

  texture(name) {
    if (!this.tex[name]) {
      const t = this.loader.load(this.data.textures + name + '.png');
      t.colorSpace = THREE.SRGBColorSpace;
      this.tex[name] = t;
    }
    return this.tex[name];
  }

  // ejes del juego -> ejes locales del nodo
  local(v) { return this.flip ? new THREE.Vector3(-v[0], v[1], -v[2]) : new THREE.Vector3(v[0], v[1], v[2]); }

  play(name, node, { offset = [0, 0, 0], loop = false } = {}) {
    const spec = this.data.effects[name];
    if (!spec || !node || !this.enabled) return null;
    const h = { spec, node, offset: this.local(offset), loop, t: 0, layers: [], dead: false };
    for (const L of spec.layers) {
      const st = { L, acc: 0, burst: false };
      if (L.class === 'PointLight') {
        st.light = new THREE.PointLight(L.Color || '#ffd27a', 0, (L.Range || 8), 1.5);
        this.group.add(st.light);
      }
      h.layers.push(st);
    }
    this.handles.push(h);
    return h;
  }

  stop(h) { if (h) h.dead = true; }
  clear() {
    for (const h of this.handles) for (const s of h.layers) if (s.light) this.group.remove(s.light);
    this.handles = [];
    for (const p of this.particles) this.group.remove(p.obj);
    this.particles = [];
  }

  emitterFrame(h) {                             // posición y orientación de mundo del punto de emisión
    const q = h.node.getWorldQuaternion(new THREE.Quaternion());
    const p = h.node.getWorldPosition(new THREE.Vector3()).add(h.offset.clone().applyQuaternion(q));
    return { p, q };
  }

  spawn(h, L, frame) {
    if (this.particles.length >= MAX_PARTICLES) return;
    const dir = this.local(DIRS[L.EmissionDirection] || DIRS.Front);
    const sp = (L.SpreadAngle || [0, 0]).map(a => THREE.MathUtils.degToRad(a));
    // dirección dentro del cono: giro al azar en los dos ejes perpendiculares
    const perpA = Math.abs(dir.y) > 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
    const ax1 = new THREE.Vector3().crossVectors(dir, perpA).normalize();
    const ax2 = new THREE.Vector3().crossVectors(dir, ax1).normalize();
    const d = dir.clone()
      .applyAxisAngle(ax1, (Math.random() * 2 - 1) * sp[0])
      .applyAxisAngle(ax2, (Math.random() * 2 - 1) * sp[1])
      .applyQuaternion(frame.q).normalize();
    const ss = L.ShapeSize || [0, 0, 0];
    const off = this.local([(Math.random() - 0.5) * ss[0], (Math.random() - 0.5) * ss[1], (Math.random() - 0.5) * ss[2]]).applyQuaternion(frame.q);
    const additive = (L.LightEmission ?? 0) >= 0.5;
    const mat = (L.Orientation === 'WorldUp')
      ? new THREE.MeshBasicMaterial({ map: this.texture(L.Texture), transparent: true, depthWrite: false, side: THREE.DoubleSide,
          blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending })
      : new THREE.SpriteMaterial({ map: this.texture(L.Texture), transparent: true, depthWrite: false,
          blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending });
    let obj;
    if (L.Orientation === 'WorldUp') { obj = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat); obj.rotation.x = -Math.PI / 2; }
    else obj = new THREE.Sprite(mat);
    obj.renderOrder = additive ? 20 : 10;
    this.group.add(obj);
    this.particles.push({
      L, obj, mat, age: 0, life: Math.max(0.02, rnd(L.Lifetime || [1, 1])),
      pos: frame.p.clone().add(off), vel: d.multiplyScalar(rnd(L.Speed || [0, 0])),
      rot: THREE.MathUtils.degToRad(rnd(L.Rotation || [0, 0])), rotSpeed: THREE.MathUtils.degToRad(rnd(L.RotSpeed || [0, 0])),
      additive, bright: L.Brightness ?? 1, shade: (L.LightInfluence ?? 1) > 0.5 ? 0.85 : 1,
    });
  }

  update(dt) {
    for (const h of this.handles) {
      if (h.dead) continue;
      h.t += dt;
      const frame = this.emitterFrame(h);
      let alive = false;
      for (const s of h.layers) {
        const L = s.L, delay = L.EmitDelay || 0;
        if (L.class === 'PointLight') {
          s.light.position.copy(frame.p);
          const dur = L.EmitDuration || 0, local = h.t - delay;
          let k = 0;
          if (local >= 0) k = dur > 0 ? Math.max(0, 1 - local / dur) : 1;
          s.light.intensity = (L.Brightness || 1) * 2.2 * k;
          if (dur === 0 && h.loop) alive = true;
          else if (local < dur) alive = true;
          continue;
        }
        if (L.EmitCount > 0 && !s.burst && h.t >= delay) {
          s.burst = true;
          for (let i = 0; i < L.EmitCount; i++) this.spawn(h, L, frame);
        }
        if (L.Rate > 0) {
          const dur = L.EmitDuration || 0;
          const on = h.t >= delay && (dur > 0 ? h.t < delay + dur : h.loop);
          if (on) {
            s.acc += L.Rate * dt;
            while (s.acc >= 1) { s.acc -= 1; this.spawn(h, L, frame); }
          }
          if (on || (dur > 0 && h.t < delay + dur)) alive = true;
        }
        if (L.EmitCount > 0 && !s.burst) alive = true;
      }
      if (!alive && !h.loop) h.dead = true;
    }
    // las partículas siguen vivas aunque su efecto haya terminado
    const cam = this.camera;
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i], L = p.L;
      p.age += dt;
      if (p.age >= p.life) { this.group.remove(p.obj); p.mat.dispose(); this.particles.splice(i, 1); continue; }
      const u = p.age / p.life;
      const acc = L.Acceleration || [0, 0, 0];
      p.vel.x += acc[0] * dt; p.vel.y += acc[1] * dt; p.vel.z += acc[2] * dt;
      if (L.Drag) p.vel.multiplyScalar(Math.exp(-L.Drag * dt));
      p.pos.addScaledVector(p.vel, dt);
      p.rot += p.rotSpeed * dt;
      const size = Math.max(0.001, seq(L.Size || [[0, 1], [1, 1]], u));
      p.obj.position.copy(p.pos);
      if (L.Orientation === 'WorldUp') p.obj.scale.set(size, size, 1);
      else if (L.Orientation === 'VelocityParallel' && p.vel.lengthSq() > 1e-6) {
        // la textura se estira y se alinea con la velocidad vista en pantalla
        const a = p.pos.clone().project(cam), b = p.pos.clone().addScaledVector(p.vel, 0.02).project(cam);
        p.mat.rotation = Math.atan2(b.y - a.y, b.x - a.x) - Math.PI / 2;
        p.obj.scale.set(size, size * 1.8, 1);
      } else { p.mat.rotation = p.rot; p.obj.scale.set(size, size, 1); }
      colorSeq(L.Color || '#ffffff', u, p.mat.color);
      p.mat.color.multiplyScalar(p.additive ? Math.min(2.5, p.bright) : p.shade);
      p.mat.opacity = Math.max(0, 1 - seq(L.Transparency || [[0, 0], [1, 1]], u));
    }
    for (const h of this.handles) if (h.dead) for (const s of h.layers) if (s.light) this.group.remove(s.light);
    this.handles = this.handles.filter(h => !h.dead);
  }
}
