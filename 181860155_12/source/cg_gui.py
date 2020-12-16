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
    QMenu,  #
    QAction)    #
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPixmap, QCursor, QTransform
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
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.color = QColor(0, 0, 0)

        # TODO: 附加功能
        self.clip_item = None

    def start_set_pen(self, color):
        self.status = ''
        self.color = color

    def start_copy(self):
        # TODO: id是否有效
        self.status = 'copy'
        self.clip_item = self.item_dict[self.selected_id]

    def start_paste(self, item_id):
        self.status = 'paste'
        self.temp_item = MyItem(item_id, self.clip_item.item_type, self.clip_item.p_list, self.clip_item.algorithm, color=self.clip_item.color)
        self.temp_item.p_list = alg.translate(self.temp_item.p_list, 10, 10)
        self.item_dict[self.temp_item.id] = self.temp_item
        self.list_widget.addItem(self.temp_item.id)
        self.scene().addItem(self.temp_item)
        self.updateScene([self.sceneRect()])
        self.finish_draw()

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_rectangle(self, algorithm, item_id):
        self.status = 'rectangle'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, algorithm, item_id):
        self.status = 'ellipse'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    def start_translate(self):
        self.status = 'translate'
        self.temp_algorithm = ''
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list
    
    def start_rotate(self):
        self.status = 'rotate_p1'
        self.temp_algorithm = ''
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list

    def start_scale(self):
        self.status = 'scale_p1'
        self.temp_algorithm = ''
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_item = self.item_dict[self.selected_id]
        self.temp_plist = self.temp_item.p_list

    def finish_draw(self):
        self.temp_item = None
        self.main_window.item_cnt += 1
        self.temp_id = self.main_window.get_id()
        # TODO:
        #self.status = ''
        
    def finish_edit(self):
        self.temp_item = None
        self.status = ''
        self.main_window.statusBar().showMessage('空闲')

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        # TODO: further modification
        if selected != '' and selected in self.item_dict:
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
            if self.selected_id in self.item_dict:
                self.item_dict[self.selected_id].selected = False
                self.item_dict[self.selected_id].update()   #?
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
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
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if self.temp_item:
                x0, y0 = self.temp_item.p_list[0]
                # TODO:
                if math.sqrt((x - x0)** 2 + (y - y0)** 2) <= 10 and len(self.temp_item.p_list) >= 3:
                    self.temp_item.p_list.append([x0, y0])
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append([x, y])
            else:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
                self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if self.temp_item:
                self.temp_item.p_list.append([x, y])
            else:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, color=self.color)
                self.scene().addItem(self.temp_item)
        elif self.status == 'translate':
            self.temp_coordinate = [x, y]
        elif self.status == 'rotate_p1':
            self.rotate_center = [x, y]
            #print(self.rotate_center)
        elif self.status == 'rotate_p2':
            self.rotate_start = [x, y]
            self.rotate_end = [x, y]
        elif self.status == 'scale_p1':
            self.scale_center = [x, y]
        elif self.status == 'scale_p2':
            self.scale_start = [x, y]
            self.scale_end = [x, y]
        elif self.status == 'clip':
            self.temp_coordinate = [x, y]
        elif self.status == '':
            # TODO: status何时表示空闲
            self.temp_item = self.main_window.scene.itemAt(pos, QTransform())
            if self.temp_item:
                self.selection_changed(self.temp_item.id)
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'rectangle':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon':
            if self.temp_item:
                x0, y0 = self.temp_item.p_list[0]
                # TODO: 和鼠标点击中同步修改
                if math.sqrt((x - x0)** 2 + (y - y0)** 2) <= 10 and len(self.temp_item.p_list) >= 4:
                    self.temp_item.p_list[-1] = [x0, y0]
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse':
            # TODO: bug
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve':
            if self.temp_item:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            sx, sy = self.temp_coordinate
            self.temp_item.p_list = alg.translate(self.temp_plist, x - sx, y - sy)
        elif self.status == 'rotate_p1':
            self.rotate_center = [x, y]
        elif self.status == 'rotate_p2':
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
            # TODO:注意临界点取等
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
            #print('旋转角度（顺）：', angle)
            self.temp_item.p_list = alg.rotate(self.temp_plist, self.rotate_center[0], self.rotate_center[1], -angle)
        elif self.status == 'scale_p1':
            self.scale_center = [x, y]
        elif self.status == 'scale_p2':
            self.scale_end = [x, y]
            # 计算向量夹角
            sx, sy = self.scale_start
            ex, ey = self.scale_end
            cx, cy = self.scale_center
            s = math.sqrt((ex - sx)** 2 + (ey - sy)** 2) / 80
            self.temp_item.p_list = alg.scale(self.temp_plist, cx, cy, s)
        elif self.status == 'clip':
            # TODO: bug
            sx, sy = self.temp_coordinate
            self.temp_item.p_list = alg.clip(self.temp_plist, min(sx, x), min(sy, y), max(sx, x), max(sy, y), self.temp_algorithm)
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'rectangle':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon':
            pass
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'curve':
            pass
        elif self.status == 'translate':
            self.item_dict[self.selected_id] = self.temp_item
            self.finish_edit()
        elif self.status == 'rotate_p1':
            self.status = 'rotate_p2'
        elif self.status == 'rotate_p2':
            self.item_dict[self.selected_id] = self.temp_item
            self.finish_edit()
        elif self.status == 'scale_p1':
            self.status = 'scale_p2'
        elif self.status == 'scale_p2':
            self.item_dict[self.selected_id] = self.temp_item
            self.finish_edit()
        elif self.status == 'clip':
            self.item_dict[self.selected_id] = self.temp_item
            #self.finish_edit()
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)

    '''
    # TODO:
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.status == 'curve':
            if self.temp_item:
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
    '''

    def keyPressEvent(self, QKeyEvent) -> None:
        if QKeyEvent.key() == Qt.Key_Return:
            if self.status == 'curve':
                if self.temp_item:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = QColor(0, 0, 0), parent: QGraphicsItem = None):
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

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'rectangle':
            item_pixels = alg.draw_rectangle(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon_gui(self.p_list, self.algorithm)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)

        for p in item_pixels:
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            # TODO
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
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            # TODO: 
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

        # 使用QListWidget来记录已有的图元，并用于选择图元。
        # TODO:这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(100)
        #self.list_widget.setMaximumWidth(100)

        # 使用QGraphicsView作为画布
        self.canvas_width = 600
        self.canvas_height = 600
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.canvas_width, self.canvas_height)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 禁用滚动条
        self.canvas_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.canvas_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        rectangle_menu = draw_menu.addMenu('矩形')
        rectangle_dda_act = rectangle_menu.addAction('DDA')
        rectangle_bresenham_act = rectangle_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)

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

        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.list_context_menu_action)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)   # TODO:
        self.setWindowTitle('CG Demo')  # TODO:


    def get_id(self):
        _id = str(self.item_cnt)
        #self.item_cnt += 1
        return _id

    def list_context_menu_action(self):
        context_menu = QMenu()
        #cut_act = context_menu.addAction('剪切')
        copy_act = context_menu.addAction('复制')
        paste_act = context_menu.addAction('粘贴')
        copy_act.triggered.connect(self.copy_action)
        paste_act.triggered.connect(self.paste_action)
        selected_index = self.list_widget.indexAt(self.list_widget.mapFromGlobal(QCursor.pos())).row()
        if selected_index > -1:
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
        # TODO: 设置窗口大小和位置

        if dlg.exec() == 1:
            self.canvas_width = box1.value()
            self.canvas_height = box2.value()
            # 清空图元和列表
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.scene.clear()
            self.list_widget.clear()
            self.item_cnt = 1 #TODO
            # 设置画布大小
            self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
            self.canvas_widget.resize(self.canvas_width, self.canvas_height)
            self.canvas_widget.setFixedSize(self.canvas_width, self.canvas_height)

    def save_canvas_action(self):
        self.statusBar().showMessage('保存画布')
        filename = QFileDialog.getSaveFileName(self, '保存画布', './output/my_canvas.bmp', 'Image Files(*.jpg *.png *.bmp)')
        if filename[0] != '':
            pix = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            pix.save(filename[0])
        '''
        pix = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
        pix.save('./output/my_canvas.bmp')
        '''

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def rectangle_dda_action(self):
        self.canvas_widget.start_draw_rectangle('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制矩形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def rectangle_bresenham_action(self):
        self.canvas_widget.start_draw_rectangle('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制矩形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse('MCA', self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        if self.canvas_widget.selected_id:    
            self.canvas_widget.start_translate()
            self.statusBar().showMessage('平移')

    def rotate_action(self):
        if self.canvas_widget.selected_id:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type != 'ellipse':
                self.canvas_widget.start_rotate()
                self.statusBar().showMessage('旋转')
            #TODO: 椭圆添加提示

    def scale_action(self):
        if self.canvas_widget.selected_id:
            self.canvas_widget.start_scale()
            self.statusBar().showMessage('缩放')

    def clip_cohen_sutherland_action(self):
        if self.canvas_widget.selected_id:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type == 'line':
                self.canvas_widget.start_clip('Cohen-Sutherland')
                self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段')

    def clip_liang_barsky_action(self):
        if self.canvas_widget.selected_id:
            temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
            if temp_item.item_type == 'line':
                self.canvas_widget.start_clip('Liang-Barsky')
                self.statusBar().showMessage('Liang-Barsky算法裁剪线段')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())