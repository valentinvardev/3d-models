--[[
	Arma el .rbxm de un objeto que se sostiene (arma o consumible) con el contrato de D024, para el juego.

	  lune run tools/roblox/held_build.luau <objeto.rig.json> <held.rig.json> <Nombre> <salida.rbxm>

	- objeto.rig.json: 04_roblox/<Id>.rig.json del objeto (rig_data.py glb + ids), en coordenadas del objeto.
	- held.rig.json: assets/animation/western/held/<Id corto>.rig.json (held.py). De ahí salen la raíz, el agarre
	  ("grip", en coordenadas del objeto) y de quién cuelga cada pieza ("tree"). Solo entran las piezas que nombra
	  el tree: la dinamita en la mano es Stick, no Bundle.
	- Nombre: el id de la ficha (Revolver, HanksWidow, Bandages…).

	Contrato (tools/roblox/README.md, "Objetos en la mano"):
	  Model con PrimaryPart = la raíz (Body, o Stock/Handle/Coil/Bottle/Stick según el objeto), que lleva un
	  Attachment "_Grip" en el punto de agarre. Al equipar, el juego crea un Motor6D RightHand -> raíz con
	  C0 = CFrame.new(RightGripAttachment.Position) y C1 = CFrame.new(_Grip.Position).
	  Cada pieza que no es la raíz cuelga de la raíz por un Motor6D con su nombre (Part0 = raíz, Part1 = la pieza,
	  C0 y C1 en el origen de la pieza, alineados a los ejes): así los clips Hold/Equip/Inspect/Fire/Reload la mueven.
	  Los marcadores (_Muzzle, _Eject, _Chamber, _Grip2…) son Attachments en la pieza que los contiene.
	  Sin colisión, sin consultas de rayos, sin masa y sin scripts: el arma no tiene que frenar al jugador ni tapar
	  los disparos.
]]

local fs = require("@lune/fs")
local process = require("@lune/process")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")

local Instance, CFrame, Vector3, Enum = roblox.Instance, roblox.CFrame, roblox.Vector3, roblox.Enum

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

if #process.args < 4 then
	print(
		"uso: lune run tools/roblox/held_build.luau <objeto.rig.json> <held.rig.json> <Nombre> <salida.rbxm>"
	)
	process.exit(1)
end

local item = serde.decode("json", fs.readFile(process.args[1]))
local held = serde.decode("json", fs.readFile(process.args[2]))
local name, out = process.args[3], process.args[4]

local nodes = {}
for _, n in ipairs(item.nodes) do
	nodes[n.name] = n
end

local root = held.root
local model = Instance.new("Model")
model.Name = name
local parts, missing = {}, {}

for piece, parent in pairs(held.tree) do
	if
		piece:sub(1, 1) ~= "_"
		and (parent == "RightHand" or held.tree[parent] ~= nil or parent == root)
	then
		local n = nodes[piece]
		assert(n, `{name}: la pieza {piece} del tree no está en {process.args[1]}`)
		local p
		if n.mesh then
			p = Instance.new("MeshPart")
			p.MeshContent = roblox.Content.fromUri(n.mesh)
			if n.texture then
				p.TextureContent = roblox.Content.fromUri(n.texture)
			end
			p.InitialSize = v3(n.meshSize or n.size)
			p.CollisionFidelity = Enum.CollisionFidelity.Box
		else
			p = Instance.new("Part")
			table.insert(missing, piece)
		end
		p.Name = piece
		p.Size = v3(n.size)
		p.CFrame = CFrame.new(table.unpack(n.cframe))
		p.Material = Enum.Material[n.material or "SmoothPlastic"]
		p.Color = roblox.Color3.new(1, 1, 1)
		p.Anchored = false
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Massless = true
		p.Parent = model
		parts[piece] = p
	end
end
assert(parts[root], `{name}: falta la raíz {root}`)
model.PrimaryPart = parts[root]

local report = {}
local motors = 0
for piece, p in pairs(parts) do
	if piece ~= root then
		local parent = parts[held.tree[piece]] or parts[root]
		local at = CFrame.new(v3(nodes[piece].origin))
		local m = Instance.new("Motor6D")
		m.Name = piece
		m.Part0, m.Part1 = parent, p
		m.C0, m.C1 = parent.CFrame:Inverse() * at, p.CFrame:Inverse() * at
		m.Parent = p
		motors += 1
	end
end

-- el agarre siempre en la raíz (en el revólver el marcador está en la pieza Grip: se pasa a la raíz)
local grip = Instance.new("Attachment")
grip.Name = "_Grip"
grip.CFrame = parts[root].CFrame:Inverse() * CFrame.new(v3(held.grip))
grip.Parent = parts[root]

local marks = {}
for marker, parent in pairs(held.tree) do
	if marker:sub(1, 1) == "_" and marker ~= "_Grip" then
		local n = nodes[marker]
		local host = parts[parent] or parts[root]
		if n then
			local a = Instance.new("Attachment")
			a.Name = marker
			a.CFrame = host.CFrame:Inverse() * CFrame.new(n.cframe[1], n.cframe[2], n.cframe[3])
			a.Parent = host
			table.insert(marks, `{marker}@{host.Name}`)
		end
	end
end
table.sort(marks)

local dir = out:match("^(.*)/[^/]+$")
if dir and not fs.isDir(dir) then
	fs.writeDir(dir)
end
fs.writeFile(out, roblox.serializeModel({ model }))
print(`{name}: raíz {root} · {motors} Motor6D · marcadores {table.concat(marks, ", ")} -> {out}`)
if #missing > 0 then
	print(`  sin malla (falta leer los ids en Studio): {table.concat(missing, ", ")}`)
end
