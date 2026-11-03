--[[
	Arma el .rbxm de un personaje R15 (enemigo, NPC, jefe) a partir de los datos de sus piezas.

	  lune run tools/roblox/rig_build.luau <rig.json> <salida.rbxm>

	rig.json (lo escribe tools/roblox/rig_data.py desde el GLB de la fábrica, y se completa con los ids
	que deja la subida a Roblox, leídos en Studio):
	  { "name": "Walker_A", "nodes": [ { "name": "Head", "origin": [x,y,z], "cframe": [12 números],
	    "size": [x,y,z], "mesh": "rbxassetid://..."?, "texture": "rbxassetid://..."?, "meshSize": [x,y,z]?,
	    "material": "Neon"? } ] }
	  Coordenadas de Roblox relativas al piso debajo del personaje (+X derecha, +Y arriba, -Z frente).
	  "origin" es el origen del nodo del GLB: la fábrica lo pone en la articulación con su padre.
	  Sin "mesh", la pieza sale como un Part del mismo tamaño (maniquí para probar el rig y las animaciones).

	Contrato (assets/models/rbx/README.md del juego, valores medidos contra el R15 por defecto el 2026-10-28):
	  Model con PrimaryPart = HumanoidRootPart (2x2x1, invisible, sin colisión, en la articulación de la
	  cadera), Humanoid R15 con Animator y sin escalado automático, parte "Head", 15 Motor6D con los nombres
	  R15 (dentro de su Part1, C0/C1 = los <Joint>RigAttachment), lo que no es R15 (Eyes, Acc_*, overlays)
	  soldado con Weld (C0 explícito), sin scripts, pies en y = 0. Colisión como el R15 por defecto (torso y
	  cabeza sí, miembros no) y fidelidad Box: muchos enemigos a la vez, y el headshot solo pide la caja.
	  BuildRigFromAttachments no crea las juntas en modo Edit (medido): por eso se arman acá.

	Criatura con esqueleto propio (toro, buitre): si el rig.json trae "skeleton", se arma con ese árbol en lugar
	del R15 (buildCreature, más abajo). Un rig sin "skeleton" sale byte a byte igual que antes.
]]

local fs = require("@lune/fs")
local process = require("@lune/process")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")

local Instance, CFrame, Vector3, Enum = roblox.Instance, roblox.CFrame, roblox.Vector3, roblox.Enum

local R15 = { -- pieza = { padre, articulación }
	LowerTorso = { "HumanoidRootPart", "Root" },
	UpperTorso = { "LowerTorso", "Waist" },
	Head = { "UpperTorso", "Neck" },
	LeftUpperArm = { "UpperTorso", "LeftShoulder" },
	LeftLowerArm = { "LeftUpperArm", "LeftElbow" },
	LeftHand = { "LeftLowerArm", "LeftWrist" },
	RightUpperArm = { "UpperTorso", "RightShoulder" },
	RightLowerArm = { "RightUpperArm", "RightElbow" },
	RightHand = { "RightLowerArm", "RightWrist" },
	LeftUpperLeg = { "LowerTorso", "LeftHip" },
	LeftLowerLeg = { "LeftUpperLeg", "LeftKnee" },
	LeftFoot = { "LeftLowerLeg", "LeftAnkle" },
	RightUpperLeg = { "LowerTorso", "RightHip" },
	RightLowerLeg = { "RightUpperLeg", "RightKnee" },
	RightFoot = { "RightLowerLeg", "RightAnkle" },
}
local COLLIDE = { LowerTorso = true, UpperTorso = true, Head = true }
local ORDER =
	{ -- orden fijo: con pairs() un empate de distancia daba otro anfitrión en cada corrida
		"LowerTorso",
		"UpperTorso",
		"Head",
		"LeftUpperArm",
		"LeftLowerArm",
		"LeftHand",
		"RightUpperArm",
		"RightLowerArm",
		"RightHand",
		"LeftUpperLeg",
		"LeftLowerLeg",
		"LeftFoot",
		"RightUpperLeg",
		"RightLowerLeg",
		"RightFoot",
	}

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

local function build(data)
	local report = {}
	local nodes = {}
	for _, n in ipairs(data.nodes) do
		nodes[n.name] = n
	end
	for part in pairs(R15) do
		assert(nodes[part], `{data.name}: falta la pieza {part}`)
	end

	-- ¿mira a -Z? Los ojos (o la cabeza) tienen que quedar delante del cuello
	local eye = nodes.Eyes or nodes.Head
	local front = eye.cframe[3] - nodes.Head.origin[3]
	local turn = front > 0 and CFrame.Angles(0, math.pi, 0) or CFrame.new()
	table.insert(
		report,
		string.format(
			"frente: ojos %.2f en Z respecto del cuello%s",
			front,
			front > 0 and " -> girado 180°" or ""
		)
	)

	-- pies en y = 0
	local minY = math.huge
	for _, n in pairs(nodes) do
		local cf = turn * CFrame.new(table.unpack(n.cframe))
		local h = v3(n.size) / 2
		for _, sx in ipairs({ -1, 1 }) do
			for _, sy in ipairs({ -1, 1 }) do
				for _, sz in ipairs({ -1, 1 }) do
					minY = math.min(minY, (cf * Vector3.new(sx * h.X, sy * h.Y, sz * h.Z)).Y)
				end
			end
		end
	end
	local lift = CFrame.new(0, -minY, 0)

	local model = Instance.new("Model")
	model.Name = data.name
	local parts, joint = {}, {}
	local markers = {}
	for name, n in pairs(nodes) do
		if name:sub(1, 1) == "_" then -- marcador de la fábrica (_Muzzle, _Grip...): Attachment, no pieza
			markers[name] = n
			nodes[name] = nil
		end
	end
	for name, n in pairs(nodes) do
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
		end
		p.Name = name
		p.Size = v3(n.size)
		p.CFrame = lift * turn * CFrame.new(table.unpack(n.cframe))
		p.Material = Enum.Material[n.material or "SmoothPlastic"]
		p.Color = roblox.Color3.new(1, 1, 1)
		p.Anchored = false
		p.CanCollide = COLLIDE[name] == true
		p.CanQuery = true
		p.CanTouch = true
		p.Parent = model
		parts[name] = p
		joint[name] = (lift * turn * CFrame.new(v3(n.origin))).Position
	end

	local hrp = Instance.new("Part")
	hrp.Name = "HumanoidRootPart"
	hrp.Size = Vector3.new(2, 2, 1)
	hrp.CFrame = CFrame.new(joint.LowerTorso)
	hrp.Transparency = 1
	hrp.CanCollide = false -- contrato del juego (assets/models/rbx/README.md): la colisión la dan torso y cabeza
	hrp.Anchored = false
	hrp.Parent = model
	model.PrimaryPart = hrp
	parts.HumanoidRootPart = hrp

	-- agarre de las manos (rig.json "rightGrip", en coordenadas del cuerpo; la izquierda es su espejo): un NPC que
	-- saca un arma la toma como el jugador (D024): C0 = CFrame.new(RightGripAttachment.Position), sin rotación
	if data.rightGrip then
		local g = data.rightGrip
		for _, side in ipairs({
			{ "RightHand", "RightGripAttachment", 1 },
			{ "LeftHand", "LeftGripAttachment", -1 },
		}) do
			local at = lift * turn * CFrame.new(side[3] * g[1], g[2], g[3])
			local a = Instance.new("Attachment")
			a.Name = side[2]
			a.CFrame = CFrame.new((parts[side[1]].CFrame:Inverse() * at).Position)
			a.Parent = parts[side[1]]
		end
		table.insert(
			report,
			string.format("agarre: RightGripAttachment en (%.2f, %.2f, %.2f)", g[1], g[2], g[3])
		)
	end

	-- articulaciones: attachments alineados a los ejes en el punto de la articulación + Motor6D
	local motors = 0
	for part, link in pairs(R15) do
		local p0, p1 = parts[link[1]], parts[part]
		local at = CFrame.new(joint[part])
		local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
		a0.Name, a1.Name = link[2] .. "RigAttachment", link[2] .. "RigAttachment"
		a0.CFrame, a1.CFrame = p0.CFrame:Inverse() * at, p1.CFrame:Inverse() * at
		a0.Parent, a1.Parent = p0, p1
		local m = Instance.new("Motor6D")
		m.Name = link[2]
		m.Part0, m.Part1 = p0, p1
		m.C0, m.C1 = a0.CFrame, a1.CFrame
		m.Parent = p1
		motors += 1
	end

	local function boxDist(p, at) -- distancia de un punto a la caja de una pieza (0 adentro)
		local l = p.CFrame:Inverse() * at
		local h = p.Size / 2
		return Vector3.new(
			math.max(math.abs(l.X) - h.X, 0),
			math.max(math.abs(l.Y) - h.Y, 0),
			math.max(math.abs(l.Z) - h.Z, 0)
		).Magnitude
	end

	-- lo que no es R15 va soldado: los ojos y el sombrero a la cabeza; el resto (armas, estrella, esposas,
	-- overlays) a la pieza R15 cuya caja queda más cerca de su origen (la fábrica lo pone donde se apoya)
	for name, n in pairs(nodes) do
		if not R15[name] then
			local best, dist = "Head", math.huge
			for _, part in ipairs(ORDER) do -- un overlay lleva el mismo origen que la pieza que cubre
				if
					(joint[part] - joint[name]).Magnitude < 0.02
					and name ~= "Eyes"
					and name ~= "Acc_Hat"
				then
					best, dist = part, -1
				end
			end
			if n.weldTo and parts[n.weldTo] then -- a mano en el rig.json, cuando el origen del modelo no sirve
				best, dist = n.weldTo, -1
			end
			if name ~= "Eyes" and name ~= "Acc_Hat" and dist > -1 then
				-- si el origen cae adentro de dos cajas (el revólver del Predicador: mano y antebrazo), gana la del
				-- centro más cercano; antes desempataba el orden de ORDER y el revólver izquierdo iba al antebrazo
				local near = math.huge
				for _, part in ipairs(ORDER) do
					local d = boxDist(parts[part], joint[name])
					local c = (parts[part].CFrame.Position - joint[name]).Magnitude -- Lune no tiene Part.Position
					if d < dist - 1e-6 or (math.abs(d - dist) <= 1e-6 and c < near) then
						best, dist, near = part, d, c
					end
				end
			end
			-- Weld con C0 y no WeldConstraint: el WeldConstraint que escribe Lune no guarda el desplazamiento y en
			-- Studio pega la pieza en el centro de la otra (medido el 2026-10-28: sombrero y ojos en la cabeza)
			local w = Instance.new("Weld")
			w.Name = name .. "Weld"
			w.Part0, w.Part1 = parts[best], parts[name]
			w.C0, w.C1 = parts[best].CFrame:Inverse() * parts[name].CFrame, CFrame.new()
			w.Parent = parts[name]
			parts[name].CanCollide = false
			parts[name].Massless = true
			table.insert(report, `extra: {name} soldado a {best}`)
		end
	end

	-- marcadores: Attachment con el mismo nombre en el accesorio que lo contiene (la boca del caño queda
	-- en el borde del arma: 0,15 de tolerancia) o, si no, en la pieza más cercana
	for name, n in pairs(markers) do
		-- mk.marker deja el origen en 0 y la cajita en el lugar: la posición es el centro de la caja
		local at = (lift * turn * CFrame.new(n.cframe[1], n.cframe[2], n.cframe[3])).Position
		local best, dist = nil, math.huge
		for pname, p in pairs(parts) do
			if pname ~= "HumanoidRootPart" then
				local d = boxDist(p, at)
				if not R15[pname] and d <= 0.15 then
					d -= 1 -- un accesorio cerca gana siempre a un brazo o un pie
				end
				if d < dist then
					best, dist = pname, d
				end
			end
		end
		local a = Instance.new("Attachment")
		a.Name = name
		a.CFrame = parts[best].CFrame:Inverse() * CFrame.new(at)
		a.Parent = parts[best]
		table.insert(report, `marcador: {name} en {best}`)
	end

	local hum = Instance.new("Humanoid")
	hum.RigType = Enum.HumanoidRigType.R15
	hum.AutomaticScalingEnabled = false
	hum.HipHeight = hrp.CFrame.Position.Y - 1
	Instance.new("Animator").Parent = hum
	hum.Parent = model

	local top = -math.huge
	for _, p in pairs(parts) do
		top = math.max(top, p.CFrame.Position.Y + p.Size.Y / 2)
	end
	table.insert(
		report,
		string.format(
			"Motor6D %d/15 · alto ~%.2f · HipHeight %.3f · piezas %d",
			motors,
			top,
			hum.HipHeight,
			#model:GetChildren() - 1
		)
	)
	return model, report
end

--[[
	Criatura con esqueleto propio. Mismo contrato que el R15 (Humanoid R15 con Animator y sin escalado automático,
	HumanoidRootPart transparente y sin colisión como PrimaryPart, parte "Head", cada Motor6D dentro de su Part1
	con C0/C1 en la articulación y alineados a los ejes, extras con Weld y C0 explícito, sin scripts, lo más bajo
	en y = 0), con el árbol del rig.json:
	  "skeleton": {
	    "tree":    { <Pieza> = <padre> }   la raíz cuelga de "HumanoidRootPart". Cada Motor6D se llama como la pieza
	                                       que mueve (como las piezas de un objeto en la mano) y sus dos Attachments
	                                       "<Pieza>RigAttachment" (lo que espera BuildRigFromAttachments)
	    "joints":  { <Pieza> = {x,y,z} }   la articulación cuando no es el "origin" de la pieza: la fábrica deja el
	                                       origen de la raíz en el piso. El HumanoidRootPart va centrado en la de la raíz
	    "hrpSize": {x,y,z}                 sin él, 2x2x1 como el R15
	    "collide": [piezas]                las que colisionan; sin él, la raíz y Head
	    "weldTo":  { <extra> = <pieza> }   a qué pieza va soldado un extra, cuando la caja no alcanza para elegir
	    "ground", "air"                  no son del rig: son de anim_preview (piezas que pisan; criatura que vuela)
	  }
	HipHeight = altura del HumanoidRootPart - la mitad de su alto, la misma cuenta que el R15: el Humanoid deja el
	fondo del HRP a HipHeight del piso, y así lo más bajo del modelo (y = 0) queda apoyado.
	Lo que no está en el árbol va soldado a "weldTo" o a la pieza del árbol cuya caja queda más cerca del CENTRO de
	su caja: el origen de un extra suele ser el del modelo, en el piso (las vetas de plata del toro).
]]
local function buildCreature(data)
	local sk = data.skeleton
	local report = {}
	local nodes, markers = {}, {}
	for _, n in ipairs(data.nodes) do
		if n.name:sub(1, 1) == "_" then -- marcador de la fábrica: Attachment, no pieza
			markers[n.name] = n
		else
			nodes[n.name] = n
		end
	end
	assert(nodes.Head, `{data.name}: falta la parte Head (el headshot la busca por nombre)`)

	-- orden fijo, de la raíz hacia afuera y por nombre: pairs no tiene orden
	local function depth(part)
		local d = 0
		while sk.tree[part] do
			part, d = sk.tree[part], d + 1
			assert(d < 64, `{data.name}: el esqueleto tiene un ciclo`)
		end
		return d
	end
	local order, root = {}, nil
	for part, parent in pairs(sk.tree) do
		assert(nodes[part], `{data.name}: la pieza {part} del esqueleto no está en nodes`)
		assert(
			parent == "HumanoidRootPart" or sk.tree[parent],
			`{data.name}: {part} cuelga de {parent}, que no está en el esqueleto`
		)
		if parent == "HumanoidRootPart" then
			assert(
				root == nil,
				`{data.name}: dos raíces ({root} y {part}); cuelga una sola de HumanoidRootPart`
			)
			root = part
		end
		table.insert(order, part)
	end
	assert(root, `{data.name}: ninguna pieza cuelga de HumanoidRootPart`)
	table.sort(order, function(a, b)
		local da, db = depth(a), depth(b)
		if da ~= db then
			return da < db
		end
		return a < b
	end)

	-- ¿mira a -Z? La cabeza tiene que quedar delante de su articulación (misma regla que el R15)
	local eye = nodes.Eyes or nodes.Head
	local front = eye.cframe[3] - nodes.Head.origin[3]
	local turn = front > 0 and CFrame.Angles(0, math.pi, 0) or CFrame.new()
	table.insert(
		report,
		string.format(
			"frente: cabeza %.2f en Z respecto de su articulación%s",
			front,
			front > 0 and " -> girado 180°" or ""
		)
	)

	-- lo más bajo en y = 0
	local minY = math.huge
	for _, n in pairs(nodes) do
		local cf = turn * CFrame.new(table.unpack(n.cframe))
		local h = v3(n.size) / 2
		for _, sx in ipairs({ -1, 1 }) do
			for _, sy in ipairs({ -1, 1 }) do
				for _, sz in ipairs({ -1, 1 }) do
					minY = math.min(minY, (cf * Vector3.new(sx * h.X, sy * h.Y, sz * h.Z)).Y)
				end
			end
		end
	end
	local lift = CFrame.new(0, -minY, 0)

	local collide = {}
	for _, part in ipairs(sk.collide or { root, "Head" }) do
		assert(nodes[part], `{data.name}: collide nombra {part}, que no está en nodes`)
		collide[part] = true
	end

	local model = Instance.new("Model")
	model.Name = data.name
	local parts, joint = {}, {}
	local names = {}
	for name in pairs(nodes) do
		table.insert(names, name)
	end
	table.sort(names)
	for _, name in ipairs(names) do
		local n = nodes[name]
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
		end
		p.Name = name
		p.Size = v3(n.size)
		p.CFrame = lift * turn * CFrame.new(table.unpack(n.cframe))
		p.Material = Enum.Material[n.material or "SmoothPlastic"]
		p.Color = roblox.Color3.new(1, 1, 1)
		p.Anchored = false
		p.CanCollide = collide[name] == true
		p.CanQuery = true
		p.CanTouch = true
		p.Parent = model
		parts[name] = p
		local at = sk.joints and sk.joints[name] or n.origin
		joint[name] = (lift * turn * CFrame.new(v3(at))).Position
	end

	local hrp = Instance.new("Part")
	hrp.Name = "HumanoidRootPart"
	hrp.Size = v3(sk.hrpSize or { 2, 2, 1 })
	hrp.CFrame = CFrame.new(joint[root])
	hrp.Transparency = 1
	hrp.CanCollide = false -- contrato del juego: la colisión la dan las piezas de "collide"
	hrp.Anchored = false
	hrp.Parent = model
	model.PrimaryPart = hrp
	parts.HumanoidRootPart = hrp

	-- articulaciones: attachments alineados a los ejes en el punto de la articulación + Motor6D con el nombre de la pieza
	for _, part in ipairs(order) do
		local p0, p1 = parts[sk.tree[part]], parts[part]
		local at = CFrame.new(joint[part])
		local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
		a0.Name, a1.Name = part .. "RigAttachment", part .. "RigAttachment"
		a0.CFrame, a1.CFrame = p0.CFrame:Inverse() * at, p1.CFrame:Inverse() * at
		a0.Parent, a1.Parent = p0, p1
		local m = Instance.new("Motor6D")
		m.Name = part
		m.Part0, m.Part1 = p0, p1
		m.C0, m.C1 = a0.CFrame, a1.CFrame
		m.Parent = p1
		local j = joint[part]
		table.insert(
			report,
			string.format(
				"Motor6D %s: %s -> %s en (%.2f, %.2f, %.2f)",
				part,
				sk.tree[part],
				part,
				j.X,
				j.Y,
				j.Z
			)
		)
	end

	local function boxDist(p, at) -- distancia de un punto a la caja de una pieza (0 adentro)
		local l = p.CFrame:Inverse() * at
		local h = p.Size / 2
		return Vector3.new(
			math.max(math.abs(l.X) - h.X, 0),
			math.max(math.abs(l.Y) - h.Y, 0),
			math.max(math.abs(l.Z) - h.Z, 0)
		).Magnitude
	end

	-- lo que no está en el árbol (ojos, vetas de plata) va soldado, con Weld y C0 explícito: el WeldConstraint que
	-- escribe Lune pierde el desplazamiento en Studio (medido el 2026-10-28)
	for _, name in ipairs(names) do
		if not sk.tree[name] then
			local n = nodes[name]
			local center = parts[name].CFrame.Position
			local best, dist, near = nil, math.huge, math.huge
			-- a mano: en el nodo o en skeleton.weldTo, que sobrevive a regenerar el rig.json desde el GLB
			local to = n.weldTo or (sk.weldTo and sk.weldTo[name])
			if to then
				assert(parts[to], `{data.name}: {name}.weldTo = {to}, que no existe`)
				best = to
			else
				for _, part in ipairs(order) do -- adentro de dos cajas: gana el centro más cercano
					local d = boxDist(parts[part], center)
					local c = (parts[part].CFrame.Position - center).Magnitude
					if d < dist - 1e-6 or (math.abs(d - dist) <= 1e-6 and c < near) then
						best, dist, near = part, d, c
					end
				end
			end
			local w = Instance.new("Weld")
			w.Name = name .. "Weld"
			w.Part0, w.Part1 = parts[best], parts[name]
			w.C0, w.C1 = parts[best].CFrame:Inverse() * parts[name].CFrame, CFrame.new()
			w.Parent = parts[name]
			parts[name].CanCollide = false
			parts[name].Massless = true
			table.insert(report, `extra: {name} soldado a {best}`)
		end
	end

	-- marcadores: en el extra que lo contiene (0,15 de tolerancia) o, si no, en la pieza más cercana
	local marks = {}
	for name in pairs(markers) do
		table.insert(marks, name)
	end
	table.sort(marks)
	for _, name in ipairs(marks) do
		local n = markers[name]
		local at = (lift * turn * CFrame.new(n.cframe[1], n.cframe[2], n.cframe[3])).Position
		local best, dist = nil, math.huge
		for _, pname in ipairs(names) do
			local d = boxDist(parts[pname], at)
			if not sk.tree[pname] and d <= 0.15 then
				d -= 1
			end
			if d < dist then
				best, dist = pname, d
			end
		end
		local a = Instance.new("Attachment")
		a.Name = name
		a.CFrame = parts[best].CFrame:Inverse() * CFrame.new(at)
		a.Parent = parts[best]
		table.insert(report, `marcador: {name} en {best}`)
	end

	local hum = Instance.new("Humanoid")
	hum.RigType = Enum.HumanoidRigType.R15
	hum.AutomaticScalingEnabled = false
	hum.HipHeight = hrp.CFrame.Position.Y - hrp.Size.Y / 2
	-- sin el cuello del R15: que el Humanoid no muera por "falta el Neck" (no medido en Studio; ver README)
	hum.RequiresNeck = false
	Instance.new("Animator").Parent = hum
	hum.Parent = model

	local top, cols = -math.huge, {}
	for _, p in pairs(parts) do
		top = math.max(top, p.CFrame.Position.Y + p.Size.Y / 2)
	end
	for _, name in ipairs(names) do
		if parts[name].CanCollide then
			table.insert(cols, name)
		end
	end
	local hp, hs = hrp.CFrame.Position, hrp.Size
	table.insert(
		report,
		string.format(
			"HumanoidRootPart %.2fx%.2fx%.2f en (%.2f, %.2f, %.2f) · HipHeight %.3f · piso por HipHeight y = %.3f",
			hs.X,
			hs.Y,
			hs.Z,
			hp.X,
			hp.Y,
			hp.Z,
			hum.HipHeight,
			hp.Y - hs.Y / 2 - hum.HipHeight
		)
	)
	table.insert(
		report,
		string.format(
			"Motor6D %d · alto ~%.2f · colisionan %s · piezas %d",
			#order,
			top,
			table.concat(cols, ", "),
			#model:GetChildren() - 1
		)
	)
	return model, report
end

if #process.args < 2 then
	print("uso: lune run tools/roblox/rig_build.luau <rig.json> <salida.rbxm>")
	process.exit(1)
end
local data = serde.decode("json", fs.readFile(process.args[1]))
local model, report
if data.skeleton then
	model, report = buildCreature(data)
else
	model, report = build(data)
end
fs.writeFile(process.args[2], roblox.serializeModel({ model }))
print(table.concat(report, "\n"))
print(`-> {process.args[2]}`)
