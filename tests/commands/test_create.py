import sublime
import unittest
from unittest.mock import patch

from javatar.commands.javatar_create import get_info

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
