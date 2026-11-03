"""
Receta de WST_Pickup_SilverShard, la esquirla de plata viva que cae de cada enemigo (prompt 035, Bloques A + B + G).

Brief
- Moneda: muchas en pantalla a la vez, tiene que ser barata (< 80 triángulos por variante) y leerse a
  40 studs como "cristal de plata con punta que brilla": 2-4 púas angulosas de un mismo pie, inclinadas
  entre sí 10-25°, con la punta de la más alta en neón (el Core asoma por ahí).
- Tres variantes en fila sobre X (0,6 entre centros), cada una con el origen en el centro de su pie:
  Shard_A (3 púas, 0,6 de alto), Shard_B (2 púas gordas, 0,55), Shard_C (4 púas, 0,5, más achaparrada).
  0,35 de ancho.
- Púa: prisma de 5-6 lados irregulares (radios desparejos) con hombro y punta; las chicas, 4-5 lados.
  Pie: un terrón bajo que tapa las raíces. Todo silver_crust; Core en silver_neon, una astilla fina de
  3 lados por el eje de la púa mayor que sale 0,08 por la punta (asoma en el último 20 % de la púa).
- Inferido: los nombres de los núcleos (Shard_A_Core... : tres objetos no pueden llamarse Core), el
  reparto de púas por variante, el terrón del pie.

Vueltas: 1) z-fighting entre la púa mayor y su Core (los dos pies en y = 0,03, girados igual); la punta
de neón asomaba 0,06 y no se leía; A de 0,405 de ancho; C con 86 triángulos · 2) Core más grueso y más
alto, pie de 4 + 2 puntos, segunda púa de C de 4 lados · 3) A más baja (0,60 con la punta) y B más
cerrada (0,346 de ancho).

Revisión
- Triángulos por variante con su Core: A 76, B 62, C 78 (tope 80).
- Medidas (ancho x alto con la punta de neón): A 0,346 x 0,60 · B 0,346 x 0,59 · C 0,359 x 0,54.
- El Core entra en la púa: los avisos de contacto son esperables.
"""

import math

GAP = 0.6


def _rot(p, ax, az):
    """Gira p (alrededor del origen) ax grados sobre X y después az sobre Z (coordenadas del juego)."""
    x, y, z = p
    a = math.radians(ax)
    y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    b = math.radians(az)
    x, y = x * math.cos(b) - y * math.sin(b), x * math.sin(b) + y * math.cos(b)
    return (x, y, z)


def _jit(i, k):
    return ((i * 7919 + k * 104729) % 97) / 97 - 0.5


def spike(base, length, radius, sides, ax, az, seed, shoulder=0.72, twist=0.0, y0=0.03):
    """Puntos de una púa: anillo de abajo (metido en el pie, sobre el piso), hombro y punta, con radios desparejos."""
    pts = []
    for y, r in ((y0, radius), (shoulder * length, radius * 0.92)):
        for i in range(sides):
            a = 2 * math.pi * i / sides + twist + 0.25 * _jit(seed, i)
            rr = r * (1 + 0.3 * _jit(seed + 3, i))
            pts.append((rr * math.cos(a), y, rr * math.sin(a)))
    pts.append((0.0, length, 0.0))
    return [tuple(b + c for b, c in zip(base, _rot(p, ax, az))) for p in pts]


def foot(base, seed):
    """Terrón bajo del pie: 4 puntos abajo, 2 arriba (8 triángulos)."""
    pts = []
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.4 + 0.3 * _jit(seed, i)
        r = 0.14 * (1 + 0.25 * _jit(seed + 1, i))
        pts.append((r * math.cos(a), 0.0, r * math.sin(a)))
    for i in range(2):
        a = math.pi * i + 1.1
        pts.append((0.06 * math.cos(a), 0.09, 0.06 * math.sin(a)))
    return [tuple(b + c for b, c in zip(base, p)) for p in pts]


# (largo, radio, lados, base dx, base dz, giro sobre X, giro sobre Z) — la primera es la mayor (lleva el Core)
VARIANTS = {
    "Shard_A": [(0.53, 0.085, 6, 0.0, 0.0, -6, 7),
                (0.36, 0.068, 5, 0.06, 0.03, 6, -15),
                (0.30, 0.060, 5, -0.06, -0.03, -14, 16)],
    "Shard_B": [(0.52, 0.10, 6, -0.02, 0.0, 4, 8),
                (0.36, 0.08, 6, 0.06, -0.02, -10, -12)],
    "Shard_C": [(0.46, 0.08, 5, 0.0, 0.01, 5, -5),
                (0.33, 0.066, 4, 0.075, -0.02, -12, -18),
                (0.27, 0.055, 4, -0.07, 0.03, 14, 18),
                (0.21, 0.05, 4, -0.02, -0.08, -24, 6)],
}


def build(mk):
    for k, (name, spikes) in enumerate(VARIANTS.items()):
        x0 = (k - 1) * GAP
        part = mk.part(name, (x0, 0, 0))
        mk.hull(part, foot((x0, 0, 0), 11 * k + 1), "silver_crust")
        for i, (ln, r, n, dx, dz, ax, az) in enumerate(spikes):
            mk.hull(part, spike((x0 + dx, 0.0, dz), ln, r, n, ax, az, 31 * k + 7 * i, twist=0.4 * i), "silver_crust")
        ln, r, n, dx, dz, ax, az = spikes[0]
        core = mk.part(f"{name}_Core", (x0, 0, 0))
        mk.hull(core, spike((x0 + dx, 0.0, dz), ln + 0.08, 0.055, 3, ax, az, 0, shoulder=0.7, y0=0.06),
                "silver_neon")                               # el pie más arriba que el de la púa: si no, caras coplanares
