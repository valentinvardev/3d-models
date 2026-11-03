--[[
	Arma el .rbxm de un modelo estático (prop, pieza del pueblo, moneda) para el juego.

	  lune run tools/roblox/prop_build.luau <layout.json> <salida.rbxm>

	El layout ya trae cada pieza resuelta (lo escribe tools/roblox/town.py, o se escribe a mano para un prop
	suelto): no se calcula nada acá.

	  {
	    "name": "Store",
	    "single": false,                  -- true: el rbxm es la MeshPart sola (la moneda), sin Model ni Root
	    "parts": [
	      { "name": "Front_Wall_Plain_frag01", "mesh": "rbxassetid://…", "texture": "rbxassetid://…",
	        "meshSize": [x, y, z], "size": [x, y, z], "cframe": [12 números], "material": "SmoothPlastic" },
	      { "name": "SignBand_Text", "block": true, "size": [x, y, z], "cframe": [12 números],
	        "color": [r, g, b], "transparency": 1,
	        "sign": { "faces": ["Front"], "text": "GENERAL STORE", "font": "Antique", "color": [r, g, b] } }
	    ]
	  }

	"block": una Part lisa, sin malla (el fondo oscuro detrás de una ventana, la tapa invisible de un cartel).
	"surface": { "texture": "rbxassetid://…", "face": "Top", "tileU": 28, "tileV": 28 } pone una Texture que se
	repite sobre esa cara (la calle de tierra).
	"weldTo": "<nombre>" suelda la pieza a esa otra y no a Root (las tablas de una hoja de puerta, a la hoja).
	"sign": un SurfaceGui con el texto en cada cara de "faces" (el cartel colgado se lee de los dos lados).
	Los demás campos del layout ("src", "box", "at", "front") son para town.py y la captura de Blender.

	Contrato con el juego (acordado con la sesión del juego el 2026-10-29):
	  - Model con PrimaryPart = "Root", una Part invisible en el origen. El origen es el centro de la caja de la
	    pieza del mapa y el modelo ya viene orientado: el juego hace PivotTo(pieza.CFrame) y suelda Root a la pieza.
	  - Cada MeshPart cuelga de Root por un Weld "Fit" (C0 = su lugar respecto de Root): si la pieza del mapa se
	    rompe o se cae, el modelo se va con ella.
	  - Solo visual: sin colisión, sin consultas de rayos, sin toques, sin masa y sin scripts. La colisión y los
	    rayos los da la pieza del mapa, que el juego deja transparente.
	  - Los carteles llevan el texto en un SurfaceGui (sin subir imágenes); el texto queda también en el atributo
	    "Text" de la pieza, por si el juego lo quiere traducir.
]]

local fs = require("@lune/fs")
local process = require("@lune/process")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")

local Instance, CFrame, Vector3, Enum = roblox.Instance, roblox.CFrame, roblox.Vector3, roblox.Enum

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

if #process.args < 2 then
	print("uso: lune run tools/roblox/prop_build.luau <layout.json> <salida.rbxm>")
	process.exit(1)
end

local layout = serde.decode("json", fs.readFile(process.args[1]))
local out = process.args[2]

local function visualOnly(p)
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
	p.CastShadow = true
end

-- Un SurfaceGui por cara ("faces": el cartel colgado se lee de los dos lados).
local function addSign(p, s)
	for _, face in ipairs(s.faces or { "Front" }) do
		local gui = Instance.new("SurfaceGui")
		gui.Name = "Sign" .. face
		gui.Face = Enum.NormalId[face]
		gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		gui.PixelsPerStud = s.pixelsPerStud or 40
		gui.LightInfluence = 1
		local label = Instance.new("TextLabel")
		label.Name = "Text"
		label.BackgroundTransparency = 1
		label.Size = roblox.UDim2.new(1, 0, 1, 0)
		label.Text = s.text
		label.TextScaled = true
		label.FontFace = roblox.Font.fromEnum(Enum.Font[s.font or "Antique"])
		local c = s.color or { 40, 28, 20 }
		label.TextColor3 = roblox.Color3.fromRGB(c[1], c[2], c[3])
		label.Parent = gui
		gui.Parent = p
	end
	p:SetAttribute("Text", s.text)
end

local missing = {}
local function meshPart(n)
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
		p = Instance.new("Part") -- "block": el fondo oscuro de un hueco o la tapa invisible de un cartel
		if not n.block then
			table.insert(missing, n.name)
		end
	end
	p.Name = n.name
	p.Size = v3(n.size)
	p.Material = Enum.Material[n.material or "SmoothPlastic"]
	p.Color = roblox.Color3.fromRGB(table.unpack(n.color or { 255, 255, 255 }))
	p.Transparency = n.transparency or 0
	visualOnly(p)
	if n.transparency == 1 then
		p.CastShadow = false
	end
	if n.sign then
		addSign(p, n.sign)
	end
	if n.surface then -- una Texture que se repite sobre una cara (la tierra de la calle)
		local t = Instance.new("Texture")
		t.Name = n.surface.name or "Surface"
		t.Face = Enum.NormalId[n.surface.face or "Top"]
		t.Texture = n.surface.texture -- ColorMapContent: Lune lo escribe pero no lo sabe leer de vuelta
		t.StudsPerTileU = n.surface.tileU
		t.StudsPerTileV = n.surface.tileV
		t.Parent = p
	end
	return p
end

local result
if layout.single then
	assert(#layout.parts == 1, "single: el layout tiene que traer una sola pieza")
	result = meshPart(layout.parts[1])
	result.CFrame = CFrame.new()
	result.Anchored = true
else
	result = Instance.new("Model")
	result.Name = layout.name
	local root = Instance.new("Part")
	root.Name = "Root"
	root.Size = Vector3.new(1, 1, 1)
	root.Transparency = 1
	root.CFrame = CFrame.new()
	root.Anchored = false
	visualOnly(root)
	root.CastShadow = false
	root.Parent = result
	result.PrimaryPart = root
	local byName, made = {}, {}
	for i, n in ipairs(layout.parts) do
		local p = meshPart(n)
		p.CFrame = CFrame.new(table.unpack(n.cframe))
		p.Anchored = false
		p.Parent = result
		made[i] = p
		byName[n.name] = byName[n.name] or p
	end
	-- cada pieza cuelga de Root; con "weldTo", de otra pieza (las tablas de una hoja de puerta, de la hoja que
	-- tiene la bisagra: el juego mueve esa y el resto la sigue)
	for i, n in ipairs(layout.parts) do
		local p = made[i]
		local host = n.weldTo and assert(byName[n.weldTo], n.name .. ": weldTo sin pieza " .. n.weldTo) or root
		local w = Instance.new("Weld")
		w.Name = "Fit"
		w.Part0 = host
		w.Part1 = p
		w.C0 = host.CFrame:Inverse() * p.CFrame
		w.C1 = CFrame.new()
		w.Parent = p
	end
end

local dir = out:match("^(.*)/[^/]+$")
if dir and not fs.isDir(dir) then
	fs.writeDir(dir)
end
fs.writeFile(out, roblox.serializeModel({ result }))
print(`{layout.name}: {#layout.parts} piezas -> {out}`)
if #missing > 0 then
	print(`  sin malla (falta leer los ids en Studio): {table.concat(missing, ", ")}`)
end
