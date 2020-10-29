#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
from math import *


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    if len(p_list) != 2:
        return []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x0 == x1:
            if y1 < y0:
                y0, y1 = y1, y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            k = (y1 - y0) / (x1 - x0)
            if abs(k) <= 1:
                if x0 > x1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                y = y0
                result.append((x0, y0))
                for x in range(x0 + 1, x1 + 1):
                    y = y + k
                    result.append((x, int(y + 0.5)))
            else:
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                x = x0
                result.append((x0, y0))
                for y in range(y0 + 1, y1 + 1):
                    x = x + 1.0 / k
                    result.append((int(x + 0.5), y))
    elif algorithm == 'Bresenham':
        # TODO: need further modification
        if x0 == x1:
            if y1 < y0:
                y0, y1 = y1, y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            m = (y1 - y0) / (x1 - x0)
            if abs(m) <= 1:
                if x0 > x1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                dx = x1 - x0
                dy = y1 - y0
                c1 = 2 * dy
                c2 = 2 * (dy - dx)
                c3 = 2 * (dy + dx)
                if m >= 0:
                    p = 2 * dy - dx
                else:   # ?
                    p = 2 * dy + dx
                x, y = x0, y0
                result.append((x, y))
                for x in range(x0 + 1, x1 + 1):
                    if m >= 0:
                        if p >= 0:
                            y += 1
                            p += c2
                        else:
                            p += c1
                    else:
                        if p >= 0:
                            p += c1
                        else:
                            y -= 1
                            p += c3
                    result.append((x, y))
            else:
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                dx = x1 - x0
                dy = y1 - y0
                c1 = 2 * dx
                c2 = 2 * (dx - dy)
                c3 = 2 * (dx + dy)
                if m >= 0:
                    p = 2 * dx - dy
                else:   # ?
                    p = 2 * dx + dy
                x, y = x0, y0
                result.append((x, y))
                for y in range(y0 + 1, y1 + 1):
                    if m >= 0:
                        if p >= 0:
                            x += 1
                            p += c2
                        else:
                            p += c1
                    else:
                        if p >= 0:
                            p += c1
                        else:
                            x -= 1
                            p += c3
                    result.append((x, y))
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    result1 = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    xc = int((x0 + x1) / 2 + 0.5)
    yc = int((y0 + y1) / 2 + 0.5)
    rx = int(abs((x1 - x0) / 2) + 0.5)
    ry = int(abs((y0 - y1) / 2) + 0.5)
    c1 = rx * rx
    c2 = ry * ry
    # 区域1
    x = 0
    y = ry
    result.append((x, y)) 
    while c2 * x < c1 * y:
        p = c2 * (x + 1) * (x + 1) + c1 * (y - 0.5) * (y - 0.5) - c1 * c2
        x += 1
        if p >= 0:
            y -= 1
        result.append((x, y))
    # 区域2
    while y > 0:
        p = c2 * (x + 0.5) * (x + 0.5) + c1 * (y - 1) * (y - 1) - c1 * c2
        y -= 1
        if p <= 0:
            x += 1
        result.append((x, y))

    for x, y in result:
        result1.append((x + xc, y + yc))
        result1.append((-x + xc, y + yc))
        result1.append((x + xc, -y + yc))
        result1.append((-x + xc, -y + yc))
    return result1


def deCasteljau(p_list, u):
    p = p_list
    n = len(p)
    x = -1
    y = -1
    if n < 2:
        return x, y
    while len(p) > 1:
        tmp = []
        for i in range(len(p) - 1):
            x = (1 - u) * p[i][0] + u * p[i + 1][0]
            y = (1 - u) * p[i][1] + u * p[i + 1][1]
            tmp.append([x, y])
        p = tmp
    return p[0][0], p[0][1]
    

'''
def BSpline(p_list, i, u):
    # P_{i-k},..., P_{i}, k=3
    u2 = u * u
    u3 = u * u2
    k1 = 1.0 / 6 * (1 - u) * (1 - u) * (1 - u)
    k2 = 1.0 / 6 * (3 * u3 - 6 * u2 + 4)
    k3 = 1.0 / 6 * (-3 * u3 + 3 * u2 + 3 * u + 1)
    k4 = 1.0 / 6 * u3
    x = k1 * p_list[i - 3][0] + k2 * p_list[i - 2][0] + k3 * p_list[i - 1][0] + k4 * p_list[i][0]
    y = k1 * p_list[i - 3][1] + k2 * p_list[i - 2][1] + k3 * p_list[i - 1][1] + k4 * p_list[i][1]
    return x, y
'''


def deBooxCox(k, i, u):
    if k == 1:
        if u >= i and u < i + 1:    # ?
            return 1
        else:
            return 0
    else:
        return (u - i) / (k - 1) * deBooxCox(k - 1, i, u) + (i + k - u) / (k - 1) * deBooxCox(k - 1, i + 1, u)


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    total = 1000
    if algorithm == 'Bezier':
        for i in range(total + 1):  # u=0开始？
            u = i / total
            x, y = deCasteljau(p_list, u)
            result.append((int(x + 0.5), int(y + 0.5)))
    elif algorithm == 'B-spline':
        total = 1000
        n = len(p_list) - 1     # n+1个顶点
        k = 3                   # 3次
        u = k
        while u <= n + 1:
            x = 0
            y = 0
            for i in range(n + 1):
                B = deBooxCox(k + 1, i, u)
                x += B * p_list[i][0]
                y += B * p_list[i][1]
            result.append((int(x + 0.5), int(y + 0.5)))
            u += 1.0 / total
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for x, y in p_list:
        result.append((x + dx, y + dy))
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    s = -sin(radians(r))
    c = cos(radians(r))
    for x1, y1 in p_list:
        # TODO：
        x2 = x + (x1 - x) * c - (y1 - y) * s
        y2 = y + (x1 - x) * s + (y1 - y) * c
        result.append((int(x2 + 0.5), int(y2 + 0.5)))
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for x1, y1 in p_list:
        x2 = x + (x1 - x) * s
        y2 = y + (y1 - y) * s
        result.append((int(x2 + 0.5), int(y2 + 0.5)))
    return result


def encode(x, y, x_min, y_min, x_max, y_max):
    LEFT = 1
    RIGHT = 2
    DOWN = 4
    UP = 8
    res = 0
    if x < x_min:
        res |= LEFT
    if x > x_max:
        res |= RIGHT
    if y < y_min:
        res |= DOWN
    if y > y_max:
        res |= UP
    return res


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
        
    if algorithm == 'Cohen-Sutherland':
        LEFT = 1
        RIGHT = 2
        DOWN = 4
        UP = 8
        while True:
            c0 = encode(x0, y0, x_min, y_min, x_max, y_max)
            c1 = encode(x1, y1, x_min, y_min, x_max, y_max)
            if c0 & c1 == 0:
                if c0 | c1 == 0:
                    return [[int(x0 + 0.5), int(y0 + 0.5)], [int(x1 + 0.5), int(y1 + 0.5)]]  # 均在窗口内
                else:
                    if c0 == 0: 
                        # P1在窗口内，交换P1和P2
                        x0, y0, x1, y1 = x1, y1, x0, y0
                        c0, c1 = c1, c0
                    if c0 & LEFT != 0:
                        x = x_min
                        if x0 == x1:
                            y = y0
                        else:
                            y = y0 + (y0 - y1) / (x0 - x1) * (x_min - x0)
                    elif c0 & RIGHT != 0:
                        x = x_max
                        if x0 == x1:
                            y = y0
                        else:
                            y = y0 + (y0 - y1) / (x0 - x1) * (x_max - x0)
                    elif c0 & DOWN != 0:
                        y = y_min
                        x = x0 + (x0 - x1) / (y0 - y1) * (y_min - y0)
                    elif c0 & UP != 0:
                        y = y_max
                        x = x0 + (x0 - x1) / (y0 - y1) * (y_max - y0)
                    x0 = x
                    y0 = y
            else:
                return []   # 均在窗口外
    elif algorithm == 'Liang-Barsky':
        dx = x1 - x0
        dy = y1 - y0
        u1, u2 = 0, 1
        m = [(-dx, x0 - x_min), (dx, x_max - x0), (-dy, y0 - y_min), (dy, y_max - y0)]
        for p, q in m:
            if p == 0:
                if q < 0:
                    return []
            else:
                r = q / p
                if p < 0:
                    u1 = max(r, u1)
                else:
                    u2 = min(r, u2)
            if u1 > u2:
                return []
        x01 = int(x0 + u1 * dx + 0.5)
        y01 = int(y0 + u1 * dy + 0.5)
        x11 = int(x0 + u2 * dx + 0.5)
        y11 = int(y0 + u2 * dy + 0.5)
        result = [[x01, y01], [x11, y11]]

    return result