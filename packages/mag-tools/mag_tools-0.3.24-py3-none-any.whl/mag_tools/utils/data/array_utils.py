from typing import Any, List

import numpy as np

from mag_tools.bean.text_format import TextFormat
from mag_tools.utils.data.value_utils import ValueUtils


class ArrayUtils:
    @staticmethod
    def text_to_array_1d(text: str, data_type: type) -> List[Any]:
        """
        从一行文本中获取数值数组[]
        :param text: 文本，由 "数值" 或 "数值个数*数值"构成
        :param data_type: 数据类型
        :return: 数值数组
        """
        data = []

        for part in text.split():
            if '*' in part:
                count, value = part.split('*')
                data.extend([ValueUtils.to_value(value, data_type)] * int(count))
            else:
                data.append(ValueUtils.to_value(part, data_type))

        return data

    @staticmethod
    def lines_to_array_1d(lines: List[str], data_type: type) -> List[Any]:
        """
        从多行文本中获取数值数组[]
        :param lines: 文本段，每行由 "数值" 或 "数值个数*数值"构成
        :param data_type: 数据类型
        :return: 数值数组
        """
        array_1d = []
        for line in lines:
            array_1d.extend(ArrayUtils.text_to_array_1d(line, data_type))
        return array_1d

    @staticmethod
    def lines_to_array_2d(lines: List[str], nx: int, ny: int, data_type: type) -> List[
        List[Any]]:
        """
        从文本块获取数值列表
        :param lines: 文本块，由多行构成，每行由 "数值" 或 "数值个数*数值"构成
        :param nx: 行数
        :param ny: 列数
        :param data_type: 数据类型
        :return: Values
        """
        array_1d = ArrayUtils.lines_to_array_1d(lines, data_type)
        return np.array(array_1d).reshape((nx, ny)).tolist()

    @staticmethod
    def lines_to_array_3d(block_lines: List[str], nx: int, ny: int, nz: int, data_type: type) -> List[List[List[Any]]]:
        """
        从文本块获取数值列表
        :param block_lines: 文本块，由多行构成，每行由 "数值" 或 "数值个数*数值"构成
        :param nx: 行数
        :param ny: 列数
        :param nz: 层数
        :param data_type: 数据类型
        :return: Values
        """
        array_1d = ArrayUtils.lines_to_array_1d(block_lines, data_type)
        return np.array(array_1d).reshape((nx, ny, nz)).tolist()

    @staticmethod
    def assign_array_2d(array2, i1, i2, j1, j2, value):
        """
        给数组指定区域的元素赋值
        :param array2: 二维数组
        :param i1: 起始行数
        :param i2: 结束行数
        :param j1: 起始列数
        :param j2: 结束列数
        :param value: 数值
        """
        if i1 < 0 or j1 < 0 or i2 >= len(array2) or j2 >= len(array2[0]):
            raise IndexError("Index out of range for the provided 2D array dimensions.")

        array2[i1:i2 + 1, j1:j2 + 1] = value
        return array2

    @staticmethod
    def multiply_array_2d(array2, i1, i2, j1, j2, factor):
        """
        给数组指定区域的元素乘以系数
        :param array2: 二维数组
        :param i1: 起始行数
        :param i2: 结束行数
        :param j1: 起始列数
        :param j2: 结束列数
        :param factor: 系数
        """
        if i1 < 0 or j1 < 0 or i2 >= len(array2) or j2 >= len(array2[0]):
            raise IndexError("Index out of range for the provided 2D array dimensions.")

        array2[i1:i2 + 1, j1:j2 + 1] *= factor
        return array2

    @staticmethod
    def add_array_2d(array2, i1, i2, j1, j2, value):
        """
        给数组指定区域的元素增加数值
        :param array2: 二维数组
        :param i1: 起始行数
        :param i2: 结束行数
        :param j1: 起始列数
        :param j2: 结束列数
        :param value: 数值
        """
        if i1 < 0 or j1 < 0 or i2 >= len(array2) or j2 >= len(array2[0]):
            raise IndexError("Index out of range for the provided 2D array dimensions.")

        array2[i1:i2 + 1, j1:j2 + 1] += value
        return array2

    @staticmethod
    def assign_array_3d(array3, i1, i2, j1, j2, k1, k2, value):
        """
        给数组指定区域的元素赋值
        :param array3: 三维数组
        :param i1: 起始层数
        :param i2: 结束层数
        :param j1: 起始行数
        :param j2: 结束行数
        :param k1: 起始列数
        :param k2: 结束列数
        :param value: 数值
        """
        if i1 < 0 or j1 < 0 or k1 < 0 or i2 >= len(array3) or j2 >= len(array3[0]) or k2 >= len(array3[0][0]):
            raise IndexError("Index out of range for the provided 3D array dimensions.")

        array3[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1] = value
        return array3

    @staticmethod
    def multiply_array_3d(array3, i1, i2, j1, j2, k1, k2, factor):
        """
        给数组指定区域的元素乘以系数
        :param array3: 三维数组
        :param i1: 起始层数
        :param i2: 结束层数
        :param j1: 起始行数
        :param j2: 结束行数
        :param k1: 起始列数
        :param k2: 结束列数
        :param factor: 系数
        """
        if i1 < 0 or j1 < 0 or k1 < 0 or i2 >= len(array3) or j2 >= len(array3[0]) or k2 >= len(array3[0][0]):
            raise IndexError("Index out of range for the provided 3D array dimensions.")

        array3[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1] *= factor
        return array3

    @staticmethod
    def add_array_3d(array3, i1, i2, j1, j2, k1, k2, value):
        """
        给数组指定区域的元素增加数值
        :param array3: 三维数组
        :param i1: 起始层数
        :param i2: 结束层数
        :param j1: 起始行数
        :param j2: 结束行数
        :param k1: 起始列数
        :param k2: 结束列数
        :param value: 数值
        """
        if i1 < 0 or j1 < 0 or k1 < 0 or i2 >= len(array3) or j2 >= len(array3[0]) or k2 >= len(array3[0][0]):
            raise IndexError("Index out of range for the provided 3D array dimensions.")

        array3[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1] += value
        return array3

    @staticmethod
    def copy_array_3d(source_array, target_array, i1, i2, j1, j2, k1, k2):
        """
        复制源数组指定区域到目标数组
        :param source_array: 源数组
        :param target_array: 目标数组
        :param i1: 起始层数
        :param i2: 结束层数
        :param j1: 起始行数
        :param j2: 结束行数
        :param k1: 起始列数
        :param k2: 结束列数
        """
        if i1 < 0 or j1 < 0 or k1 < 0 or i2 >= len(source_array) or j2 >= len(source_array[0]) or k2 >= len(
                source_array[0][0]):
            raise IndexError("Index out of range for the provided 3D array dimensions.")

        target_array[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1] = source_array[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1]
        return target_array


if __name__ == '__main__':
    _lines = ['60*0.087', '60*0.097']
    # _lines = ['1.18379        2.26189        2.61705        5.99524       10.31299',
    #           '15.17937       32.40075       33.90037      109.47345      261.72995',
    #           '238.24753      206.15742',
    #           '238.24753      206.15742      121.33305      242.47713      166.94165',
    #           '146.50681       13.91259        7.39986        5.83849        6.06996',
    #           '7.95473        8.99119']
    dt = ArrayUtils.lines_to_array_3d(_lines, 20, 3, 2, float)

    _text_format = TextFormat(number_per_line=5, decimal_places_of_zero=3, decimal_places=3)
    te = _text_format.array_3d_to_lines(dt)
    print("\n".join(te))
