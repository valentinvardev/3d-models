--[[
	Arma el .rbxm de una o varias animaciones R15 a partir de sus specs (JSON), para subirlas con
	tools/roblox/opencloud.py animation. La conversión es la de tools/roblox/anim_r15.luau, la misma
	que se usa para la vista previa en Studio.

	  lune run tools/roblox/anim_build.luau assets/animation/western/<Clip>.json [...]

	Deja al lado de cada spec <Clip>.rbxm (lo que se sube) y <Clip>.poses.json (las Pose.CFrame exactas de
	cada key, para la vista previa y los chequeos de tools/roblox/anim_preview.py: así la conversión de
	ángulos vive en un solo lugar). Imprime una línea por clip con keys, poses y duración.

	Criatura con esqueleto propio: el spec lleva "rig": "<ruta del rig.json, desde la raíz del repo>" y de ahí sale
	el árbol ("skeleton.tree"), que anim_r15 usa en lugar del R15 para anidar las Poses.
]]

local fs = require("@lune/fs")
local process = require("@lune/process")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")
local anim = require("./anim_r15")

local env = {
	CFrame = roblox.CFrame,
	Vector3 = roblox.Vector3,
	Instance = roblox.Instance,
	Enum = roblox.Enum,
}

if #process.args == 0 then
	print("uso: lune run tools/roblox/anim_build.luau <spec.json> [...]")
	process.exit(1)
end

-- "rig" del spec: desde donde se corre o desde la raíz del repo (lo que va antes de assets/ en la ruta del spec)
local function readRig(specPath, rigPath)
	local tries = { rigPath }
	local root = specPath:gsub("\\", "/"):match("^(.-)assets/")
	if root and root ~= "" then
		table.insert(tries, root .. rigPath)
	end
	for _, p in ipairs(tries) do
		if fs.isFile(p) then
			return serde.decode("json", fs.readFile(p))
		end
	end
	error(`{specPath}: no encuentro el rig {rigPath}`)
end

for _, path in ipairs(process.args) do
	if path:match("%.poses%.json$") then
		continue -- es una salida, no un spec (un glob Clip_*.json la agarra)
	end
	local spec = serde.decode("json", fs.readFile(path))
	if spec.rig then -- criatura con esqueleto propio: el árbol sale del rig.json, no se copia en cada clip
		assert(spec.tree == nil, `{path}: "rig" o "tree", no los dos`)
		local rig = readRig(path, spec.rig)
		assert(rig.skeleton and rig.skeleton.tree, `{spec.rig}: el rig no trae "skeleton.tree"`)
		spec.tree = rig.skeleton.tree
	end
	local seq = anim.build(env, spec)
	local out = path:gsub("%.json$", ".rbxm")
	fs.writeFile(out, roblox.serializeModel({ seq }))
	local dump = {
		name = spec.name,
		loop = seq.Loop,
		priority = spec.priority or "Action",
		keys = {},
		markers = spec.markers or {},
		rig = spec.rig, -- solo en una criatura: para qué esqueleto son estas poses
	}
	for _, kf in ipairs(seq:GetChildren()) do
		local key = { t = kf.Time, poses = {} }
		for _, po in ipairs(kf:GetDescendants()) do
			if po:IsA("Pose") and po.Weight > 0 then
				key.poses[po.Name] = {
					cf = { po.CFrame:GetComponents() },
					style = po.EasingStyle.Name,
					dir = po.EasingDirection.Name,
				}
			end
		end
		table.insert(dump.keys, key)
	end
	fs.writeFile((path:gsub("%.json$", ".poses.json")), serde.encode("json", dump, true))
	local poses = 0
	for _, d in ipairs(seq:GetDescendants()) do
		if d:IsA("Pose") and d.Weight > 0 then
			poses += 1
		end
	end
	local keys = seq:GetChildren()
	print(
		`{spec.name}: {#keys} keys, {poses} poses, {keys[#keys].Time} s, loop {seq.Loop} -> {out}`
	)
end
