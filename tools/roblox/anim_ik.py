"""
Copiado del agente de animación de enemigos (2026-10-28).
IK de piernas con la convención de tools/roblox/anim_r15.luau (solo cálculo; no escribe nada del repo).

leg(rig, root, side, ankle, foot_pitch=0, foot_roll=None)
  root = {"pos": [dx, dy, dz], "pitch", "lean", "turn"} (como en el spec)
  side = "Left" | "Right"
  ankle = (x, y, z) del tobillo en el marco del personaje (piso y=0, -Z adelante); x=None = la del rig
  foot_pitch = ángulo absoluto del pie (+ = punta arriba)
  -> {"Hip": {"swing", "spread"}, "Knee": {"swing"}, "Ankle": {"swing"}}
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/roblox
import anim_preview as ap  # noqa: E402


def qaxis(axis, deg):
    a = math.radians(deg) / 2
    s = math.sin(a)
    return (math.cos(a), axis[0] * s, axis[1] * s, axis[2] * s)


def up_local(sem):
    """Root/Waist/Neck: CFrame(pos) * Ry(turn) * Rz(lean) * Rx(-pitch)"""
    q = ap.qmul(ap.qmul(qaxis((0, 1, 0), sem.get("turn", 0)), qaxis((0, 0, 1), sem.get("lean", 0))), qaxis((1, 0, 0), -sem.get("pitch", 0)))
    return q, tuple(sem.get("pos", [0, 0, 0]))


def limb_local(sem, side):
    s = 1 if side == "Right" else -1
    q = ap.qmul(ap.qmul(qaxis((0, 1, 0), sem.get("twist", 0)), qaxis((0, 0, 1), sem.get("spread", 0) * s)), qaxis((1, 0, 0), sem.get("swing", 0)))
    return q, tuple(sem.get("pos", [0, 0, 0]))


def origins(rig):
    return {n["name"]: tuple(n["origin"]) for n in rig["nodes"]}


def chain(rig, root, side, hip, knee, ankle_sw=0.0):
    o = origins(rig)
    lt = ap.compose((ap.IDENT[0], o["LowerTorso"]), up_local(root))
    off = lambda a, b: tuple(x - y for x, y in zip(o[a], o[b]))
    ul = ap.compose(ap.compose(lt, (ap.IDENT[0], off(side + "UpperLeg", "LowerTorso"))), limb_local(hip, side))
    ll = ap.compose(ap.compose(ul, (ap.IDENT[0], off(side + "LowerLeg", side + "UpperLeg"))), limb_local(knee, side))
    ft = ap.compose(ap.compose(ll, (ap.IDENT[0], off(side + "Foot", side + "LowerLeg"))), limb_local({"swing": ankle_sw}, side))
    return lt, ul, ll, ft


def solve(f, x0, target, iters=60):
    x = list(x0)
    for _ in range(iters):
        y = f(x)
        e = [t - v for t, v in zip(target, y)]
        if max(abs(v) for v in e) < 1e-5:
            break
        J = []
        for j in range(len(x)):
            xp = list(x)
            xp[j] += 1e-3
            yp = f(xp)
            J.append([(a - b) / 1e-3 for a, b in zip(yp, y)])
        # mínimos cuadrados: (J^T J) dx = J^T e, con J como lista de columnas
        n = len(x)
        A = [[sum(J[i][k] * J[j][k] for k in range(len(y))) + (1e-6 if i == j else 0) for j in range(n)] for i in range(n)]
        b = [sum(J[i][k] * e[k] for k in range(len(y))) for i in range(n)]
        # Gauss
        M = [row[:] + [bb] for row, bb in zip(A, b)]
        for c in range(n):
            p = max(range(c, n), key=lambda r: abs(M[r][c]))
            M[c], M[p] = M[p], M[c]
            for r in range(n):
                if r != c:
                    k = M[r][c] / M[c][c]
                    M[r] = [a - k * bb for a, bb in zip(M[r], M[c])]
        dx = [M[i][n] / M[i][i] for i in range(n)]
        lim = 20.0
        x = [xi + max(-lim, min(lim, d)) for xi, d in zip(x, dx)]
    return x


def leg(rig, root, side, ankle, foot_pitch=0.0, knee_guess=-30.0, twist=0.0):
    o = origins(rig)
    ax = ankle[0] if ankle[0] is not None else o[side + "Foot"][0]
    tgt = (ax, ankle[1], ankle[2])

    def f(x):
        _, _, _, ft = chain(rig, root, side, {"swing": x[0], "spread": x[1], "twist": twist}, {"swing": x[2]})
        return ft[1]

    x = solve(f, [10.0, 0.0, knee_guess], tgt)
    if x[2] > 0:  # rodilla al revés: probar del otro lado
        x = solve(f, [x[0] + 20, x[1], -abs(x[2]) - 20], tgt)

    def g(a):
        _, _, _, ft = chain(rig, root, side, {"swing": x[0], "spread": x[1], "twist": twist}, {"swing": x[2]}, a[0])
        fwd = ap.qrot(ft[0], (0, 0, -1))
        return [math.degrees(math.atan2(fwd[1], -fwd[2]))]

    _, _, ll, _ = chain(rig, root, side, {"swing": x[0], "spread": x[1], "twist": twist}, {"swing": x[2]})
    down = ap.qrot(ll[0], (0, -1, 0))
    shin = math.degrees(math.atan2(-down[2], -down[1]))  # + = la canilla va adelante
    a = solve(g, [foot_pitch - shin], [foot_pitch])
    hip = {"swing": round(x[0], 1), "spread": round(x[1], 1)}
    if twist:
        hip["twist"] = round(twist, 1)
    return {"Hip": hip, "Knee": {"swing": round(x[2], 1)}, "Ankle": {"swing": round(a[0], 1)}}


def ankle_of(rig, root, side, hip, knee, ankle_sw=0.0):
    return chain(rig, root, side, hip, knee, ankle_sw)[3][1]


def hip_world(rig, root, side):
    lt = chain(rig, root, side, {}, {})[0]
    o = origins(rig)
    off = tuple(x - y for x, y in zip(o[side + "UpperLeg"], o["LowerTorso"]))
    return ap.compose(lt, (ap.IDENT[0], off))[1]


def arm_chain(rig, joints, side):
    """(UpperTorso, UpperArm, LowerArm, Hand) en el marco del personaje, con Root y Waist de joints."""
    o = origins(rig)
    off = lambda a, b: tuple(x - y for x, y in zip(o[a], o[b]))
    lt = ap.compose((ap.IDENT[0], o["LowerTorso"]), up_local(joints.get("Root", {})))
    ut = ap.compose(ap.compose(lt, (ap.IDENT[0], off("UpperTorso", "LowerTorso"))), up_local(joints.get("Waist", {})))
    ua = ap.compose(ap.compose(ut, (ap.IDENT[0], off(side + "UpperArm", "UpperTorso"))), limb_local(joints.get(side + "Shoulder", {}), side))
    la = ap.compose(ap.compose(ua, (ap.IDENT[0], off(side + "LowerArm", side + "UpperArm"))), limb_local(joints.get(side + "Elbow", {}), side))
    hd = ap.compose(ap.compose(la, (ap.IDENT[0], off(side + "Hand", side + "LowerArm"))), limb_local(joints.get(side + "Wrist", {}), side))
    return ut, ua, la, hd


def barrel(rig, joints):
    hd = arm_chain(rig, joints, "Right")[3]
    d = ap.qrot(hd[0], (0, 0, -1))
    return math.degrees(math.atan2(d[1], math.hypot(d[0], d[2]))), math.degrees(math.atan2(d[0], -d[2]))


def grip_point(rig, joints, local_from_hand):
    hd = arm_chain(rig, joints, "Right")[3]
    return tuple(a + b for a, b in zip(hd[1], ap.qrot(hd[0], local_from_hand)))


def aim(rig, joints, pitch, yaw):
    """Resuelve RightShoulder.twist y RightWrist.swing para que el caño (-Z de la mano) quede en (pitch, yaw)."""
    import copy
    j = copy.deepcopy(joints)
    turn = j.get("Root", {}).get("turn", 0) + j.get("Waist", {}).get("turn", 0)
    tilt = j.get("Root", {}).get("pitch", 0) + j.get("Waist", {}).get("pitch", 0)
    sw = j.get("RightShoulder", {}).get("swing", 0) + j.get("RightElbow", {}).get("swing", 0)
    j.setdefault("RightShoulder", {})["twist"] = -turn + yaw * -1
    j.setdefault("RightWrist", {})["swing"] = pitch - sw + tilt

    def f(x):
        j["RightShoulder"]["twist"], j["RightWrist"]["swing"] = x
        return list(barrel(rig, j))

    x = solve(f, [j["RightShoulder"]["twist"], j["RightWrist"]["swing"]], [pitch, yaw])
    return round(x[0], 1), round(x[1], 1)


def reach(rig, joints, side, target, hand_local=(0, -0.25, 0), guess=(60, 0, 60)):
    """Resuelve <side>Shoulder swing/twist y Elbow swing para llevar un punto de la mano a target."""
    import copy
    j = copy.deepcopy(joints)
    sh = j.setdefault(side + "Shoulder", {})
    el = j.setdefault(side + "Elbow", {})

    def f(x):
        sh["swing"], sh["twist"], el["swing"] = x
        hd = arm_chain(rig, j, side)[3]
        return [a + b for a, b in zip(hd[1], ap.qrot(hd[0], hand_local))]

    x = solve(f, list(guess), list(target))
    return round(x[0], 1), round(x[1], 1), round(x[2], 1)


JOINT_OF = {part: link[1] for part, link in ap.R15.items()}


def fk_world(rig, joints):
    """Mundo de cada pieza (q, p) para una pose semántica suelta (sin pasar por anim_build)."""
    o = origins(rig)
    world = {}
    for part in ap.ORDER:
        parent, joint = ap.R15[part]
        sem = joints.get(joint, {})
        if joint in ("Root", "Waist", "Neck"):
            local = up_local(sem)
        else:
            local = limb_local(sem, "Right" if joint.startswith("Right") else "Left")
        if parent == "HumanoidRootPart":
            base = (ap.IDENT[0], o[part])
        else:
            base = ap.compose(world[parent], (ap.IDENT[0], tuple(a - b for a, b in zip(o[part], o[parent]))))
        world[part] = ap.compose(base, local)
    for name, host in ap.hosts(rig).items():
        world[name] = ap.compose(world[host], (ap.IDENT[0], tuple(a - b for a, b in zip(o[name], o[host]))))
    return world


def lows(rig, joints, n=6):
    w = fk_world(rig, joints)
    out = []
    for nd in rig["nodes"]:
        q, p = w[nd["name"]]
        c = tuple(a - b for a, b in zip(nd["cframe"][:3], nd["origin"]))
        h = [s / 2 for s in nd["size"]]
        lo = min(p[1] + ap.qrot(q, (c[0] + sx * h[0], c[1] + sy * h[1], c[2] + sz * h[2]))[1]
                 for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1))
        out.append((round(lo, 3), nd["name"]))
    return sorted(out)[:n]
