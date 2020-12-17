from unittest import TestCase

import archinfo

from angr.knowledge_plugins.key_definitions.atoms import Register, SpOffset
from angr.knowledge_plugins.key_definitions.dataset import DataSet
from angr.knowledge_plugins.key_definitions.live_definitions import LiveDefinitions


class TestLiveDefinitions(TestCase):
    def setUp(self):
        self.arch = archinfo.arch_arm.ArchARM()

        sp_offset = self.arch.registers['sp'][0]
        self.sp_register = Register(sp_offset, self.arch.bytes)

    def test_get_sp_retrieves_the_value_of_sp_register(self):
        address = SpOffset(self.arch.bits, 0)
        sp_value = DataSet({address}, self.arch.bits)

        live_definitions = LiveDefinitions(self.arch)
        live_definitions.kill_and_add_definition(self.sp_register, None, sp_value)

        retrieved_sp_value = live_definitions.get_sp()

        self.assertEqual(retrieved_sp_value, address)

    def test_get_sp_fails_if_there_are_different_definitions_for_sp_with_different_values(self):
        address = SpOffset(self.arch.bits, 0)
        sp_value = DataSet({address}, self.arch.bits)
        other_address = SpOffset(self.arch.bits, 20)
        other_sp_value = DataSet({other_address}, self.arch.bits)

        # To get multiple definitions of SP cohabiting, we need to create a `LiveDefinitions` via `.merge`:
        # Let's create the "base" `LiveDefinitions`, holding *DIFFERENT* values.
        live_definitions = LiveDefinitions(self.arch)
        live_definitions.kill_and_add_definition(self.sp_register, 0x0, sp_value)
        other_live_definitions = LiveDefinitions(self.arch)
        other_live_definitions.kill_and_add_definition(self.sp_register, 0x1, other_sp_value)
        # Then merge them.
        live_definitions_with_multiple_sps = live_definitions.merge(other_live_definitions)

        self.assertRaises(AssertionError, live_definitions_with_multiple_sps.get_sp)


    def test_get_sp_retrieves_the_value_of_sp_register_even_if_it_has_several_definitions(self):
        address = SpOffset(self.arch.bits, 0)
        sp_value = DataSet({address}, self.arch.bits)

        # To get multiple definitions of SP cohabiting, we need to create a `LiveDefinitions` via `.merge`:
        # Let's create the "base" `LiveDefinitions`, holding *THE SAME* values.
        live_definitions = LiveDefinitions(self.arch)
        live_definitions.kill_and_add_definition(self.sp_register, 0x1, sp_value)
        other_live_definitions = LiveDefinitions(self.arch)
        other_live_definitions.kill_and_add_definition(self.sp_register, 0x2, sp_value)
        # Then merge them.
        live_definitions_with_multiple_sps = live_definitions.merge(other_live_definitions)

        retrieved_sp_value = live_definitions_with_multiple_sps.get_sp()

        self.assertEqual(retrieved_sp_value, address)