--[[
	Arma el .rbxm de un overlay de plata (o de piezas sueltas) para el juego.

	  lune run tools/roblox/overlay_build.luau <piezas.rig.json> <Nombre> <salida.rbxm> [<cuerpo.rig.json>]

	Con cuerpo (overlay: SilverEyes, SilverVeins, SilverCrust, hechos sobre el caminante A):
	  Cada pieza es una MeshPart con el nombre de la parte del cuerpo que cubre (Silver_LeftLowerArm -> LeftLowerArm,
	  Silver_Head_Crust -> Head, Silver_Eyes -> Eyes; si el nombre no da una parte, la de caja más cercana). El
	  nombre original queda en el atributo "Piece". Adentro lleva un Weld "Fit" con Part1 = la pieza, Part0 vacío
	  y C0 = la posición de la pieza respecto de esa parte en el cuerpo de referencia: el juego pone
	  Fit.Part0 = enemigo[pieza.Name] y la pieza queda en su lugar. Dos piezas pueden cubrir la misma parte (en
	  SilverEyes, los ojos y las lágrimas): se recorren los hijos, no se busca por nombre.
	  Sin colisión, sin rayos (el headshot sigue dando en la Head real) y sin masa.
	Sin cuerpo (las balas de la recarga: Rounds): las MeshParts con su nombre, cada una centrada en el origen.
]]

local fs = require("@lune/fs")
local process = require("@lune/process")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")

local Instance, CFrame, Vector3, Enum = roblox.Instance, roblox.CFrame, roblox.Vector3, roblox.Enum

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

if #process.args < 3 then
	print(
		"uso: lune run tools/roblox/overlay_build.luau <piezas.rig.json> <Nombre> <salida.rbxm> [<cuerpo.rig.json>]"
	)
	process.exit(1)
end

local data = serde.decode("json", fs.readFile(process.args[1]))
local name, out = process.args[2], process.args[3]
local body = process.args[4] and serde.decode("json", fs.readFile(process.args[4]))

local ref = {}
if body then
	for _, n in ipairs(body.nodes) do
		if n.name:sub(1, 1) ~= "_" then
			ref[n.name] = n
		end
	end
end

local function boxDist(n, at)
	local d = 0
	for i = 1, 3 do
		d += math.max(math.abs(at[i] - n.cframe[i]) - n.size[i] / 2, 0) ^ 2
	end
	return math.sqrt(d)
end

local function covered(piece, n)
	local guess = piece:gsub("^Silver_", ""):gsub("_Crust$", "")
	if ref[guess] then
		return guess
	end
	local best, dist = nil, math.huge
	for partName, r in pairs(ref) do
		local d = boxDist(r, n.cframe) + (r.cframe[1] - n.cframe[1]) ^ 2 * 1e-3
		if d < dist then
			best, dist = partName, d
		end
	end
	return best
end

local model = Instance.new("Model")
model.Name = name
local report, missing = {}, {}
for _, n in ipairs(data.nodes) do
	if n.name:sub(1, 1) ~= "_" then
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
			table.insert(missing, n.name)
		end
		p.Size = v3(n.size)
		p.Material = Enum.Material[n.material or "SmoothPlastic"]
		p.Color = roblox.Color3.new(1, 1, 1)
		p.Anchored = false
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Massless = true
		local cf = CFrame.new(table.unpack(n.cframe))
		if body then
			local target = covered(n.name, n)
			p.Name = target
			p:SetAttribute("Piece", n.name)
			p.CFrame = cf
			local w = Instance.new("Weld")
			w.Name = "Fit"
			w.Part1 = p
			w.C0 = CFrame.new(table.unpack(ref[target].cframe)):Inverse() * cf
			w.C1 = CFrame.new()
			w.Parent = p
			table.insert(report, `{n.name} -> {target}`)
		else
			p.Name = n.name
			p.CFrame = CFrame.new() -- las balas no traen rotación: centradas en el origen
			table.insert(report, n.name)
		end
		p.Parent = model
	end
end

local dir = out:match("^(.*)/[^/]+$")
if dir and not fs.isDir(dir) then
	fs.writeDir(dir)
end
fs.writeFile(out, roblox.serializeModel({ model }))
print(`{name}: {table.concat(report, ", ")} -> {out}`)
if #missing > 0 then
	print(`  sin malla (falta leer los ids en Studio): {table.concat(missing, ", ")}`)
end
