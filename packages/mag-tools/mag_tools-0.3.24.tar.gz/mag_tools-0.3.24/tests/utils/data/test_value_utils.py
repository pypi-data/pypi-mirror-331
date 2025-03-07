import unittest

from mag_tools.utils.data.value_utils import ValueUtils


class TestValueUtils(unittest.TestCase):
    def test_to_value(self):
        print(ValueUtils.to_value('12.50', float))

        # 测试整数转换
        self.assertEqual(ValueUtils.to_value("123", int), 123)
        # 测试浮点数转换
        self.assertEqual(ValueUtils.to_value("123.45", float), 123.45)
        # 测试布尔值转换
        self.assertTrue(ValueUtils.to_value("true", bool))
        self.assertFalse(ValueUtils.to_value("false", bool))
        # 测试列表转换
        self.assertEqual(ValueUtils.to_value("[1, 2, 3]", list), [1, 2, 3])
        # 测试字典转换
        self.assertEqual(ValueUtils.to_value("{'key': 'value'}", dict), {'key': 'value'})
        # 测试默认类型转换
        self.assertEqual(ValueUtils.to_value("text"), "text")

    def test_number_to_scientific(self):
        print(ValueUtils.number_to_scientific(123.50, 3))

        # 测试默认小数位数
        self.assertEqual(ValueUtils.number_to_scientific(1000000000.0), "1.000000e9")
        self.assertEqual(ValueUtils.number_to_scientific(0.000123), "1.230000e-4")

        # 测试指定小数位数
        self.assertEqual(ValueUtils.number_to_scientific(1000000000.0, 5), "1.00000e9")
        self.assertEqual(ValueUtils.number_to_scientific(0.000123, 3), "1.230e-4")

        # 测试负数
        self.assertEqual(ValueUtils.number_to_scientific(-1000000000.0), "-1.000000e9")
        self.assertEqual(ValueUtils.number_to_scientific(-0.000123), "-1.230000e-4")

        # 测试小数位数不足时补零
        self.assertEqual(ValueUtils.number_to_scientific(1.23, 5), "1.23000e0")
        self.assertEqual(ValueUtils.number_to_scientific(1.0, 5), "1.00000e0")

    def test_to_string(self):
        print(ValueUtils.to_string(125000, 6, 3))

        # 测试浮点数格式化
        self.assertEqual(ValueUtils.to_string(123.456, 2), "123.46")
        self.assertEqual(ValueUtils.to_string(123.0, 2, 2), "123.00")
        # 测试科学计数法格式化
        self.assertEqual(ValueUtils.to_string(1e9, 6, 1,True), "1.000000e9")
        # 测试整数格式化
        self.assertEqual(ValueUtils.to_string(123), "123")