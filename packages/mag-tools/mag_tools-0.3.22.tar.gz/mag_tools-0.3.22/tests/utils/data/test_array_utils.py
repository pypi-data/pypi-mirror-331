import unittest


from mag_tools.utils.data.array_utils import ArrayUtils


class TestArrayUtils(unittest.TestCase):

    def test_text_to_array_1d(self):
        # 测试整数数组
        text = "1 2 3 4*2"
        expected_output = [1, 2, 3, 2, 2, 2, 2]
        result = ArrayUtils.text_to_array_1d(text, int)
        self.assertEqual(result, expected_output)

        # 测试浮点数数组
        text = "1.1 2.2 3.3 2*4.4"
        expected_output = [1.1, 2.2, 3.3, 4.4, 4.4]
        result = ArrayUtils.text_to_array_1d(text, float)
        self.assertEqual(result, expected_output)

        # 测试布尔值数组
        text = "true false 2*true"
        expected_output = [True, False, True, True]
        result = ArrayUtils.text_to_array_1d(text, bool)
        self.assertEqual(result, expected_output)

        # 测试字符串数组
        text = "a b c 2*d"
        expected_output = ["a", "b", "c", "d", "d"]
        result = ArrayUtils.text_to_array_1d(text, str)
        self.assertEqual(result, expected_output)

        # 测试字符型数组
        text = "1 2.2 true 2*a"
        expected_output = ["1", "2.2", "true", "a", "a"]
        result = ArrayUtils.text_to_array_1d(text, str)
        self.assertEqual(result, expected_output)

    def test_lines_to_array_1d(self):
        # 测试整数数组
        lines = [
            "1 2 3",
            "4 5 6",
            "7 8 9"
        ]
        expected_output = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = ArrayUtils.lines_to_array_1d(lines, int)
        self.assertEqual(result, expected_output)

        # 测试浮点数数组
        lines = [
            "1.1 2.2 3.3",
            "4.4 5.5 6.6",
            "7.7 8.8 9.9"
        ]
        expected_output = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9]
        result = ArrayUtils.lines_to_array_1d(lines, float)
        self.assertEqual(result, expected_output)

        # 测试布尔值数组
        lines = [
            "true false true",
            "false true false"
        ]
        expected_output = [True, False, True, False, True, False]
        result = ArrayUtils.lines_to_array_1d(lines, bool)
        self.assertEqual(result, expected_output)

        # 测试字符串数组
        lines = [
            "a b c",
            "d e f",
            "g h i"
        ]
        expected_output = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        result = ArrayUtils.lines_to_array_1d(lines, str)
        self.assertEqual(result, expected_output)

        # 测试混合类型数组
        lines = [
            "1 2.2 true",
            "2*a"
        ]
        expected_output = ['1', '2.2', 'true', 'a', 'a']
        result = ArrayUtils.lines_to_array_1d(lines, str)
        self.assertEqual(expected_output, result)

    def test_lines_to_array_2d(self):
        # 测试整数数组
        lines = [
            "1 2 3",
            "4 5 6",
            "7 8 9"
        ]
        nx, ny = 3, 3
        expected_output = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        result = ArrayUtils.lines_to_array_2d(lines, nx, ny, int)
        self.assertEqual(result, expected_output)

        # 测试浮点数数组
        lines = [
            "1.1 2.2 3.3",
            "4.4 5.5 6.6",
            "7.7 8.8 9.9"
        ]
        nx, ny = 3, 3
        expected_output = [
            [1.1, 2.2, 3.3],
            [4.4, 5.5, 6.6],
            [7.7, 8.8, 9.9]
        ]
        result = ArrayUtils.lines_to_array_2d(lines, nx, ny, float)
        self.assertEqual(result, expected_output)

        # 测试布尔值数组
        lines = [
            "true false true",
            "false true false"
        ]
        nx, ny = 2, 3
        expected_output = [
            [True, False, True],
            [False, True, False]
        ]
        result = ArrayUtils.lines_to_array_2d(lines, nx, ny, bool)
        self.assertEqual(result, expected_output)

        # 测试字符串数组
        lines = [
            "a b c",
            "d e f",
            "g h i"
        ]
        nx, ny = 3, 3
        expected_output = [
            ["a", "b", "c"],
            ["d", "e", "f"],
            ["g", "h", "i"]
        ]
        result = ArrayUtils.lines_to_array_2d(lines, nx, ny, str)
        self.assertEqual(result, expected_output)

        # 测试混合类型数组
        lines = [
            "1 2.2 true",
            "2*a none"
        ]
        nx, ny = 2, 3
        expected_output = [
            ["1", "2.2", "true"],
            ["a", "a", 'none']  # 由于混合类型，最后一个值可能为 None
        ]
        result = ArrayUtils.lines_to_array_2d(lines, nx, ny, str)
        self.assertEqual(result, expected_output)

    def test_lines_to_array_3d(self):
        # 测试整数数组
        block_lines = [
            "1 2 3",
            "4 5 6",
            "7 8 9",
            "10 11 12",
            "13 14 15",
            "16 17 18"
        ]
        nx, ny, nz = 2, 3, 3
        expected_output = [
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ],
            [
                [10, 11, 12],
                [13, 14, 15],
                [16, 17, 18]
            ]
        ]
        result = ArrayUtils.lines_to_array_3d(block_lines, nx, ny, nz, int)
        self.assertEqual(expected_output, result)

        # 测试浮点数数组
        block_lines = [
            "1.1 2.2 3.3",
            "4.4 5.5 6.6",
            "7.7 8.8 9.9",
            "10.1 11.2 12.3",
            "13.4 14.5 15.6",
            "16.7 17.8 18.9"
        ]
        nx, ny, nz = 2, 3, 3
        expected_output = [
            [
                [1.1, 2.2, 3.3],
                [4.4, 5.5, 6.6],
                [7.7, 8.8, 9.9]
            ],
            [
                [10.1, 11.2, 12.3],
                [13.4, 14.5, 15.6],
                [16.7, 17.8, 18.9]
            ]
        ]
        result = ArrayUtils.lines_to_array_3d(block_lines, nx, ny, nz, float)
        self.assertEqual(expected_output, result)

        # 测试布尔值数组
        block_lines = [
            "true false true",
            "false true false",
            "true true false",
            "false false true",
            "true false true",
            "false true false"
        ]
        nx, ny, nz = 2, 3, 3
        expected_output = [
            [
                [True, False, True],
                [False, True, False],
                [True, True, False]
            ],
            [
                [False, False, True],
                [True, False, True],
                [False, True, False]
            ]
        ]
        result = ArrayUtils.lines_to_array_3d(block_lines, nx, ny, nz, bool)
        self.assertEqual(expected_output, result)

        # 测试字符串数组
        block_lines = [
            "a b c",
            "d e f",
            "g h i",
            "j k l",
            "m n o",
            "p q r"
        ]
        nx, ny, nz = 2, 3, 3
        expected_output = [
            [
                ["a", "b", "c"],
                ["d", "e", "f"],
                ["g", "h", "i"]
            ],
            [
                ["j", "k", "l"],
                ["m", "n", "o"],
                ["p", "q", "r"]
            ]
        ]
        result = ArrayUtils.lines_to_array_3d(block_lines, nx, ny, nz, str)
        self.assertEqual(expected_output, result)


if __name__ == '__main__':
    unittest.main()




