import sublime
import unittest
from unittest.mock import patch, MagicMock

from javatar.commands.javatar_create import (
    get_info,
    JavatarCreateCommand
)

side_effect = sublime.load_settings(
    "Javatar.sublime-settings"
).get


@patch('javatar.utils.javatar_utils.get_settings', side_effect=side_effect)
@patch('javatar.utils.javatar_java.get_settings', side_effect=side_effect)
@patch('javatar.commands.javatar_create.make_package')
@patch('javatar.commands.javatar_create.is_project', return_value=True)
@patch('javatar.commands.javatar_create.is_file', return_value=True)
class TestCreateGetInfo(unittest.TestCase):
    def test_private_visibility(self, *_):
        q = get_info('~here.privateBattleShip')

        self.assertEqual(
            'BattleShip',
            q['class']
        )

        self.assertEqual(
            'private',
            q['visibility_keyword']
        )

    def test_protected_visibility(self, *_):
        q = get_info('~here.protectedAbstractBattleShip')

        self.assertEqual('BattleShip', q['class'])
        self.assertEqual('abstract', q['modifier_keyword'])
        self.assertEqual('protected', q['visibility_keyword'])

    def test_default_with_package(self, *_):
        q = get_info('~wargame.entity.defaultBattleShip')

        self.assertEqual('BattleShip', q['class'])
        self.assertEqual('wargame.entity', q['package'])
        self.assertEqual('default', q['visibility_keyword'])

    def test_basic_extends(self, *_):
        q = get_info('~here.BattleShip:BattleUnit')

        self.assertEqual(['BattleUnit'], q['extends'])

    def test_basic_interface(self, *_):
        q = get_info('~here.BattleShip:BattleUnit<WaterUnit')

        self.assertEqual(['BattleUnit'], q['extends'])
        self.assertEqual(['WaterUnit'], q['implements'])

    def test_extended_interface(self, *_):
        q = get_info('~here.BattleShip<Carrier,WaterUnit:BattleUnit')

        self.assertEqual(['BattleUnit'], q['extends'])
        self.assertEqual(['Carrier', 'WaterUnit'], q['implements'])

    def test_extended_case(self, *_):
        q = get_info(
            '~wargame.entity.defaultAbstractBattleShip'
            ':BattleUnit<Carrier,WaterUnit'
        )

        self.assertEqual('abstract', q['modifier_keyword'])
        self.assertEqual('BattleShip', q['class'])
        self.assertEqual('wargame.entity', q['package'])
        self.assertEqual('default', q['visibility_keyword'])
        self.assertEqual(['BattleUnit'], q['extends'])
        self.assertEqual(['Carrier', 'WaterUnit'], q['implements'])


class TestCreateMisc(unittest.TestCase):
    def test_build_prefix(self):

        window = MagicMock(spec=sublime.Window)
        inst = JavatarCreateCommand(window)
        inst.create_type = 'Class'

        self.assertEqual(
            inst.build_prefix({
                'visibility_keyword': 'private',
                'modifier_keyword': 'abstract',
                'asmain': True
            }),
            'Private abstract main class'
        )

    def test_build_additional_text(self):
        window = MagicMock(spec=sublime.Window)
        inst = JavatarCreateCommand(window)
        inst.create_type = 'Class'

        self.assertEqual(
            inst.build_additional_text({
                'extends': ['Hello', 'World'],
                'implements': ['Hello', 'World']
            }),
            ', extends "Hello", "World", implements "Hello", "World" '
            '[Warning! Class can be extent only once]'
        )

        self.assertEqual(
            inst.build_additional_text({
                'extends': ['Hello', 'World', 'String'],
                'implements': ['Hello', 'World', 'String']
            }),
            ', extends "Hello", "World" and 1 more classes'
            ', implements "Hello", "World" and 1 more classes '
            '[Warning! Class can be extent only once]'
        )

    def test_build_additional_text_enumerator(self):
        window = MagicMock(spec=sublime.Window)
        inst = JavatarCreateCommand(window)
        inst.create_type = 'Enumerator'

        self.assertEqual(
            inst.build_additional_text({
                'extends': ['World'],
                'implements': []
            }),
            ', extends "World" '
            '[Warning! Enumerator use "implements" instead of "extends"]'
        )

    def test_build_additional_text_interface(self):
        window = MagicMock(spec=sublime.Window)
        inst = JavatarCreateCommand(window)
        inst.create_type = 'Interface'

        self.assertEqual(
            inst.build_additional_text({
                'extends': [],
                'implements': ['World']
            }),
            ', implements "World" '
            '[Warning! Interface use "extends" instead of "implements"]'
        )
