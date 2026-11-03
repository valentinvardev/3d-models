--[[
	Para pegar en execute_luau (MCP de Studio), en modo Edit. No corre con Lune: usa InsertService.

	Carga los Models subidos con opencloud.py (sin meterlos en el juego) y lee de cada MeshPart lo que
	rig_build necesita: centro, tamaño, MeshSize, MeshId, TextureID y rotación. Imprime una línea por pieza
	con el formato de rig_data.py (parse_studio_txt), precedida por "# <Id>". Esas líneas se guardan en
	04_roblox/<Id>.studio.txt y se pasan con `py -I tools/roblox/rig_data.py ids <Id> <ruta .studio.txt>`.

	ASSETS: { [Id de la fábrica] = assetId del Model }, sacado de assets/models/western/_roblox.json.
]]

local ASSETS = {
	-- WST_Enemy_Walker_A = 135446854627431,
}

local IS = game:GetService("InsertService")

local function f(v)
	return string.format("%.4f", v):gsub("%.?0+$", "")
end

local function vec(v)
	return `{f(v.X)},{f(v.Y)},{f(v.Z)}`
end

local function num(id)
	return (tostring(id):match("%d+")) or ""
end

local out = {}
for modelId, assetId in pairs(ASSETS) do
	local done, res
	task.spawn(function()
		local ok, m = pcall(IS.LoadAsset, IS, assetId)
		res = ok and m or tostring(m)
		done = true
	end)
	local t0 = os.clock()
	while not done and os.clock() - t0 < 40 do
		task.wait(0.2)
	end
	table.insert(out, "# " .. modelId)
	if typeof(res) ~= "Instance" then
		table.insert(out, "# falló: " .. tostring(res))
		continue
	end
	for _, p in ipairs(res:GetDescendants()) do
		if p:IsA("MeshPart") then
			local cf = p.CFrame
			local _, _, _, r00, r01, r02, r10, r11, r12, r20, r21, r22 = cf:GetComponents()
			local rot = { r00, r01, r02, r10, r11, r12, r20, r21, r22 }
			local ident = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }
			local isI = true
			for i = 1, 9 do
				if math.abs(rot[i] - ident[i]) > 1e-4 then
					isI = false
				end
			end
			local r = "I"
			if not isI then
				local parts = {}
				for i = 1, 9 do
					parts[i] = f(rot[i])
				end
				r = table.concat(parts, ",")
			end
			table.insert(
				out,
				table.concat({
					p.Name,
					vec(cf.Position),
					vec(p.Size),
					vec(p.MeshSize),
					num(p.MeshId),
					num(p.TextureID),
					r,
				}, "|")
			)
		end
	end
	res:Destroy()
end
return table.concat(out, "\n")
