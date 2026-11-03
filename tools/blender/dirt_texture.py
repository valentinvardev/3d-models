"""
Textura de la calle de tierra de Dusty Gulch y el GLB que la sube a Roblox (la única forma de subir una imagen
que hay hoy: opencloud.py sube Models, y el importador crea la imagen de la textura del GLB).

  "%LOCALAPPDATA%\\Programs\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup ^
      --python-exit-code 1 -P tools/blender/dirt_texture.py

Deja en assets/models/western/textures/WST_Tex_StreetDirt/:
  01_design/StreetDirt.png       1024 x 1024, opaca (el alfa de una imagen dentro de un GLB no está garantizado)
  03_export/WST_Tex_StreetDirt.glb  un cuadrado de 28 x 28 con la imagen; se sube con opencloud.py model y el id de
                                 la imagen se lee en Studio (TextureID de la MeshPart), como el resto.

Diseño: un cuadro cubre los 28 de ancho de la calle (U = x de la calle) y 28 de largo (V = a lo largo, z): se
repite sin costura en V. Dos carriles con su par de huellas de rueda (trocha 5,8, la de la carreta) y huellas
de cascos por el medio de cada carril; tierra moteada, piedritas. Colores alrededor del Mud (139,100,66) que
quedó en la calle.
"""

import math
from pathlib import Path

import bpy
import numpy as np

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "assets" / "models" / "western" / "textures" / "WST_Tex_StreetDirt"
N = 1024
STUDS = 28.0
PX = N / STUDS                      # píxeles por stud
rng = np.random.default_rng(7)


def periodic_noise(cells, octaves=4):
    """Ruido de valor que se repite en los dos ejes (cada octava es una grilla periódica interpolada)."""
    out = np.zeros((N, N))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        c = cells * 2 ** o
        grid = rng.random((c, c))
        t = np.arange(N) * c / N
        i0 = np.floor(t).astype(int) % c
        i1 = (i0 + 1) % c
        f = t - np.floor(t)
        f = f * f * (3 - 2 * f)
        rows = grid[i0][:, i0] * (1 - f)[None, :] + grid[i0][:, i1] * f[None, :]
        rows1 = grid[i1][:, i0] * (1 - f)[None, :] + grid[i1][:, i1] * f[None, :]
        out += amp * (rows * (1 - f)[:, None] + rows1 * f[:, None])
        total += amp
        amp *= 0.5
    return out / total


def build_image():
    # filas = V (a lo largo de la calle), columnas = U (a lo ancho)
    v = np.arange(N)[:, None]
    u = np.arange(N)[None, :]
    x = (u + 0.5) / PX - STUDS / 2            # studs desde el centro de la calle
    base = np.array([146, 106, 70], float)
    patches = periodic_noise(3, 3) - 0.5                       # manchones: seco más claro, húmedo más oscuro
    mott = periodic_noise(6) - 0.5
    fine = periodic_noise(48, 2) - 0.5
    img = (base[None, None, :] + patches[..., None] * np.array([46, 36, 26])
           + mott[..., None] * np.array([26, 20, 14]) + fine[..., None] * np.array([16, 13, 10]))

    # huellas de rueda: dos carriles (x = ±6), cada uno con un par a ±2,9; las ruedas van casi derechas
    wob = (np.sin(2 * math.pi * v / N * 2) * 0.07 + np.sin(2 * math.pi * v / N * 5 + 1.3) * 0.03)
    for lane in (-6.0, 6.0):
        for side in (-2.9, 2.9):
            for k, extra in enumerate((0.0, 0.3)):                   # dos pasadas de ruedas, un poco corridas
                cx = lane + side + wob * (1 if k == 0 else -0.6) + extra * np.sign(side)
                d = np.abs(x - cx)
                rut = np.clip(1 - d / 0.45, 0, 1) ** 1.6 * (0.7 if k == 0 else 0.35)
                ridge = np.clip(1 - np.abs(d - 0.55) / 0.2, 0, 1) * (0.25 if k == 0 else 0.1)
                img = img * (1 - rut[..., None] * 0.28) + ridge[..., None] * np.array([18, 14, 10])

    # cascos: medialunas chicas y suaves por el medio de cada carril, giradas al azar y a veces cortadas
    def hoof(cv, cu, angle, strength):
        r = 0.24 * PX
        rr = int(r * 1.6) + 2
        cut = rng.uniform(-0.6, 0.2)                                   # cuánto de la herradura se marcó
        for dv in range(-rr, rr + 1):
            for du in range(-rr, rr + 1):
                a = math.atan2(dv, du) - angle
                dist = math.hypot(dv, du)
                edge = 1 - abs(dist - r) / (0.08 * PX)
                if edge > 0 and math.cos(a) > cut:
                    vv, uu = (cv + dv) % N, cu + du
                    if 0 <= uu < N:
                        img[vv, uu] *= 1 - 0.16 * strength * edge
    for lane in (-6.0, 6.0):
        for i in range(30):
            cv = int(rng.random() * N)
            cu = int((lane + rng.normal(0, 0.9) + STUDS / 2) * PX)
            hoof(cv, cu, math.pi / 2 + rng.normal(0, 0.6), 0.5 + 0.5 * rng.random())

    # piedritas claras y oscuras
    for _ in range(900):
        cv, cu = int(rng.random() * N), int(rng.random() * N)
        rad = rng.choice([1, 1, 2, 2, 3])
        col = np.array([178, 162, 140]) if rng.random() < 0.6 else np.array([96, 82, 68])
        for dv in range(-rad, rad + 1):
            for du in range(-rad, rad + 1):
                if dv * dv + du * du <= rad * rad and 0 <= cu + du < N:
                    img[(cv + dv) % N, cu + du] = col * (0.85 + 0.15 * rng.random())

    # orillas: hacia los bordes de la calle la tierra se aclara (más pisada al medio, polvo a los costados)
    edge = np.clip((np.abs(x) - 11.5) / 2.5, 0, 1)
    img = img * (1 - edge[..., None] * 0.15) + edge[..., None] * np.array([205, 172, 120]) * 0.15
    return np.clip(img, 0, 255)


def main():
    (OUT / "01_design").mkdir(parents=True, exist_ok=True)
    (OUT / "03_export").mkdir(parents=True, exist_ok=True)
    pix = build_image() / 255.0
    rgba = np.concatenate([pix, np.ones((N, N, 1))], axis=2)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    im = bpy.data.images.new("StreetDirt", N, N, alpha=False)
    im.pixels.foreach_set(rgba[::-1].astype(np.float32).ravel())   # las filas de Blender van de abajo arriba
    png = OUT / "01_design" / "StreetDirt.png"
    im.filepath_raw = str(png)
    im.file_format = "PNG"
    im.save()

    # el cuadrado de 28 x 28 (en Blender, Z arriba; el juego lo ve en XZ)
    h = STUDS / 2
    me = bpy.data.meshes.new("StreetDirt")
    me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for li, (a, b) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = (a, b)
    mat = bpy.data.materials.new("StreetDirt")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(png))
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    me.materials.append(mat)
    ob = bpy.data.objects.new("StreetDirt", me)
    bpy.context.scene.collection.objects.link(ob)
    glb = OUT / "03_export" / "WST_Tex_StreetDirt.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=False,
                              export_image_format="AUTO", export_apply=True)
    print("@@JSON@@" + str({"png": str(png.relative_to(REPO)), "glb": str(glb.relative_to(REPO))}))


main()
