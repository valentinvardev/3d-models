--[[
	Spec de poses (datos) -> KeyframeSequence R15. Luau puro: corre igual en Lune (tools/roblox/anim_build.luau,
	que escribe el .rbxm que se sube) y pegado en Studio (vista previa con StepAnimations).

	Convención de ángulos (de vendor/skills/syphodev-roblox-ai-skills/.../scripts/r6_joint.py, en grados,
	medidos en los ejes de reposo del padre, marco de Roblox: +X derecha del personaje, +Y arriba, -Z frente):
	  Root, Waist, Neck (la pieza hija queda ARRIBA de la articulación):
	    pitch + = se inclina hacia adelante   lean + = se tumba a la izquierda del personaje   turn + = gira a la izquierda
	  hombros, codos, muñecas, caderas, rodillas, tobillos (la pieza cuelga ABAJO):
	    swing + = el miembro va hacia adelante   spread + = se abre hacia afuera   twist + = gira sobre el eje vertical
	  pos = {dx, dy, dz} en studs (sube, baja o adelanta la cadera en Root).
	W = Ry(turn|twist) * Rz(lean|±spread) * Rx(-pitch|swing). Los rigs de la fábrica tienen las articulaciones
	alineadas a los ejes (C0 sin rotación), así que la Pose.CFrame es directamente CFrame(pos) * W.
	Los ángulos de un hijo se suman a los del padre: inclinar el torso 20° tira los brazos 20° para atrás.

	Spec:
	  { name, loop, priority ("Core"|"Idle"|"Movement"|"Action"...), keys = { { t, ease, joints = { <Joint> = {...} } } },
	    markers = { { t, name, value? } }, props = { <Pieza> = { parent = "RightHand" | <otra pieza del objeto> } }? }

	Objetos en la mano (D024): "props" declara las piezas del objeto y de quién cuelgan. La raíz (la pieza con el
	marcador _Grip, "Body") cuelga de RightHand por un Motor6D cuyo C0 es el punto de agarre de la mano y C1 el
	_Grip del objeto, sin rotación: en reposo los ejes del objeto son los de la mano (con el brazo colgando, el
	caño mira al frente). Cada pieza que se mueve sola (Cylinder, Hammer...) cuelga de la raíz con su origen.
	Sus articulaciones se llaman como la pieza y llevan rot = {x, y, z} en grados (CFrame.Angles, en los ejes del
	padre), pos = {dx, dy, dz} y pivot = {x, y, z} opcional: gira alrededor de ese punto (en studs, desde la
	articulación) en vez de la articulación; así el revólver gira en el dedo, por el guardamonte.
	  ease del key = cómo se va de ESE key al siguiente: "linear" | "constant" | "in" (acelera hacia el
	  siguiente) | "out" (frena al llegar) | "smooth". Una articulación puede pisarlo con su propio "ease". Una articulación que un key no nombra no lleva Pose en
	  ese key: Roblox interpola entre los keys que sí la tienen. Una articulación que ningún key nombra no
	  se toca nunca (un clip de brazos no clava las piernas).

	Criaturas con esqueleto propio (toro, buitre): spec.tree = { <Pieza> = <pieza padre> } reemplaza al R15 entero;
	la raíz cuelga de "HumanoidRootPart". Cada articulación se llama como la pieza que mueve y se anima como una
	pieza de objeto (rot, pos, pivot), en los ejes de reposo del padre. anim_build.luau llena spec.tree con el
	"skeleton.tree" del rig.json que nombra spec.rig, para no copiar el árbol en cada clip.
]]

local M = {}

M.TREE = { -- pieza (nombre de la Pose) = { pieza padre, articulación }
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
local UP = { Root = true, Waist = true, Neck = true }
local UP_KEYS = { pitch = true, lean = true, turn = true, pos = true, ease = true }
local LIMB_KEYS = { swing = true, spread = true, twist = true, pos = true, ease = true }
local PROP_KEYS = { rot = true, pos = true, pivot = true, ease = true }
-- CubicV2 respeta el nombre de la dirección; el que la invierte es solo el Cubic viejo (medido en Studio:
-- vendor/skills/hildlabs-openrig-studio/docs/how-it-works.md, corrige el traps.md #36 de SyphoDev).
-- El easing de un tramo es el de la pose donde arranca.
local EASE = {
	linear = { "Linear", "In" },
	constant = { "Constant", "In" },
	["in"] = { "CubicV2", "In" },
	out = { "CubicV2", "Out" },
	smooth = { "CubicV2", "InOut" },
}

-- árbol del spec: el R15 más las piezas del objeto en la mano (articulación = nombre de la pieza), o el esqueleto
-- propio de una criatura (spec.tree) solo
function M.tree(spec)
	local tree, partOf = {}, {}
	if spec.tree then
		for part, parent in pairs(spec.tree) do
			tree[part] = { parent, part }
			partOf[part] = part
		end
		for part, parent in pairs(spec.tree) do
			assert(
				tree[parent] or parent == "HumanoidRootPart",
				`{spec.name}: la pieza {part} cuelga de {parent}, que no existe`
			)
		end
		return tree, partOf
	end
	for part, link in pairs(M.TREE) do
		tree[part] = link
		partOf[link[2]] = part
	end
	for part, p in pairs(spec.props or {}) do
		tree[part] = { p.parent, part }
		partOf[part] = part
	end
	for part, p in pairs(spec.props or {}) do -- después de registrarlas todas: pairs no tiene orden
		assert(
			tree[p.parent] or p.parent == "HumanoidRootPart",
			`{spec.name}: la pieza {part} cuelga de {p.parent}, que no existe`
		)
	end
	return tree, partOf
end

function M.check(spec)
	local tree, PART_OF = M.tree(spec)
	assert(type(spec.name) == "string", "spec sin name")
	assert(#spec.keys >= 1, spec.name .. ": sin keys")
	local last = -1
	for i, k in ipairs(spec.keys) do
		assert(k.t > last, `{spec.name}: los keys van en orden de tiempo (key {i})`)
		last = k.t
		assert(EASE[k.ease or "smooth"], `{spec.name}: ease desconocido {k.ease}`)
		for joint, sem in pairs(k.joints or {}) do
			assert(PART_OF[joint], `{spec.name}: articulación desconocida {joint}`)
			-- criatura primero: el toro tiene una pieza "Neck", que no es la articulación Neck del R15
			local allowed = spec.tree and PROP_KEYS
				or UP[joint] and UP_KEYS
				or (spec.props and spec.props[joint]) and PROP_KEYS
				or LIMB_KEYS
			for key in pairs(sem) do
				assert(allowed[key], `{spec.name}: {joint} no lleva '{key}'`)
			end
			assert(
				sem.ease == nil or EASE[sem.ease],
				`{spec.name}: ease desconocido {sem.ease} en {joint}`
			)
		end
	end
end

function M.transform(env, joint: string, sem, isProp: boolean?): CFrame
	local CFrame, Vector3 = env.CFrame, env.Vector3
	local r = math.rad
	if isProp then
		local rot, p, pv = sem.rot or { 0, 0, 0 }, sem.pos or { 0, 0, 0 }, sem.pivot or { 0, 0, 0 }
		local pivot = CFrame.new(Vector3.new(pv[1], pv[2], pv[3]))
		return CFrame.new(Vector3.new(p[1], p[2], p[3]))
			* pivot
			* CFrame.Angles(r(rot[1]), r(rot[2]), r(rot[3]))
			* pivot:Inverse()
	end
	local a, b, c
	if UP[joint] then
		a, b, c = r(-(sem.pitch or 0)), r(sem.lean or 0), r(sem.turn or 0)
	else
		local side = joint:sub(1, 5) == "Right" and 1 or -1
		a, b, c = r(sem.swing or 0), r((sem.spread or 0) * side), r(sem.twist or 0)
	end
	local p = sem.pos or { 0, 0, 0 }
	return CFrame.new(Vector3.new(p[1], p[2], p[3]))
		* CFrame.Angles(0, c, 0)
		* CFrame.Angles(0, 0, b)
		* CFrame.Angles(a, 0, 0)
end

function M.build(env, spec)
	local Instance, Enum = env.Instance, env.Enum
	M.check(spec)
	local TREE, PART_OF = M.tree(spec)
	local seq = Instance.new("KeyframeSequence")
	seq.Name = spec.name
	seq.Loop = spec.loop == true
	seq.Priority = Enum.AnimationPriority[spec.priority or "Action"]
	local frames = {}
	for _, k in ipairs(spec.keys) do
		local kf = Instance.new("Keyframe")
		kf.Name = "Keyframe"
		kf.Time = k.t
		local style = EASE[k.ease or "smooth"]
		local poses = {}
		local function pose(part)
			if poses[part] then
				return poses[part]
			end
			local po = Instance.new("Pose")
			po.Name = part
			po.Weight = 0
			po.EasingStyle = Enum.PoseEasingStyle[style[1]]
			po.EasingDirection = Enum.PoseEasingDirection[style[2]]
			poses[part] = po
			if part == "HumanoidRootPart" then
				po.Parent = kf
			else
				po.Parent = pose(TREE[part][1])
			end
			return po
		end
		pose("HumanoidRootPart")
		for joint, sem in pairs(k.joints or {}) do
			local po = pose(PART_OF[joint])
			po.CFrame = M.transform(
				env,
				joint,
				sem,
				spec.tree ~= nil or (spec.props ~= nil and spec.props[joint] ~= nil)
			)
			po.Weight = 1
			if sem.ease then -- una articulación puede ir con otro ritmo que el resto del key (la cadera rebota)
				po.EasingStyle = Enum.PoseEasingStyle[EASE[sem.ease][1]]
				po.EasingDirection = Enum.PoseEasingDirection[EASE[sem.ease][2]]
			end
		end
		kf.Parent = seq
		table.insert(frames, kf)
	end
	for _, m in ipairs(spec.markers or {}) do
		local at
		for _, kf in ipairs(frames) do
			if math.abs(kf.Time - m.t) < 1e-4 then
				at = kf
			end
		end
		assert(at, `{spec.name}: el marcador {m.name} en t={m.t} no cae en un key`)
		local mk = Instance.new("KeyframeMarker")
		mk.Name = m.name
		mk.Value = tostring(m.value or "")
		mk.Parent = at
	end
	return seq
end

return M
