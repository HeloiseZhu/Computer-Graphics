#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,  #
    QDialog,
    QColorDialog,
    QFileDialog,
    QFormLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QToolButton,
    QMenu,  #
    QAction)    #
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPixmap, QCursor, QTransform, QIcon
from PyQt5.QtCore import QRectF, Qt, QPoint
import math
import numpy as np

class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.color = QColor(0, 0, 0)

        self.clip_item = None
        self.temp_coordinate = None

    def get_ready(self):
        # 处理未完成的绘制或编辑
        if self.status == 'polygon':
            if self.temp_item:
                if len(self.temp_item.p_list) >= 3:
                    self.temp_item.finished = True
                    self.item_dict[self.temp_id] = self.temp_item
                    self.finish_draw()
                else:
                    self.scene().removeItem(self.temp_item)
                    if self.temp_id in self.item_dict:
                        del self.item_dict[self.selected_id]
        elif self.status == 'curve':
            if self.temp_item:
                if self.temp_algorithm == 'Bezier' and len(self.temp_item.p_list) < 2:
                    self.scene().removeItem(self.temp_item)
                    if self.temp_id in self.item_dict:
                        del self.item_dict[self.selected_id]
                elif self.temp_algorithm == 'B-spline' and len(self.temp_item.p_list) < 3:
                    self.scene().removeItem(self.temp_item)
                    if self.temp_id in self.item_dict:
                        del self.item_dict[self.selected_id]
                else:
                    self.temp_item.finished = True
                    self.item_dict[self.temp_id] = self.temp_item
                    self.finish_draw()
        self.updateScene([self.sceneRect()])

        if self.selected_id not in self.item_dict:
            self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.temp_item = None
        self.temp_coordinate = None

    def finish_draw(self):
        self.temp_item.finished = True
        self.main_window.item_cnt += 1
        self.temp_id = self.main_window.get_id()
        self.temp_item = None
        
    def finish_edit(self):
        self.get_ready()
        self.main_window.statusBar().showMessage('空闲')

    def start_set_pen(self, color):
        self.get_ready()
        self.color = color
        self.main_window.statusBar().showMessage('空闲')

    def start_copy(self):
        self.get_ready()
        self.status = 'copy'
        if self.selected_id in self.item_dict:
            self.clip_item = self.item_dict[self.selected_id]
        else:
            self.clip_item = None
        self.finish_edit()

    def start_paste(self, item_id):
        self.status = 'paste'
        self.temp_id = self.main_window.get_id()
        self.temp_item = MyItem(self.temp_id, self.clip_item.item_type, self.clip_item.p_list, self.clip_item.algorithm, color=self.clip_item.color, fill=self.clip_item.fill)
        self.temp_item.finished = True
        self.temp_item.p_list = alg.translate(self.temp_item.p_list, 15, 15)
        self.item_dict[self.temp_id] = self.temp_item
        self.scene().addItem(self.temp_item)
        self.selection_changed(self.temp_item.id)
        self.updateScene([self.sceneRect()])
        self.finish_draw()
        self.finish_edit()

    def start_draw_line(self, algorithm, item_id):
        self.get_ready()
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = self.main_window.get_id()

    def start_draw_rectangle(self, algorithm, item_id):
        self.get_ready()
        self.status = 'rectangle'
        self.temp_algorithm = algorithm
        self.temp_id = self.main_window.get_id()

    def start_draw_polygon(self, algorithm, item_id):
        self.get_ready()
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = self.main_window.get_id()

    def start_draw_ellipse(self, algorithm, item_id):
        self.get_ready()
        self.status = 'ellipse'
        self.temp_algorithm = algorithm
        self.temp_id = self.main_window.get_id()

    def start_draw_curve(self, algorithm, item_id):
        self.get_ready()
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = self.main_window.get_id()
    
    def start_translate(self):
        self.get_ready()
        self.status = 'translate_p1'
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list.copy()
    
    def start_rotate(self):
        self.get_ready()
        self.status = 'rotate'
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list.copy()
        rect = self.temp_item.boundingRect()
        cx = int(float(rect.left() + rect.right()) / 2 + 0.5)
        cy = int(float(rect.bottom() + rect.top()) / 2 + 0.5)
        self.rotate_center = [cx, cy]

    def start_scale(self):
        self.get_ready()
        self.status = 'scale'
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list.copy()
        rect = self.temp_item.boundingRect()
        cx = int(float(rect.left() + rect.right()) / 2 + 0.5)
        cy = int(float(rect.bottom() + rect.top()) / 2 + 0.5)
        self.scale_center = [cx, cy]

    def start_clip(self, algorithm):
        self.get_ready()
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list.copy()

    def start_polygon_clip(self, algorithm):
        self.get_ready()
        self.status = 'polygon_clip'
        self.temp_algorithm = algorithm
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list.copy()

    def start_fill(self):
        self.get_ready()
        self.status = 'fill'
        if self.selected_id in self.item_dict:
            self.temp_item = self.item_dict[self.selected_id]
            if self.temp_item.item_type == 'rectangle' or self.temp_item.item_type == 'polygon':
                self.temp_item.fill = True
                self.temp_item.color = self.color
                self.item_dict[self.selected_id] = self.temp_item
                self.updateScene([self.sceneRect()])
        self.finish_edit()
        

    def start_delete(self):
        self.get_ready()
        self.status = 'delete'
        if self.selected_id in self.item_dict:
            self.temp_item = self.item_dict[self.selected_id]
            del self.item_dict[self.selected_id]
            self.scene().removeItem(self.temp_item)
            self.updateScene([self.sceneRect()])
        self.status = ''
        self.temp_item = None

    def clear_selection(self):
        if self.selected_id in self.item_dict:
            self.item_dict[self.selected_id].selected = False
        self.selected_id = ''

    def selection_changed(self, selected):
        if self.selected_id in self.item_dict:
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        if selected in self.item_dict:
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
        else:
            self.selected_id = ''
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'rectangle':
            self.temp_item = MyItem(self.temp_id, 'rectangle', [[x, y], [x, y]], self.temp_algorithm, color=self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if self.temp_item:
                x0, y0 = self.temp_item.p_list[0]
                if math.sqrt((x - x0)** 2 + (y - y0)** 2) <= 10 and len(self.temp_item.p_list) >= 3:
                    #self.temp_item.p_list.append([x0, y0])
                    self.temp_item.finished = True
                    self.item_dict[self.temp_id] = self.temp_item
                    #self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    if len(self.temp_item.p_list) == 2:
                        fx = (self.temp_item.p_list[0][0] == self.temp_item.p_list[1][0])
                        fy = (self.temp_item.p_list[0][1] == self.temp_item.p_list[1][1])
                        if fx and fy:
                            self.temp_item.p_list.pop(0)
                    self.temp_item.p_list.append([x, y])
            else:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
                self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if self.temp_item:
                if len(self.temp_item.p_list) >= 2:
                    x1, y1 = self.temp_item.p_list[0]
                    x2, y2 = self.temp_item.p_list[1]
                    if x1 == x2 and y1 == y2:
                        self.temp_item.p_list.pop(1)
                self.temp_item.p_list.append([x, y])
            else:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
                self.scene().addItem(self.temp_item)
        elif self.status == 'translate_p1':
            item = self.main_window.scene.itemAt(pos, QTransform())
            if item == self.temp_item:
                self.temp_coordinate = [x, y]
                self.status = 'translate_p2'
        elif self.status == 'translate_p2':
            pass
        elif self.status == 'rotate':
            self.rotate_start = [x, y]
            self.rotate_end = [x, y]
        elif self.status == 'scale':
            self.scale_start = [x, y]
            self.scale_end = [x, y]
        elif self.status == 'clip':
            self.temp_coordinate = [x, y]
        elif self.status == 'polygon_clip':
            self.temp_coordinate = [x, y]
        elif self.status == '':
            self.temp_item = self.main_window.scene.itemAt(pos, QTransform())
            if self.temp_item:
                self.selection_changed(self.temp_item.id)
            else:
                self.selection_changed('')
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            if self.temp_item:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'rectangle':
            if self.temp_item:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon':
            if self.temp_item:
                x0, y0 = self.temp_item.p_list[0]
                if math.sqrt((x - x0)** 2 + (y - y0)** 2) <= 10 and len(self.temp_item.p_list) >= 4:
                    self.temp_item.p_list.pop(len(self.temp_item.p_list) - 1)
                    self.temp_item.finished = True
                    self.item_dict[self.temp_id] = self.temp_item
                    self.finish_draw()
                else:
                    self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse':
            if self.temp_item:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve':
            if self.temp_item:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate_p1':
            pass
        elif self.status == 'translate_p2':
            if self.temp_coordinate:
                sx, sy = self.temp_coordinate
                self.temp_item.p_list = alg.translate(self.temp_plist, x - sx, y - sy)
        elif self.status == 'rotate':
            self.rotate_end = [x, y]
            # 计算向量夹角
            sx, sy = self.rotate_start
            ex, ey = self.rotate_end
            cx, cy = self.rotate_center
            vec1 = np.array([sx - cx, sy - cy])
            vec2 = np.array([ex - cx, ey - cy])
            len1 = np.sqrt(vec1.dot(vec1))
            len2 = np.sqrt(vec2.dot(vec2))
            r = np.arccos(vec1.dot(vec2) / (len1 * len2))
            angle = int(math.degrees(r) + 0.5)
            if sx == ex:
                if sy < ey and cx > sx:
                    angle = 360 - angle
                elif sy > ey and cx < sx:
                    angle = 360 - angle
            else:
                k = (ey - sy) / (ex - sx)
                b = sy - k * sx
                if sx > ex and cy > k * cx + b:
                    angle = 360 - angle
                elif sx < ex and cy < k * cx + b:
                    angle = 360 - angle
            if self.temp_item:
                self.temp_item.p_list = alg.rotate(self.temp_plist, self.rotate_center[0], self.rotate_center[1], -angle)
        elif self.status == 'scale':
            self.scale_end = [x, y]
            # 计算向量夹角
            sx, sy = self.scale_start
            ex, ey = self.scale_end
            cx, cy = self.scale_center
            s = math.sqrt((ex - sx)** 2 + (ey - sy)** 2) / 80
            if self.temp_item:
                self.temp_item.p_list = alg.scale(self.temp_plist, cx, cy, s)
        elif self.status == 'clip':
            sx, sy = self.temp_coordinate
            if self.temp_item:
                self.temp_item.p_list = alg.clip(self.temp_plist, sx, sy, x, y, self.temp_algorithm)
        elif self.status == 'polygon_clip':
            sx, sy = self.temp_coordinate
            if self.temp_algorithm == 'Sutherland-Hodgman':
                if self.temp_item:
                    self.temp_item.p_list = alg.polygon_clip(self.temp_plist, sx, sy, x, y, self.temp_algorithm)
        elif self.status == '':
            pass
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.finish_draw()
        elif self.status == 'rectangle':
            x1, y1 = self.temp_item.p_list[0]
            x2, y2 = self.temp_item.p_list[1]
            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            temp_plist = [[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]
            self.temp_item.item_type = 'polygon'
            self.temp_item.p_list = temp_plist
            self.temp_item.finished = True
            self.item_dict[self.temp_id] = self.temp_item
            self.finish_draw()
        elif self.status == 'polygon':
            pass
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.finish_draw()
        elif self.status == 'curve':
            pass
        elif self.status == 'translate_p1':
            pass
        elif self.status == 'translate_p2':
            self.item_dict[self.selected_id] = self.temp_item
            self.status = 'translate_p1'
            self.temp_coordinate = None
            self.temp_plist = self.temp_item.p_list.copy()
        elif self.status == 'rotate':
            self.item_dict[self.selected_id] = self.temp_item
            self.rotate_start = None
            self.rotate_end = None
            self.temp_plist = self.temp_item.p_list.copy()
        elif self.status == 'scale':
            self.item_dict[self.selected_id] = self.temp_item
            self.scale_start = None
            self.scale_end = None
            self.temp_plist = self.temp_item.p_list.copy()
        elif self.status == 'clip':
            if len(self.temp_item.p_list) > 0:
                self.item_dict[self.selected_id] = self.temp_item
                self.temp_coordinate = None
                self.temp_plist = self.temp_item.p_list.copy()
            else:
                del self.item_dict[self.selected_id]
                self.scene().removeItem(self.temp_item)
            self.finish_edit()
        elif self.status == 'polygon_clip':
            if len(self.temp_item.p_list) > 0:
                self.item_dict[self.selected_id] = self.temp_item
                self.temp_coordinate = None
                self.temp_plist = self.temp_item.p_list.copy()
            else:
                del self.item_dict[self.selected_id]
                self.scene().removeItem(self.temp_item)
            self.finish_edit()
        elif self.status == '':
            pass
        super().mouseReleaseEvent(event)
    

class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = QColor(0, 0, 0), fill: bool = False, parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False       # 是否被选中
        self.color = color          # 图元颜色
        self.fill = fill            # 是否填充
        self.finished = False       # 是否绘制结束

    def highlight(self, x, y):
        # 高亮坐标(x,y)
        # 返回两种颜色像素点的坐标列表
        red_pixels = []     # 外圈
        black_pixels = []   # 内圈
        red_pixels += alg.draw_ellipse([[x - 4, y - 4], [x + 4, y + 4]])
        red_pixels += alg.draw_ellipse([[x - 3, y - 3], [x + 3, y + 3]])
        black_pixels += alg.draw_ellipse([[x - 2, y - 2], [x + 2, y + 2]])
        black_pixels += alg.draw_ellipse([[x - 1, y - 1], [x + 1, y + 1]])
        return red_pixels, black_pixels

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'rectangle':
            x1, y1 = self.p_list[0]
            x2, y2 = self.p_list[1]
            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            temp_plist = [[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]
            item_pixels = alg.draw_polygon(temp_plist, self.algorithm, label=True)
            if self.fill:
                item_pixels += alg.polygon_fill(temp_plist)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm, label=self.finished)
            if self.fill:
                item_pixels += alg.polygon_fill(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if not self.finished or self.selected:
                # 显示控制点
                red_pixels = []
                black_pixels = []
                for x, y in self.p_list:
                    r, b = self.highlight(x, y)
                    red_pixels += r
                    black_pixels += b
                for i in range(len(self.p_list) - 1):
                    red_pixels += alg.draw_line([self.p_list[i], self.p_list[i + 1]], 'DDA')
                painter.setPen(QColor(255, 0, 0))
                for p in red_pixels:
                    painter.drawPoint(*p)
                painter.setPen(QColor(0, 0, 0))
                for p in black_pixels:
                    painter.drawPoint(*p)
                painter.setPen(self.color)

        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            if len(self.p_list) != 2:
                return QRectF()
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'rectangle':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon':
            if len(self.p_list) > 0:
                x0, y0 = self.p_list[0]
                x1, y1 = self.p_list[0]
                for x, y in self.p_list:
                    x0 = min(x0, x)
                    y0 = min(y0, y)
                    x1 = max(x1, x)
                    y1 = max(y1, y)
                w = x1 - x0
                h = y1 - y0
                return QRectF(x0 - 1, y0 - 1, w + 2, h + 2)
            else:
                return QRectF()
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[0]
            for x, y in self.p_list:
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
            w = x1 - x0
            h = y1 - y0
            return QRectF(x0 - 1, y0 - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QGraphicsView作为画布
        self.canvas_width = 750
        self.canvas_height = 750
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.canvas_width, self.canvas_height)
        self.canvas_widget.main_window = self

        # 禁用滚动条
        self.canvas_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.canvas_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        m_set_pen_act = file_menu.addAction('设置画笔')
        m_reset_canvas_act = file_menu.addAction('重置画布')
        m_save_canvas_act = file_menu.addAction('保存画布')
        m_exit_act = file_menu.addAction('退出')
        
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        m_line_naive_act = line_menu.addAction('Naive')
        m_line_dda_act = line_menu.addAction('DDA')
        m_line_bresenham_act = line_menu.addAction('Bresenham')
        rectangle_menu = draw_menu.addMenu('矩形')
        m_rectangle_dda_act = rectangle_menu.addAction('DDA')
        m_rectangle_bresenham_act = rectangle_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        m_polygon_dda_act = polygon_menu.addAction('DDA')
        m_polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        m_ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        m_curve_bezier_act = curve_menu.addAction('Bezier')
        m_curve_b_spline_act = curve_menu.addAction('B-spline')
        
        edit_menu = menubar.addMenu('编辑')
        m_translate_act = edit_menu.addAction('平移')
        m_rotate_act = edit_menu.addAction('旋转')
        m_scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('线段裁剪')
        m_clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        m_clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        polygon_clip_menu = edit_menu.addMenu('多边形裁剪')
        m_polygon_clip_sutherland_hodgman_act = polygon_clip_menu.addAction('Sutherland-Hodgman')
        m_fill_act = edit_menu.addAction('多边形填充')
        m_delete_act = edit_menu.addAction('删除图元')

        # 设置工具栏
        toolbar = self.addToolBar('工具栏')
        # 画布设置（文件）
        save_canvas_act = QAction(QIcon('./icon/save.png'), '保存画布', self)
        reset_canvas_act = QAction(QIcon('./icon/reset.png'), '重置画布', self)
        set_pen_act = QAction(QIcon('./icon/pen.png'), '设置画笔', self)
        exit_act = QAction(QIcon('./icon/exit.png'), '退出', self)
        mouse_act = QAction(QIcon('./icon/mouse.png'), '点击', self)
        # 图元绘制
        # 直线
        line_btn = QToolButton()
        line_btn.setIcon(QIcon('./icon/line.png'))
        line_btn.setToolTip('线段')
        line_btn.setPopupMode(QToolButton.InstantPopup)
        line_menu = QMenu()
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        line_btn.setMenu(line_menu)
        # 矩形
        rectangle_btn = QToolButton()
        rectangle_btn.setIcon(QIcon('./icon/rectangle.png'))
        rectangle_btn.setToolTip('矩形')
        rectangle_btn.setPopupMode(QToolButton.InstantPopup)
        rectangle_menu = QMenu()
        rectangle_dda_act = rectangle_menu.addAction('DDA')
        rectangle_bresenham_act = rectangle_menu.addAction('Bresenham')
        rectangle_btn.setMenu(rectangle_menu)
        # 多边形
        polygon_btn = QToolButton()
        polygon_btn.setIcon(QIcon('./icon/polygon.png'))
        polygon_btn.setToolTip('多边形')
        polygon_btn.setPopupMode(QToolButton.InstantPopup)
        polygon_menu = QMenu()
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        polygon_btn.setMenu(polygon_menu)
        # 椭圆
        ellipse_act = QAction(QIcon('./icon/ellipse.png'), '椭圆', self)
        # 曲线
        curve_btn = QToolButton()
        curve_btn.setIcon(QIcon('./icon/curve.png'))
        curve_btn.setToolTip('曲线')
        curve_btn.setPopupMode(QToolButton.InstantPopup)
        curve_menu = QMenu()
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        curve_btn.setMenu(curve_menu)
        # 图元编辑
        translate_act = QAction(QIcon('./icon/translate.png'), '平移', self)
        rotate_act = QAction(QIcon('./icon/rotate.png'), '旋转', self)
        scale_act = QAction(QIcon('./icon/scale.png'), '缩放', self)
        clip_btn = QToolButton()
        clip_btn.setIcon(QIcon('./icon/clip.png'))
        clip_btn.setToolTip('线段裁剪')
        clip_btn.setPopupMode(QToolButton.InstantPopup)
        clip_menu = QMenu()
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        clip_btn.setMenu(clip_menu)
        polygon_clip_btn = QToolButton()
        polygon_clip_btn.setIcon(QIcon('./icon/polygon_clip.png'))
        polygon_clip_btn.setToolTip('多边形裁剪')
        polygon_clip_btn.setPopupMode(QToolButton.InstantPopup)
        polygon_clip_menu = QMenu()
        polygon_clip_sutherland_hodgman_act = polygon_clip_menu.addAction('Sutherland-Hodgman')
        #polygon_clip_weiler_atherton_act = polygon_clip_menu.addAction('Weiler-Atherton')
        polygon_clip_btn.setMenu(polygon_clip_menu)
        fill_act = QAction(QIcon('./icon/fill.png'), '多边形填充', self)
        delete_act = QAction(QIcon('./icon/delete.png'), '删除图元', self)

        toolbar.addAction(save_canvas_act)
        toolbar.addAction(reset_canvas_act)
        toolbar.addAction(set_pen_act)
        toolbar.addAction(exit_act)
        toolbar.addAction(mouse_act)
        toolbar.addSeparator()
        toolbar.addWidget(line_btn)
        toolbar.addWidget(rectangle_btn)
        toolbar.addWidget(polygon_btn)
        toolbar.addAction(ellipse_act)
        toolbar.addWidget(curve_btn)
        toolbar.addSeparator()
        toolbar.addAction(translate_act)
        toolbar.addAction(rotate_act)
        toolbar.addAction(scale_act)
        toolbar.addWidget(clip_btn)
        toolbar.addWidget(polygon_clip_btn)
        toolbar.addAction(fill_act)
        toolbar.addAction(delete_act)
        
        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)
        mouse_act.triggered.connect(self.mouse_action)
        m_set_pen_act.triggered.connect(self.set_pen_action)
        m_reset_canvas_act.triggered.connect(self.reset_canvas_action)
        m_save_canvas_act.triggered.connect(self.save_canvas_action)
        m_exit_act.triggered.connect(qApp.quit)
        
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        rectangle_dda_act.triggered.connect(self.rectangle_dda_action)
        rectangle_bresenham_act.triggered.connect(self.rectangle_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        m_line_naive_act.triggered.connect(self.line_naive_action)
        m_line_dda_act.triggered.connect(self.line_dda_action)
        m_line_bresenham_act.triggered.connect(self.line_bresenham_action)
        m_rectangle_dda_act.triggered.connect(self.rectangle_dda_action)
        m_rectangle_bresenham_act.triggered.connect(self.rectangle_bresenham_action)
        m_polygon_dda_act.triggered.connect(self.polygon_dda_action)
        m_polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        m_ellipse_act.triggered.connect(self.ellipse_action)
        m_curve_bezier_act.triggered.connect(self.curve_bezier_action)
        m_curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        polygon_clip_sutherland_hodgman_act.triggered.connect(self.polygon_clip_sutherland_hodgman_action)
        #polygon_clip_weiler_atherton_act.triggered.connect(self.polygon_clip_weiler_atherton_action)
        fill_act.triggered.connect(self.fill_action)
        delete_act.triggered.connect(self.delete_action)
        m_translate_act.triggered.connect(self.translate_action)
        m_rotate_act.triggered.connect(self.rotate_action)
        m_scale_act.triggered.connect(self.scale_action)
        m_clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        m_clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        m_polygon_clip_sutherland_hodgman_act.triggered.connect(self.polygon_clip_sutherland_hodgman_action)
        m_fill_act.triggered.connect(self.fill_action)
        m_delete_act.triggered.connect(self.delete_action)
        
        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(750, 750)
        self.setWindowTitle('CG Paint')
        self.setWindowIcon(QIcon('./icon/paint.png'))

        # 自定义菜单、消息框
        self.canvas_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas_widget.customContextMenuRequested.connect(self.canvas_context_menu_action)


    def get_id(self):
        _id = str(self.item_cnt)
        #self.item_cnt += 1
        return _id

    def canvas_context_menu_action(self):
        if self.canvas_widget.status == '':
            pos = self.canvas_widget.mapToScene(QCursor.pos())
            # 右键菜单
            context_menu = QMenu()
            copy_act = context_menu.addAction('复制')
            paste_act = context_menu.addAction('粘贴')
            copy_act.triggered.connect(self.copy_action)
            paste_act.triggered.connect(self.paste_action)
            # 设置选项不可用
            if not self.canvas_widget.clip_item:
                paste_act.setEnabled(False)
            if self.canvas_widget.selected_id == '':
                copy_act.setEnabled(False)
            context_menu.exec_(QCursor.pos())

    def copy_action(self):
        self.statusBar().showMessage('复制图元')
        self.canvas_widget.start_copy()

    def paste_action(self):
        self.statusBar().showMessage('粘贴图元')
        self.canvas_widget.start_paste(self.get_id())

    def set_pen_action(self):
        self.statusBar().showMessage('设置画笔')
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas_widget.start_set_pen(color)

    def reset_canvas_action(self):
        self.statusBar().showMessage('重置画布')
        # 设置输入窗口的布局
        dlg = QDialog()
        dlg.setWindowTitle('重置画布')
        form = QFormLayout(dlg)
        box1 = QSpinBox(dlg)
        box1.setRange(100, 1000)
        box1.setValue(self.canvas_width)
        box2 = QSpinBox(dlg)
        box2.setRange(100, 1000)
        box2.setValue(self.canvas_height)
        okBtn = QPushButton('确定')
        okBtn.clicked.connect(dlg.accept)
        form.addRow('宽度：', box1)
        form.addRow('高度：', box2)
        form.addRow(okBtn)
        form.setVerticalSpacing(20)
        form.setHorizontalSpacing(10)

        if dlg.exec() == 1:
            if box1.value() > 0 and box2.value() > 0:
                self.canvas_width = box1.value()
                self.canvas_height = box2.value()
            # 清空图元和列表
            self.canvas_widget.clear_selection()
            self.scene.clear()
            self.item_cnt = 0
            # 设置画布大小
            self.scene = QGraphicsScene(self)
            self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
            self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
            self.canvas_widget = MyCanvas(self.scene, self)
            self.canvas_widget.setFixedSize(self.canvas_width, self.canvas_height)
            self.canvas_widget.main_window = self
            self.canvas_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            self.canvas_widget.customContextMenuRequested.connect(self.canvas_context_menu_action)   
            self.canvas_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.canvas_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.hbox_layout = QHBoxLayout()
            self.hbox_layout.addWidget(self.canvas_widget)
            self.central_widget = QWidget()
            self.central_widget.setLayout(self.hbox_layout)
            self.setCentralWidget(self.central_widget)
            self.resize(self.canvas_width, self.canvas_height)
            self.mouse_action()

    def save_canvas_action(self):
        self.statusBar().showMessage('保存画布')
        filename = QFileDialog.getSaveFileName(self, '保存画布', './output/my_canvas.bmp', 'Image Files(*.jpg *.png *.bmp)')
        if filename[0] != '':
            selected = self.canvas_widget.selected_id
            self.canvas_widget.selection_changed('')
            pix = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            pix.save(filename[0])
            self.canvas_widget.selection_changed(selected)

    def line_naive_action(self):
        self.statusBar().showMessage('Naive算法绘制线段')
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.statusBar().showMessage('DDA算法绘制线段')
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.canvas_widget.clear_selection()

    def rectangle_dda_action(self):
        self.statusBar().showMessage('DDA算法绘制矩形')
        self.canvas_widget.start_draw_rectangle('DDA', self.get_id())
        self.canvas_widget.clear_selection()

    def rectangle_bresenham_action(self):
        self.statusBar().showMessage('Bresenham算法绘制矩形')
        self.canvas_widget.start_draw_rectangle('Bresenham', self.get_id())
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.statusBar().showMessage('绘制椭圆')
        self.canvas_widget.start_draw_ellipse('MCA', self.get_id())
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.canvas_widget.clear_selection()

    def translate_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            self.statusBar().showMessage('平移')
            self.canvas_widget.start_translate()
        else:
            self.mouse_action()

    def rotate_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type != 'ellipse':
                self.statusBar().showMessage('旋转')
                self.canvas_widget.start_rotate()     
        else:
            self.mouse_action()

    def scale_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            self.statusBar().showMessage('缩放')
            self.canvas_widget.start_scale()
        else:
            self.mouse_action()

    def clip_cohen_sutherland_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type == 'line':
                self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段')
                self.canvas_widget.start_clip('Cohen-Sutherland')
        else:
            self.mouse_action()

    def clip_liang_barsky_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type == 'line':
                self.statusBar().showMessage('Liang-Barsky算法裁剪线段')
                self.canvas_widget.start_clip('Liang-Barsky')
        else:
            self.mouse_action()

    def polygon_clip_sutherland_hodgman_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type == 'rectangle' or temp_item.item_type == 'polygon':
                self.statusBar().showMessage('Sutherland-Hodgman算法裁剪多边形')
                self.canvas_widget.start_polygon_clip('Sutherland-Hodgman')
        else:
            self.mouse_action()

    def fill_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            self.statusBar().showMessage('填充')
            self.canvas_widget.start_fill()
        else:
            self.mouse_action()

    def delete_action(self):
        if self.canvas_widget.selected_id in self.canvas_widget.item_dict:
            self.statusBar().showMessage('删除图元')
            self.canvas_widget.start_delete()
        else:
            self.mouse_action()

    def mouse_action(self):
        self.canvas_widget.get_ready()
        self.statusBar().showMessage('空闲')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())