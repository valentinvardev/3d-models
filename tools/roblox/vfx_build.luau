--[[
	Arma en Roblox los efectos del Western a partir de sus JSON (D025): un .rbxm con una carpeta "VFX" que tiene un
	Attachment por efecto, con sus ParticleEmitter y PointLight adentro y los atributos de emisión de roclicks
	(EmitDelay, EmitCount, EmitDuration; EffectDuration en el efecto). El módulo Emit de
	vendor/skills/roclicks-skills/roblox-vfx/templates/Emit.luau los reproduce tal cual (VFX.play(efecto, cframe)).

	  lune run tools/roblox/vfx_build.luau [assets/vfx/rbx/WesternVFX.rbxm]

	Lee assets/vfx/western/*.json y los ids de las texturas de assets/vfx/textures/_ids.json ({ "flame": "rbxassetid://…" }).
	Una textura sin id queda vacía con el atributo TextureName (se completa después de subirlas) y se avisa.

	Diferencias con el visor (tools/viewer/vfx.js):
	- Orientation "WorldUp" (anillo plano en el piso) no existe en Roblox: va como VelocityPerpendicular con la
	  emisión hacia arriba y una velocidad mínima, que deja la partícula horizontal.
	- ShapeSize: un emisor dentro de un Attachment sale de un punto; el volumen queda en el atributo ShapeSize
	  para quien lo monte sobre una parte.
	- Las direcciones del JSON están en los ejes del juego, que son los del Attachment (Front = su LookVector).
]]

local fs = require("@lune/fs")
local process = require("@lune/process")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")

local Instance, Enum = roblox.Instance, roblox.Enum
local NumberRange, NumberSequence, NumberSequenceKeypoint =
	roblox.NumberRange, roblox.NumberSequence, roblox.NumberSequenceKeypoint
local ColorSequence, ColorSequenceKeypoint, Color3 =
	roblox.ColorSequence, roblox.ColorSequenceKeypoint, roblox.Color3
local Vector2, Vector3 = roblox.Vector2, roblox.Vector3

local SRC = "assets/vfx/western"
local IDS = "assets/vfx/textures/_ids.json"
local OUT = process.args[1] or "assets/vfx/rbx/WesternVFX.rbxm"

local function range(v, default)
	if type(v) == "table" then
		return NumberRange.new(v[1], v[2])
	end
	return NumberRange.new(v or default or 0)
end

local function numSeq(keys, default)
	if type(keys) ~= "table" then
		return NumberSequence.new(keys or default or 0)
	end
	local kps = {}
	for i, k in ipairs(keys) do
		local t = k[1]
		if i == 1 then -- Roblox pide que la secuencia empiece en 0 y termine en 1
			t = 0
		elseif i == #keys then
			t = 1
		end
		table.insert(kps, NumberSequenceKeypoint.new(t, k[2], k[3] or 0))
	end
	if #kps == 1 then
		table.insert(kps, NumberSequenceKeypoint.new(1, keys[1][2]))
	end
	return NumberSequence.new(kps)
end

local function colSeq(keys)
	if type(keys) ~= "table" then
		return ColorSequence.new(Color3.fromHex(keys or "#FFFFFF"))
	end
	local kps = {}
	for i, k in ipairs(keys) do
		local t = (i == 1 and 0) or (i == #keys and 1) or k[1]
		table.insert(kps, ColorSequenceKeypoint.new(t, Color3.fromHex(k[2])))
	end
	if #kps == 1 then
		table.insert(kps, ColorSequenceKeypoint.new(1, Color3.fromHex(keys[1][2])))
	end
	return ColorSequence.new(kps)
end

local ids = {}
if fs.isFile(IDS) then
	ids = serde.decode("json", fs.readFile(IDS))
end

local root = Instance.new("Folder")
root.Name = "VFX"
local missing, count = {}, 0

local names = {}
for _, f in ipairs(fs.readDir(SRC)) do
	if f:match("%.json$") and f:sub(1, 1) ~= "_" then
		table.insert(names, f)
	end
end
table.sort(names)

for _, file in ipairs(names) do
	local spec = serde.decode("json", fs.readFile(`{SRC}/{file}`))
	local fx = Instance.new("Attachment")
	fx.Name = spec.name
	if spec.EffectDuration then
		fx:SetAttribute("EffectDuration", spec.EffectDuration)
	end
	for _, L in ipairs(spec.layers) do
		local inst
		if L.class == "PointLight" then
			inst = Instance.new("PointLight")
			inst.Brightness = L.Brightness or 1
			inst.Range = L.Range or 8
			inst.Color = Color3.fromHex(L.Color or "#FFD27A")
			inst.Shadows = false
			inst.Enabled = (L.EmitDuration or 0) == 0 -- las que no se apagan quedan prendidas (loop)
		else
			inst = Instance.new("ParticleEmitter")
			local tex = ids[L.Texture]
			if tex then
				inst.Texture = tex
			else
				missing[L.Texture] = true
			end
			inst:SetAttribute("TextureName", L.Texture)
			inst.Lifetime = range(L.Lifetime, 1)
			inst.Speed = range(L.Speed, 0)
			inst.SpreadAngle =
				Vector2.new((L.SpreadAngle or { 0, 0 })[1], (L.SpreadAngle or { 0, 0 })[2])
			inst.EmissionDirection = Enum.NormalId[L.EmissionDirection or "Front"]
			local orient = L.Orientation or "FacingCamera"
			if orient == "WorldUp" then
				orient = "VelocityPerpendicular"
				inst.EmissionDirection = Enum.NormalId.Top
				inst.Speed = NumberRange.new(0.01)
			end
			inst.Orientation = Enum.ParticleOrientation[orient]
			inst.Size = numSeq(L.Size, 1)
			inst.Transparency = numSeq(L.Transparency, 0)
			inst.Color = colSeq(L.Color)
			inst.LightEmission = L.LightEmission or 0
			inst.LightInfluence = L.LightInfluence or 1
			inst.Brightness = L.Brightness or 1
			inst.Drag = L.Drag or 0
			local a = L.Acceleration or { 0, 0, 0 }
			inst.Acceleration = Vector3.new(a[1], a[2], a[3])
			inst.Rotation = range(L.Rotation, 0)
			inst.RotSpeed = range(L.RotSpeed, 0)
			inst.LockedToPart = false
			inst.Rate = L.Rate or 0
			-- las ráfagas (EmitCount) no emiten solas: las dispara Emit; las de Rate emiten mientras estén prendidas
			inst.Enabled = (L.Rate or 0) > 0 and (L.EmitDuration or 0) == 0
			local ss = L.ShapeSize or { 0, 0, 0 }
			if ss[1] + ss[2] + ss[3] > 0 then
				inst:SetAttribute("ShapeSize", Vector3.new(ss[1], ss[2], ss[3]))
			end
		end
		inst.Name = L.name
		for _, attr in ipairs({ "EmitDelay", "EmitCount", "EmitDuration" }) do
			if (L[attr] or 0) > 0 then
				inst:SetAttribute(attr, L[attr])
			end
		end
		inst.Parent = fx
	end
	fx.Parent = root
	count += 1
end

local dir = OUT:match("^(.*)/[^/]+$")
if dir and not fs.isDir(dir) then
	fs.writeDir(dir)
end
fs.writeFile(OUT, roblox.serializeModel({ root }))
print(`{count} efectos -> {OUT}`)
local list = {}
for name in pairs(missing) do
	table.insert(list, name)
end
table.sort(list)
if #list > 0 then
	print(`texturas sin id (falta subirlas): {table.concat(list, ", ")}`)
end
