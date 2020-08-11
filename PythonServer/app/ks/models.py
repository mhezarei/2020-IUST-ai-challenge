# -*- coding: utf-8 -*-

# python imports
import sys
import struct
from enum import Enum

PY3 = sys.version_info > (3,)


class ECell(Enum):
	Empty = 0
	FrontlineDelivery = 1
	Material = 2
	BacklineDelivery = 3
	Machine = 4


class MachineStatus(Enum):
	Idle = 0
	Working = 1
	AmmoReady = 2


class MaterialType(Enum):
	Powder = 0
	Iron = 1
	Carbon = 2
	Gold = 3
	Shell = 4


class AmmoType(Enum):
	RifleBullet = 0
	TankShell = 1
	HMGBullet = 2
	MortarShell = 3
	GoldenTankShell = 4


class UnitType(Enum):
	Soldier = 0
	Tank = 1
	HeavyMachineGunner = 2
	Mortar = 3
	GoldenTank = 4


class AgentType(Enum):
	Warehouse = 0
	Factory = 1


class Position(object):

	@staticmethod
	def name():
		return 'Position'


	def __init__(self, index=None):
		self.initialize(index)
	

	def initialize(self, index=None):
		self.index = index
	

	def serialize(self):
		s = b''
		
		# serialize self.index
		s += b'\x00' if self.index is None else b'\x01'
		if self.index is not None:
			s += struct.pack('i', self.index)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.index
		tmp0 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp0:
			self.index = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.index = None
		
		return offset


class Material(object):

	@staticmethod
	def name():
		return 'Material'


	def __init__(self, type=None, position=None, count=None, c_capacity=None):
		self.initialize(type, position, count, c_capacity)
	

	def initialize(self, type=None, position=None, count=None, c_capacity=None):
		self.type = type
		self.position = position
		self.count = count
		self.c_capacity = c_capacity
	

	def serialize(self):
		s = b''
		
		# serialize self.type
		s += b'\x00' if self.type is None else b'\x01'
		if self.type is not None:
			s += struct.pack('b', self.type.value)
		
		# serialize self.position
		s += b'\x00' if self.position is None else b'\x01'
		if self.position is not None:
			s += self.position.serialize()
		
		# serialize self.count
		s += b'\x00' if self.count is None else b'\x01'
		if self.count is not None:
			s += struct.pack('i', self.count)
		
		# serialize self.c_capacity
		s += b'\x00' if self.c_capacity is None else b'\x01'
		if self.c_capacity is not None:
			s += struct.pack('i', self.c_capacity)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.type
		tmp1 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp1:
			tmp2 = struct.unpack('b', s[offset:offset + 1])[0]
			offset += 1
			self.type = MaterialType(tmp2)
		else:
			self.type = None
		
		# deserialize self.position
		tmp3 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp3:
			self.position = Position()
			offset = self.position.deserialize(s, offset)
		else:
			self.position = None
		
		# deserialize self.count
		tmp4 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp4:
			self.count = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.count = None
		
		# deserialize self.c_capacity
		tmp5 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp5:
			self.c_capacity = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_capacity = None
		
		return offset


class Machine(object):

	@staticmethod
	def name():
		return 'Machine'


	def __init__(self, position=None, status=None, current_ammo=None, construction_rem_time=None):
		self.initialize(position, status, current_ammo, construction_rem_time)
	

	def initialize(self, position=None, status=None, current_ammo=None, construction_rem_time=None):
		self.position = position
		self.status = status
		self.current_ammo = current_ammo
		self.construction_rem_time = construction_rem_time
	

	def serialize(self):
		s = b''
		
		# serialize self.position
		s += b'\x00' if self.position is None else b'\x01'
		if self.position is not None:
			s += self.position.serialize()
		
		# serialize self.status
		s += b'\x00' if self.status is None else b'\x01'
		if self.status is not None:
			s += struct.pack('b', self.status.value)
		
		# serialize self.current_ammo
		s += b'\x00' if self.current_ammo is None else b'\x01'
		if self.current_ammo is not None:
			s += struct.pack('b', self.current_ammo.value)
		
		# serialize self.construction_rem_time
		s += b'\x00' if self.construction_rem_time is None else b'\x01'
		if self.construction_rem_time is not None:
			s += struct.pack('i', self.construction_rem_time)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.position
		tmp6 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp6:
			self.position = Position()
			offset = self.position.deserialize(s, offset)
		else:
			self.position = None
		
		# deserialize self.status
		tmp7 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp7:
			tmp8 = struct.unpack('b', s[offset:offset + 1])[0]
			offset += 1
			self.status = MachineStatus(tmp8)
		else:
			self.status = None
		
		# deserialize self.current_ammo
		tmp9 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp9:
			tmp10 = struct.unpack('b', s[offset:offset + 1])[0]
			offset += 1
			self.current_ammo = AmmoType(tmp10)
		else:
			self.current_ammo = None
		
		# deserialize self.construction_rem_time
		tmp11 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp11:
			self.construction_rem_time = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.construction_rem_time = None
		
		return offset


class FrontlineDelivery(object):

	@staticmethod
	def name():
		return 'FrontlineDelivery'


	def __init__(self, ammos=None, delivery_rem_time=None, c_delivery_duration=None):
		self.initialize(ammos, delivery_rem_time, c_delivery_duration)
	

	def initialize(self, ammos=None, delivery_rem_time=None, c_delivery_duration=None):
		self.ammos = ammos
		self.delivery_rem_time = delivery_rem_time
		self.c_delivery_duration = c_delivery_duration
	

	def serialize(self):
		s = b''
		
		# serialize self.ammos
		s += b'\x00' if self.ammos is None else b'\x01'
		if self.ammos is not None:
			tmp12 = b''
			tmp12 += struct.pack('I', len(self.ammos))
			while len(tmp12) and tmp12[-1] == b'\x00'[0]:
				tmp12 = tmp12[:-1]
			s += struct.pack('B', len(tmp12))
			s += tmp12
			
			for tmp13 in self.ammos:
				s += b'\x00' if tmp13 is None else b'\x01'
				if tmp13 is not None:
					s += struct.pack('b', tmp13.value)
				s += b'\x00' if self.ammos[tmp13] is None else b'\x01'
				if self.ammos[tmp13] is not None:
					s += struct.pack('i', self.ammos[tmp13])
		
		# serialize self.delivery_rem_time
		s += b'\x00' if self.delivery_rem_time is None else b'\x01'
		if self.delivery_rem_time is not None:
			s += struct.pack('i', self.delivery_rem_time)
		
		# serialize self.c_delivery_duration
		s += b'\x00' if self.c_delivery_duration is None else b'\x01'
		if self.c_delivery_duration is not None:
			s += struct.pack('i', self.c_delivery_duration)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.ammos
		tmp14 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp14:
			tmp15 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp16 = s[offset:offset + tmp15]
			offset += tmp15
			tmp16 += b'\x00' * (4 - tmp15)
			tmp17 = struct.unpack('I', tmp16)[0]
			
			self.ammos = {}
			for tmp18 in range(tmp17):
				tmp21 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp21:
					tmp22 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp19 = AmmoType(tmp22)
				else:
					tmp19 = None
				tmp23 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp23:
					tmp20 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp20 = None
				self.ammos[tmp19] = tmp20
		else:
			self.ammos = None
		
		# deserialize self.delivery_rem_time
		tmp24 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp24:
			self.delivery_rem_time = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.delivery_rem_time = None
		
		# deserialize self.c_delivery_duration
		tmp25 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp25:
			self.c_delivery_duration = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_delivery_duration = None
		
		return offset


class Warehouse(object):

	@staticmethod
	def name():
		return 'Warehouse'


	def __init__(self, materials=None, materials_reload_rem_time=None, c_materials_reload_duration=None):
		self.initialize(materials, materials_reload_rem_time, c_materials_reload_duration)
	

	def initialize(self, materials=None, materials_reload_rem_time=None, c_materials_reload_duration=None):
		self.materials = materials
		self.materials_reload_rem_time = materials_reload_rem_time
		self.c_materials_reload_duration = c_materials_reload_duration
	

	def serialize(self):
		s = b''
		
		# serialize self.materials
		s += b'\x00' if self.materials is None else b'\x01'
		if self.materials is not None:
			tmp26 = b''
			tmp26 += struct.pack('I', len(self.materials))
			while len(tmp26) and tmp26[-1] == b'\x00'[0]:
				tmp26 = tmp26[:-1]
			s += struct.pack('B', len(tmp26))
			s += tmp26
			
			for tmp27 in self.materials:
				s += b'\x00' if tmp27 is None else b'\x01'
				if tmp27 is not None:
					s += tmp27.serialize()
				s += b'\x00' if self.materials[tmp27] is None else b'\x01'
				if self.materials[tmp27] is not None:
					s += self.materials[tmp27].serialize()
		
		# serialize self.materials_reload_rem_time
		s += b'\x00' if self.materials_reload_rem_time is None else b'\x01'
		if self.materials_reload_rem_time is not None:
			s += struct.pack('i', self.materials_reload_rem_time)
		
		# serialize self.c_materials_reload_duration
		s += b'\x00' if self.c_materials_reload_duration is None else b'\x01'
		if self.c_materials_reload_duration is not None:
			s += struct.pack('i', self.c_materials_reload_duration)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.materials
		tmp28 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp28:
			tmp29 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp30 = s[offset:offset + tmp29]
			offset += tmp29
			tmp30 += b'\x00' * (4 - tmp29)
			tmp31 = struct.unpack('I', tmp30)[0]
			
			self.materials = {}
			for tmp32 in range(tmp31):
				tmp35 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp35:
					tmp33 = Position()
					offset = tmp33.deserialize(s, offset)
				else:
					tmp33 = None
				tmp36 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp36:
					tmp34 = Material()
					offset = tmp34.deserialize(s, offset)
				else:
					tmp34 = None
				self.materials[tmp33] = tmp34
		else:
			self.materials = None
		
		# deserialize self.materials_reload_rem_time
		tmp37 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp37:
			self.materials_reload_rem_time = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.materials_reload_rem_time = None
		
		# deserialize self.c_materials_reload_duration
		tmp38 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp38:
			self.c_materials_reload_duration = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_materials_reload_duration = None
		
		return offset


class BacklineDelivery(object):

	@staticmethod
	def name():
		return 'BacklineDelivery'


	def __init__(self, materials=None, ammos=None):
		self.initialize(materials, ammos)
	

	def initialize(self, materials=None, ammos=None):
		self.materials = materials
		self.ammos = ammos
	

	def serialize(self):
		s = b''
		
		# serialize self.materials
		s += b'\x00' if self.materials is None else b'\x01'
		if self.materials is not None:
			tmp39 = b''
			tmp39 += struct.pack('I', len(self.materials))
			while len(tmp39) and tmp39[-1] == b'\x00'[0]:
				tmp39 = tmp39[:-1]
			s += struct.pack('B', len(tmp39))
			s += tmp39
			
			for tmp40 in self.materials:
				s += b'\x00' if tmp40 is None else b'\x01'
				if tmp40 is not None:
					s += struct.pack('b', tmp40.value)
				s += b'\x00' if self.materials[tmp40] is None else b'\x01'
				if self.materials[tmp40] is not None:
					s += struct.pack('i', self.materials[tmp40])
		
		# serialize self.ammos
		s += b'\x00' if self.ammos is None else b'\x01'
		if self.ammos is not None:
			tmp41 = b''
			tmp41 += struct.pack('I', len(self.ammos))
			while len(tmp41) and tmp41[-1] == b'\x00'[0]:
				tmp41 = tmp41[:-1]
			s += struct.pack('B', len(tmp41))
			s += tmp41
			
			for tmp42 in self.ammos:
				s += b'\x00' if tmp42 is None else b'\x01'
				if tmp42 is not None:
					s += struct.pack('b', tmp42.value)
				s += b'\x00' if self.ammos[tmp42] is None else b'\x01'
				if self.ammos[tmp42] is not None:
					s += struct.pack('i', self.ammos[tmp42])
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.materials
		tmp43 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp43:
			tmp44 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp45 = s[offset:offset + tmp44]
			offset += tmp44
			tmp45 += b'\x00' * (4 - tmp44)
			tmp46 = struct.unpack('I', tmp45)[0]
			
			self.materials = {}
			for tmp47 in range(tmp46):
				tmp50 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp50:
					tmp51 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp48 = MaterialType(tmp51)
				else:
					tmp48 = None
				tmp52 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp52:
					tmp49 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp49 = None
				self.materials[tmp48] = tmp49
		else:
			self.materials = None
		
		# deserialize self.ammos
		tmp53 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp53:
			tmp54 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp55 = s[offset:offset + tmp54]
			offset += tmp54
			tmp55 += b'\x00' * (4 - tmp54)
			tmp56 = struct.unpack('I', tmp55)[0]
			
			self.ammos = {}
			for tmp57 in range(tmp56):
				tmp60 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp60:
					tmp61 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp58 = AmmoType(tmp61)
				else:
					tmp58 = None
				tmp62 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp62:
					tmp59 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp59 = None
				self.ammos[tmp58] = tmp59
		else:
			self.ammos = None
		
		return offset


class Factory(object):

	@staticmethod
	def name():
		return 'Factory'


	def __init__(self, machines=None, c_mixture_formulas=None, c_construction_durations=None, c_ammo_box_sizes=None):
		self.initialize(machines, c_mixture_formulas, c_construction_durations, c_ammo_box_sizes)
	

	def initialize(self, machines=None, c_mixture_formulas=None, c_construction_durations=None, c_ammo_box_sizes=None):
		self.machines = machines
		self.c_mixture_formulas = c_mixture_formulas
		self.c_construction_durations = c_construction_durations
		self.c_ammo_box_sizes = c_ammo_box_sizes
	

	def serialize(self):
		s = b''
		
		# serialize self.machines
		s += b'\x00' if self.machines is None else b'\x01'
		if self.machines is not None:
			tmp63 = b''
			tmp63 += struct.pack('I', len(self.machines))
			while len(tmp63) and tmp63[-1] == b'\x00'[0]:
				tmp63 = tmp63[:-1]
			s += struct.pack('B', len(tmp63))
			s += tmp63
			
			for tmp64 in self.machines:
				s += b'\x00' if tmp64 is None else b'\x01'
				if tmp64 is not None:
					s += tmp64.serialize()
				s += b'\x00' if self.machines[tmp64] is None else b'\x01'
				if self.machines[tmp64] is not None:
					s += self.machines[tmp64].serialize()
		
		# serialize self.c_mixture_formulas
		s += b'\x00' if self.c_mixture_formulas is None else b'\x01'
		if self.c_mixture_formulas is not None:
			tmp65 = b''
			tmp65 += struct.pack('I', len(self.c_mixture_formulas))
			while len(tmp65) and tmp65[-1] == b'\x00'[0]:
				tmp65 = tmp65[:-1]
			s += struct.pack('B', len(tmp65))
			s += tmp65
			
			for tmp66 in self.c_mixture_formulas:
				s += b'\x00' if tmp66 is None else b'\x01'
				if tmp66 is not None:
					s += struct.pack('b', tmp66.value)
				s += b'\x00' if self.c_mixture_formulas[tmp66] is None else b'\x01'
				if self.c_mixture_formulas[tmp66] is not None:
					tmp67 = b''
					tmp67 += struct.pack('I', len(self.c_mixture_formulas[tmp66]))
					while len(tmp67) and tmp67[-1] == b'\x00'[0]:
						tmp67 = tmp67[:-1]
					s += struct.pack('B', len(tmp67))
					s += tmp67
					
					for tmp68 in self.c_mixture_formulas[tmp66]:
						s += b'\x00' if tmp68 is None else b'\x01'
						if tmp68 is not None:
							s += struct.pack('b', tmp68.value)
						s += b'\x00' if self.c_mixture_formulas[tmp66][tmp68] is None else b'\x01'
						if self.c_mixture_formulas[tmp66][tmp68] is not None:
							s += struct.pack('i', self.c_mixture_formulas[tmp66][tmp68])
		
		# serialize self.c_construction_durations
		s += b'\x00' if self.c_construction_durations is None else b'\x01'
		if self.c_construction_durations is not None:
			tmp69 = b''
			tmp69 += struct.pack('I', len(self.c_construction_durations))
			while len(tmp69) and tmp69[-1] == b'\x00'[0]:
				tmp69 = tmp69[:-1]
			s += struct.pack('B', len(tmp69))
			s += tmp69
			
			for tmp70 in self.c_construction_durations:
				s += b'\x00' if tmp70 is None else b'\x01'
				if tmp70 is not None:
					s += struct.pack('b', tmp70.value)
				s += b'\x00' if self.c_construction_durations[tmp70] is None else b'\x01'
				if self.c_construction_durations[tmp70] is not None:
					s += struct.pack('i', self.c_construction_durations[tmp70])
		
		# serialize self.c_ammo_box_sizes
		s += b'\x00' if self.c_ammo_box_sizes is None else b'\x01'
		if self.c_ammo_box_sizes is not None:
			tmp71 = b''
			tmp71 += struct.pack('I', len(self.c_ammo_box_sizes))
			while len(tmp71) and tmp71[-1] == b'\x00'[0]:
				tmp71 = tmp71[:-1]
			s += struct.pack('B', len(tmp71))
			s += tmp71
			
			for tmp72 in self.c_ammo_box_sizes:
				s += b'\x00' if tmp72 is None else b'\x01'
				if tmp72 is not None:
					s += struct.pack('b', tmp72.value)
				s += b'\x00' if self.c_ammo_box_sizes[tmp72] is None else b'\x01'
				if self.c_ammo_box_sizes[tmp72] is not None:
					s += struct.pack('i', self.c_ammo_box_sizes[tmp72])
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.machines
		tmp73 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp73:
			tmp74 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp75 = s[offset:offset + tmp74]
			offset += tmp74
			tmp75 += b'\x00' * (4 - tmp74)
			tmp76 = struct.unpack('I', tmp75)[0]
			
			self.machines = {}
			for tmp77 in range(tmp76):
				tmp80 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp80:
					tmp78 = Position()
					offset = tmp78.deserialize(s, offset)
				else:
					tmp78 = None
				tmp81 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp81:
					tmp79 = Machine()
					offset = tmp79.deserialize(s, offset)
				else:
					tmp79 = None
				self.machines[tmp78] = tmp79
		else:
			self.machines = None
		
		# deserialize self.c_mixture_formulas
		tmp82 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp82:
			tmp83 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp84 = s[offset:offset + tmp83]
			offset += tmp83
			tmp84 += b'\x00' * (4 - tmp83)
			tmp85 = struct.unpack('I', tmp84)[0]
			
			self.c_mixture_formulas = {}
			for tmp86 in range(tmp85):
				tmp89 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp89:
					tmp90 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp87 = AmmoType(tmp90)
				else:
					tmp87 = None
				tmp91 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp91:
					tmp92 = struct.unpack('B', s[offset:offset + 1])[0]
					offset += 1
					tmp93 = s[offset:offset + tmp92]
					offset += tmp92
					tmp93 += b'\x00' * (4 - tmp92)
					tmp94 = struct.unpack('I', tmp93)[0]
					
					tmp88 = {}
					for tmp95 in range(tmp94):
						tmp98 = struct.unpack('B', s[offset:offset + 1])[0]
						offset += 1
						if tmp98:
							tmp99 = struct.unpack('b', s[offset:offset + 1])[0]
							offset += 1
							tmp96 = MaterialType(tmp99)
						else:
							tmp96 = None
						tmp100 = struct.unpack('B', s[offset:offset + 1])[0]
						offset += 1
						if tmp100:
							tmp97 = struct.unpack('i', s[offset:offset + 4])[0]
							offset += 4
						else:
							tmp97 = None
						tmp88[tmp96] = tmp97
				else:
					tmp88 = None
				self.c_mixture_formulas[tmp87] = tmp88
		else:
			self.c_mixture_formulas = None
		
		# deserialize self.c_construction_durations
		tmp101 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp101:
			tmp102 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp103 = s[offset:offset + tmp102]
			offset += tmp102
			tmp103 += b'\x00' * (4 - tmp102)
			tmp104 = struct.unpack('I', tmp103)[0]
			
			self.c_construction_durations = {}
			for tmp105 in range(tmp104):
				tmp108 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp108:
					tmp109 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp106 = AmmoType(tmp109)
				else:
					tmp106 = None
				tmp110 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp110:
					tmp107 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp107 = None
				self.c_construction_durations[tmp106] = tmp107
		else:
			self.c_construction_durations = None
		
		# deserialize self.c_ammo_box_sizes
		tmp111 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp111:
			tmp112 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp113 = s[offset:offset + tmp112]
			offset += tmp112
			tmp113 += b'\x00' * (4 - tmp112)
			tmp114 = struct.unpack('I', tmp113)[0]
			
			self.c_ammo_box_sizes = {}
			for tmp115 in range(tmp114):
				tmp118 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp118:
					tmp119 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp116 = AmmoType(tmp119)
				else:
					tmp116 = None
				tmp120 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp120:
					tmp117 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp117 = None
				self.c_ammo_box_sizes[tmp116] = tmp117
		else:
			self.c_ammo_box_sizes = None
		
		return offset


class Agent(object):

	@staticmethod
	def name():
		return 'Agent'


	def __init__(self, type=None, position=None, materials_bag=None, c_materials_bag_capacity=None, ammos_bag=None, c_ammos_bag_capacity=None):
		self.initialize(type, position, materials_bag, c_materials_bag_capacity, ammos_bag, c_ammos_bag_capacity)
	

	def initialize(self, type=None, position=None, materials_bag=None, c_materials_bag_capacity=None, ammos_bag=None, c_ammos_bag_capacity=None):
		self.type = type
		self.position = position
		self.materials_bag = materials_bag
		self.c_materials_bag_capacity = c_materials_bag_capacity
		self.ammos_bag = ammos_bag
		self.c_ammos_bag_capacity = c_ammos_bag_capacity
	

	def serialize(self):
		s = b''
		
		# serialize self.type
		s += b'\x00' if self.type is None else b'\x01'
		if self.type is not None:
			s += struct.pack('b', self.type.value)
		
		# serialize self.position
		s += b'\x00' if self.position is None else b'\x01'
		if self.position is not None:
			s += self.position.serialize()
		
		# serialize self.materials_bag
		s += b'\x00' if self.materials_bag is None else b'\x01'
		if self.materials_bag is not None:
			tmp121 = b''
			tmp121 += struct.pack('I', len(self.materials_bag))
			while len(tmp121) and tmp121[-1] == b'\x00'[0]:
				tmp121 = tmp121[:-1]
			s += struct.pack('B', len(tmp121))
			s += tmp121
			
			for tmp122 in self.materials_bag:
				s += b'\x00' if tmp122 is None else b'\x01'
				if tmp122 is not None:
					s += struct.pack('b', tmp122.value)
				s += b'\x00' if self.materials_bag[tmp122] is None else b'\x01'
				if self.materials_bag[tmp122] is not None:
					s += struct.pack('i', self.materials_bag[tmp122])
		
		# serialize self.c_materials_bag_capacity
		s += b'\x00' if self.c_materials_bag_capacity is None else b'\x01'
		if self.c_materials_bag_capacity is not None:
			s += struct.pack('i', self.c_materials_bag_capacity)
		
		# serialize self.ammos_bag
		s += b'\x00' if self.ammos_bag is None else b'\x01'
		if self.ammos_bag is not None:
			tmp123 = b''
			tmp123 += struct.pack('I', len(self.ammos_bag))
			while len(tmp123) and tmp123[-1] == b'\x00'[0]:
				tmp123 = tmp123[:-1]
			s += struct.pack('B', len(tmp123))
			s += tmp123
			
			for tmp124 in self.ammos_bag:
				s += b'\x00' if tmp124 is None else b'\x01'
				if tmp124 is not None:
					s += struct.pack('b', tmp124.value)
				s += b'\x00' if self.ammos_bag[tmp124] is None else b'\x01'
				if self.ammos_bag[tmp124] is not None:
					s += struct.pack('i', self.ammos_bag[tmp124])
		
		# serialize self.c_ammos_bag_capacity
		s += b'\x00' if self.c_ammos_bag_capacity is None else b'\x01'
		if self.c_ammos_bag_capacity is not None:
			s += struct.pack('i', self.c_ammos_bag_capacity)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.type
		tmp125 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp125:
			tmp126 = struct.unpack('b', s[offset:offset + 1])[0]
			offset += 1
			self.type = AgentType(tmp126)
		else:
			self.type = None
		
		# deserialize self.position
		tmp127 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp127:
			self.position = Position()
			offset = self.position.deserialize(s, offset)
		else:
			self.position = None
		
		# deserialize self.materials_bag
		tmp128 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp128:
			tmp129 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp130 = s[offset:offset + tmp129]
			offset += tmp129
			tmp130 += b'\x00' * (4 - tmp129)
			tmp131 = struct.unpack('I', tmp130)[0]
			
			self.materials_bag = {}
			for tmp132 in range(tmp131):
				tmp135 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp135:
					tmp136 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp133 = MaterialType(tmp136)
				else:
					tmp133 = None
				tmp137 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp137:
					tmp134 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp134 = None
				self.materials_bag[tmp133] = tmp134
		else:
			self.materials_bag = None
		
		# deserialize self.c_materials_bag_capacity
		tmp138 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp138:
			self.c_materials_bag_capacity = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_materials_bag_capacity = None
		
		# deserialize self.ammos_bag
		tmp139 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp139:
			tmp140 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp141 = s[offset:offset + tmp140]
			offset += tmp140
			tmp141 += b'\x00' * (4 - tmp140)
			tmp142 = struct.unpack('I', tmp141)[0]
			
			self.ammos_bag = {}
			for tmp143 in range(tmp142):
				tmp146 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp146:
					tmp147 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp144 = AmmoType(tmp147)
				else:
					tmp144 = None
				tmp148 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp148:
					tmp145 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp145 = None
				self.ammos_bag[tmp144] = tmp145
		else:
			self.ammos_bag = None
		
		# deserialize self.c_ammos_bag_capacity
		tmp149 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp149:
			self.c_ammos_bag_capacity = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_ammos_bag_capacity = None
		
		return offset


class Unit(object):

	@staticmethod
	def name():
		return 'Unit'


	def __init__(self, type=None, health=None, c_individual_health=None, c_individual_damage=None, c_damage_distribution=None, ammo_count=None, reload_rem_time=None, c_reload_duration=None):
		self.initialize(type, health, c_individual_health, c_individual_damage, c_damage_distribution, ammo_count, reload_rem_time, c_reload_duration)
	

	def initialize(self, type=None, health=None, c_individual_health=None, c_individual_damage=None, c_damage_distribution=None, ammo_count=None, reload_rem_time=None, c_reload_duration=None):
		self.type = type
		self.health = health
		self.c_individual_health = c_individual_health
		self.c_individual_damage = c_individual_damage
		self.c_damage_distribution = c_damage_distribution
		self.ammo_count = ammo_count
		self.reload_rem_time = reload_rem_time
		self.c_reload_duration = c_reload_duration
	

	def serialize(self):
		s = b''
		
		# serialize self.type
		s += b'\x00' if self.type is None else b'\x01'
		if self.type is not None:
			s += struct.pack('b', self.type.value)
		
		# serialize self.health
		s += b'\x00' if self.health is None else b'\x01'
		if self.health is not None:
			s += struct.pack('i', self.health)
		
		# serialize self.c_individual_health
		s += b'\x00' if self.c_individual_health is None else b'\x01'
		if self.c_individual_health is not None:
			s += struct.pack('i', self.c_individual_health)
		
		# serialize self.c_individual_damage
		s += b'\x00' if self.c_individual_damage is None else b'\x01'
		if self.c_individual_damage is not None:
			s += struct.pack('i', self.c_individual_damage)
		
		# serialize self.c_damage_distribution
		s += b'\x00' if self.c_damage_distribution is None else b'\x01'
		if self.c_damage_distribution is not None:
			tmp150 = b''
			tmp150 += struct.pack('I', len(self.c_damage_distribution))
			while len(tmp150) and tmp150[-1] == b'\x00'[0]:
				tmp150 = tmp150[:-1]
			s += struct.pack('B', len(tmp150))
			s += tmp150
			
			for tmp151 in self.c_damage_distribution:
				s += b'\x00' if tmp151 is None else b'\x01'
				if tmp151 is not None:
					s += struct.pack('b', tmp151.value)
				s += b'\x00' if self.c_damage_distribution[tmp151] is None else b'\x01'
				if self.c_damage_distribution[tmp151] is not None:
					s += struct.pack('f', self.c_damage_distribution[tmp151])
		
		# serialize self.ammo_count
		s += b'\x00' if self.ammo_count is None else b'\x01'
		if self.ammo_count is not None:
			s += struct.pack('i', self.ammo_count)
		
		# serialize self.reload_rem_time
		s += b'\x00' if self.reload_rem_time is None else b'\x01'
		if self.reload_rem_time is not None:
			s += struct.pack('i', self.reload_rem_time)
		
		# serialize self.c_reload_duration
		s += b'\x00' if self.c_reload_duration is None else b'\x01'
		if self.c_reload_duration is not None:
			s += struct.pack('i', self.c_reload_duration)
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.type
		tmp152 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp152:
			tmp153 = struct.unpack('b', s[offset:offset + 1])[0]
			offset += 1
			self.type = UnitType(tmp153)
		else:
			self.type = None
		
		# deserialize self.health
		tmp154 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp154:
			self.health = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.health = None
		
		# deserialize self.c_individual_health
		tmp155 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp155:
			self.c_individual_health = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_individual_health = None
		
		# deserialize self.c_individual_damage
		tmp156 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp156:
			self.c_individual_damage = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_individual_damage = None
		
		# deserialize self.c_damage_distribution
		tmp157 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp157:
			tmp158 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp159 = s[offset:offset + tmp158]
			offset += tmp158
			tmp159 += b'\x00' * (4 - tmp158)
			tmp160 = struct.unpack('I', tmp159)[0]
			
			self.c_damage_distribution = {}
			for tmp161 in range(tmp160):
				tmp164 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp164:
					tmp165 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp162 = UnitType(tmp165)
				else:
					tmp162 = None
				tmp166 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp166:
					tmp163 = struct.unpack('f', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp163 = None
				self.c_damage_distribution[tmp162] = tmp163
		else:
			self.c_damage_distribution = None
		
		# deserialize self.ammo_count
		tmp167 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp167:
			self.ammo_count = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.ammo_count = None
		
		# deserialize self.reload_rem_time
		tmp168 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp168:
			self.reload_rem_time = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.reload_rem_time = None
		
		# deserialize self.c_reload_duration
		tmp169 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp169:
			self.c_reload_duration = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.c_reload_duration = None
		
		return offset


class Base(object):

	@staticmethod
	def name():
		return 'Base'


	def __init__(self, c_area=None, agents=None, frontline_deliveries=None, warehouse=None, backline_delivery=None, factory=None, units=None):
		self.initialize(c_area, agents, frontline_deliveries, warehouse, backline_delivery, factory, units)
	

	def initialize(self, c_area=None, agents=None, frontline_deliveries=None, warehouse=None, backline_delivery=None, factory=None, units=None):
		self.c_area = c_area
		self.agents = agents
		self.frontline_deliveries = frontline_deliveries
		self.warehouse = warehouse
		self.backline_delivery = backline_delivery
		self.factory = factory
		self.units = units
	

	def serialize(self):
		s = b''
		
		# serialize self.c_area
		s += b'\x00' if self.c_area is None else b'\x01'
		if self.c_area is not None:
			tmp170 = b''
			tmp170 += struct.pack('I', len(self.c_area))
			while len(tmp170) and tmp170[-1] == b'\x00'[0]:
				tmp170 = tmp170[:-1]
			s += struct.pack('B', len(tmp170))
			s += tmp170
			
			for tmp171 in self.c_area:
				s += b'\x00' if tmp171 is None else b'\x01'
				if tmp171 is not None:
					s += tmp171.serialize()
				s += b'\x00' if self.c_area[tmp171] is None else b'\x01'
				if self.c_area[tmp171] is not None:
					s += struct.pack('b', self.c_area[tmp171].value)
		
		# serialize self.agents
		s += b'\x00' if self.agents is None else b'\x01'
		if self.agents is not None:
			tmp172 = b''
			tmp172 += struct.pack('I', len(self.agents))
			while len(tmp172) and tmp172[-1] == b'\x00'[0]:
				tmp172 = tmp172[:-1]
			s += struct.pack('B', len(tmp172))
			s += tmp172
			
			for tmp173 in self.agents:
				s += b'\x00' if tmp173 is None else b'\x01'
				if tmp173 is not None:
					s += struct.pack('b', tmp173.value)
				s += b'\x00' if self.agents[tmp173] is None else b'\x01'
				if self.agents[tmp173] is not None:
					s += self.agents[tmp173].serialize()
		
		# serialize self.frontline_deliveries
		s += b'\x00' if self.frontline_deliveries is None else b'\x01'
		if self.frontline_deliveries is not None:
			tmp174 = b''
			tmp174 += struct.pack('I', len(self.frontline_deliveries))
			while len(tmp174) and tmp174[-1] == b'\x00'[0]:
				tmp174 = tmp174[:-1]
			s += struct.pack('B', len(tmp174))
			s += tmp174
			
			for tmp175 in self.frontline_deliveries:
				s += b'\x00' if tmp175 is None else b'\x01'
				if tmp175 is not None:
					s += tmp175.serialize()
		
		# serialize self.warehouse
		s += b'\x00' if self.warehouse is None else b'\x01'
		if self.warehouse is not None:
			s += self.warehouse.serialize()
		
		# serialize self.backline_delivery
		s += b'\x00' if self.backline_delivery is None else b'\x01'
		if self.backline_delivery is not None:
			s += self.backline_delivery.serialize()
		
		# serialize self.factory
		s += b'\x00' if self.factory is None else b'\x01'
		if self.factory is not None:
			s += self.factory.serialize()
		
		# serialize self.units
		s += b'\x00' if self.units is None else b'\x01'
		if self.units is not None:
			tmp176 = b''
			tmp176 += struct.pack('I', len(self.units))
			while len(tmp176) and tmp176[-1] == b'\x00'[0]:
				tmp176 = tmp176[:-1]
			s += struct.pack('B', len(tmp176))
			s += tmp176
			
			for tmp177 in self.units:
				s += b'\x00' if tmp177 is None else b'\x01'
				if tmp177 is not None:
					s += struct.pack('b', tmp177.value)
				s += b'\x00' if self.units[tmp177] is None else b'\x01'
				if self.units[tmp177] is not None:
					s += self.units[tmp177].serialize()
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.c_area
		tmp178 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp178:
			tmp179 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp180 = s[offset:offset + tmp179]
			offset += tmp179
			tmp180 += b'\x00' * (4 - tmp179)
			tmp181 = struct.unpack('I', tmp180)[0]
			
			self.c_area = {}
			for tmp182 in range(tmp181):
				tmp185 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp185:
					tmp183 = Position()
					offset = tmp183.deserialize(s, offset)
				else:
					tmp183 = None
				tmp186 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp186:
					tmp187 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp184 = ECell(tmp187)
				else:
					tmp184 = None
				self.c_area[tmp183] = tmp184
		else:
			self.c_area = None
		
		# deserialize self.agents
		tmp188 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp188:
			tmp189 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp190 = s[offset:offset + tmp189]
			offset += tmp189
			tmp190 += b'\x00' * (4 - tmp189)
			tmp191 = struct.unpack('I', tmp190)[0]
			
			self.agents = {}
			for tmp192 in range(tmp191):
				tmp195 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp195:
					tmp196 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp193 = AgentType(tmp196)
				else:
					tmp193 = None
				tmp197 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp197:
					tmp194 = Agent()
					offset = tmp194.deserialize(s, offset)
				else:
					tmp194 = None
				self.agents[tmp193] = tmp194
		else:
			self.agents = None
		
		# deserialize self.frontline_deliveries
		tmp198 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp198:
			tmp199 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp200 = s[offset:offset + tmp199]
			offset += tmp199
			tmp200 += b'\x00' * (4 - tmp199)
			tmp201 = struct.unpack('I', tmp200)[0]
			
			self.frontline_deliveries = []
			for tmp202 in range(tmp201):
				tmp204 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp204:
					tmp203 = FrontlineDelivery()
					offset = tmp203.deserialize(s, offset)
				else:
					tmp203 = None
				self.frontline_deliveries.append(tmp203)
		else:
			self.frontline_deliveries = None
		
		# deserialize self.warehouse
		tmp205 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp205:
			self.warehouse = Warehouse()
			offset = self.warehouse.deserialize(s, offset)
		else:
			self.warehouse = None
		
		# deserialize self.backline_delivery
		tmp206 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp206:
			self.backline_delivery = BacklineDelivery()
			offset = self.backline_delivery.deserialize(s, offset)
		else:
			self.backline_delivery = None
		
		# deserialize self.factory
		tmp207 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp207:
			self.factory = Factory()
			offset = self.factory.deserialize(s, offset)
		else:
			self.factory = None
		
		# deserialize self.units
		tmp208 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp208:
			tmp209 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp210 = s[offset:offset + tmp209]
			offset += tmp209
			tmp210 += b'\x00' * (4 - tmp209)
			tmp211 = struct.unpack('I', tmp210)[0]
			
			self.units = {}
			for tmp212 in range(tmp211):
				tmp215 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp215:
					tmp216 = struct.unpack('b', s[offset:offset + 1])[0]
					offset += 1
					tmp213 = UnitType(tmp216)
				else:
					tmp213 = None
				tmp217 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp217:
					tmp214 = Unit()
					offset = tmp214.deserialize(s, offset)
				else:
					tmp214 = None
				self.units[tmp213] = tmp214
		else:
			self.units = None
		
		return offset


class World(object):

	@staticmethod
	def name():
		return 'World'


	def __init__(self, max_cycles=None, bases=None, total_healths=None):
		self.initialize(max_cycles, bases, total_healths)
	

	def initialize(self, max_cycles=None, bases=None, total_healths=None):
		self.max_cycles = max_cycles
		self.bases = bases
		self.total_healths = total_healths
	

	def serialize(self):
		s = b''
		
		# serialize self.max_cycles
		s += b'\x00' if self.max_cycles is None else b'\x01'
		if self.max_cycles is not None:
			s += struct.pack('i', self.max_cycles)
		
		# serialize self.bases
		s += b'\x00' if self.bases is None else b'\x01'
		if self.bases is not None:
			tmp218 = b''
			tmp218 += struct.pack('I', len(self.bases))
			while len(tmp218) and tmp218[-1] == b'\x00'[0]:
				tmp218 = tmp218[:-1]
			s += struct.pack('B', len(tmp218))
			s += tmp218
			
			for tmp219 in self.bases:
				s += b'\x00' if tmp219 is None else b'\x01'
				if tmp219 is not None:
					tmp220 = b''
					tmp220 += struct.pack('I', len(tmp219))
					while len(tmp220) and tmp220[-1] == b'\x00'[0]:
						tmp220 = tmp220[:-1]
					s += struct.pack('B', len(tmp220))
					s += tmp220
					
					s += tmp219.encode('ISO-8859-1') if PY3 else tmp219
				s += b'\x00' if self.bases[tmp219] is None else b'\x01'
				if self.bases[tmp219] is not None:
					s += self.bases[tmp219].serialize()
		
		# serialize self.total_healths
		s += b'\x00' if self.total_healths is None else b'\x01'
		if self.total_healths is not None:
			tmp221 = b''
			tmp221 += struct.pack('I', len(self.total_healths))
			while len(tmp221) and tmp221[-1] == b'\x00'[0]:
				tmp221 = tmp221[:-1]
			s += struct.pack('B', len(tmp221))
			s += tmp221
			
			for tmp222 in self.total_healths:
				s += b'\x00' if tmp222 is None else b'\x01'
				if tmp222 is not None:
					tmp223 = b''
					tmp223 += struct.pack('I', len(tmp222))
					while len(tmp223) and tmp223[-1] == b'\x00'[0]:
						tmp223 = tmp223[:-1]
					s += struct.pack('B', len(tmp223))
					s += tmp223
					
					s += tmp222.encode('ISO-8859-1') if PY3 else tmp222
				s += b'\x00' if self.total_healths[tmp222] is None else b'\x01'
				if self.total_healths[tmp222] is not None:
					s += struct.pack('i', self.total_healths[tmp222])
		
		return s
	

	def deserialize(self, s, offset=0):
		# deserialize self.max_cycles
		tmp224 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp224:
			self.max_cycles = struct.unpack('i', s[offset:offset + 4])[0]
			offset += 4
		else:
			self.max_cycles = None
		
		# deserialize self.bases
		tmp225 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp225:
			tmp226 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp227 = s[offset:offset + tmp226]
			offset += tmp226
			tmp227 += b'\x00' * (4 - tmp226)
			tmp228 = struct.unpack('I', tmp227)[0]
			
			self.bases = {}
			for tmp229 in range(tmp228):
				tmp232 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp232:
					tmp233 = struct.unpack('B', s[offset:offset + 1])[0]
					offset += 1
					tmp234 = s[offset:offset + tmp233]
					offset += tmp233
					tmp234 += b'\x00' * (4 - tmp233)
					tmp235 = struct.unpack('I', tmp234)[0]
					
					tmp230 = s[offset:offset + tmp235].decode('ISO-8859-1') if PY3 else s[offset:offset + tmp235]
					offset += tmp235
				else:
					tmp230 = None
				tmp236 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp236:
					tmp231 = Base()
					offset = tmp231.deserialize(s, offset)
				else:
					tmp231 = None
				self.bases[tmp230] = tmp231
		else:
			self.bases = None
		
		# deserialize self.total_healths
		tmp237 = struct.unpack('B', s[offset:offset + 1])[0]
		offset += 1
		if tmp237:
			tmp238 = struct.unpack('B', s[offset:offset + 1])[0]
			offset += 1
			tmp239 = s[offset:offset + tmp238]
			offset += tmp238
			tmp239 += b'\x00' * (4 - tmp238)
			tmp240 = struct.unpack('I', tmp239)[0]
			
			self.total_healths = {}
			for tmp241 in range(tmp240):
				tmp244 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp244:
					tmp245 = struct.unpack('B', s[offset:offset + 1])[0]
					offset += 1
					tmp246 = s[offset:offset + tmp245]
					offset += tmp245
					tmp246 += b'\x00' * (4 - tmp245)
					tmp247 = struct.unpack('I', tmp246)[0]
					
					tmp242 = s[offset:offset + tmp247].decode('ISO-8859-1') if PY3 else s[offset:offset + tmp247]
					offset += tmp247
				else:
					tmp242 = None
				tmp248 = struct.unpack('B', s[offset:offset + 1])[0]
				offset += 1
				if tmp248:
					tmp243 = struct.unpack('i', s[offset:offset + 4])[0]
					offset += 4
				else:
					tmp243 = None
				self.total_healths[tmp242] = tmp243
		else:
			self.total_healths = None
		
		return offset
