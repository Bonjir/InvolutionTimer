# affliated to 卷摆计时器.py

from PyQt5.QtCore import Qt, QTime, QEasingCurve, \
    QPoint, QSize, QRect, \
    QTimer, QPropertyAnimation

from PyQt5.QtWidgets import QWidget
import typing
    
# class Animation(object):
#     # 实现方法1：类似于ui，把所有动画效果的过程都在这里面实现
#     def setupAnimation(self, Form):
#         self.ui = Ui_Form()
        
#         self.work_button_shrink = QPropertyAnimation(self.ui.work_button, b"geometry")
#         self.relax_button_shrink = QPropertyAnimation(self.ui.relax_button, b"geometry")
        
#     def work_button_shrink_start(self):
#         # 设置动画的起始值和结束值
#         start_rect = self.ui.work_button.geometry()
#         end_rect = QRect(mini_x, mini_y, self.mini_size.width(), self.mini_size.height())
#         self.work_button_shrink.setStartValue(start_rect)
#         self.work_button_shrink.setEndValue(end_rect)
#         self.work_button_shrink.setDuration(1000) # 设置动画持续时间
#         self.work_button_shrink.setEasingCurve(QEasingCurve.OutBounce) # 出弹跳动画
#         self.work_button_shrink.start()


class ShrinkTo(int):
    top_left = ...
    top_right = ...
    top_center = ...
    bottom_left = ...
    bottom_right = ...
    bottom_center = ...
    vcenter_left = ...
    vcenter_right = ...
    center = ...
    
class SimpleShrink(object):
    # 实现方法2：创建一个简单动画类，实现可能的动画过程，简化创建和启动的过程
    
    def __init__(self, window : QWidget, shrink_to : ShrinkTo = ShrinkTo.center, mini_size = QSize(0, 0), normal_size = QSize(-1, -1)):
        self.window = window
        self.shrink_to = shrink_to
        self.mini_size = mini_size
        self.normal_size = normal_size
        self.animation = QPropertyAnimation(window, b"geometry")
        self.default_duration = 1000
        self.default_shrink_easing_curve = QEasingCurve.Type.OutBounce
        self.default_restore_easing_curve = QEasingCurve.Type.OutElastic
    
    def set_normal_size(self, normal_size : QSize):
        self.normal_size = normal_size
    
    def set_mini_size(self, mini_size : QSize):
        self.mini_size = mini_size
    
    def set_shrink_to(self, shrink_to : ShrinkTo):
        self.shrink_to = shrink_to
        
    def set_restore_pos(self, restore_pos : QPoint):
        self.restore_pos = restore_pos
    
    def set_default_duration(self, duration : int):
        self.default_duration = duration
    
    def set_default_shrink_easing_curve(self, easing_curve : QEasingCurve.Type):
        self.default_shrink_easing_curve = easing_curve
        
    def set_default_restore_easing_curve(self, easing_curve : QEasingCurve.Type):
        self.default_restore_easing_curve = easing_curve
    
    @typing.overload
    def start_shrink_animation(self): ...
    @typing.overload
    def start_shrink_animation(self, duration): ...
    @typing.overload
    def start_shrink_animation(self, easing_curve): ...
    @typing.overload
    def start_shrink_animation(self, duration, easing_curve): ...
    
    def start_shrink_animation(self, *args):
        
        duration = self.default_duration
        easing_curve = self.default_shrink_easing_curve
        
        if len(args) == 1 and isinstance(args[0], bool):
            pass
        elif len(args) == 1 and isinstance(args[0], int):
            duration = args[0]
        elif len(args) == 1 and isinstance(args[0], QEasingCurve.Type):
            easing_curve = args[0]
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], QEasingCurve.Type):
            duration = args[0]
            easing_curve = args[0]
        
        print(f'{type(self.window)} shrinking')
        
        rect_now = self.window.geometry()
        # 记录当前窗口信息以供还原使用
        if self.normal_size.width() == -1 and self.normal_size.height() == -1:
            self.normal_size = QSize(rect_now.width(), rect_now.height())
        self.restore_pos = QPoint(rect_now.left(), rect_now.top())
        
        if self.shrink_to == ShrinkTo.top_left:
            end_x = rect_now.left()
            end_y = rect_now.top()
        elif self.shrink_to == ShrinkTo.vcenter_left:
            end_x = rect_now.left()
            end_y = int((rect_now.top() + rect_now.bottom()) / 2 - self.mini_size.height() / 2)
        elif self.shrink_to == ShrinkTo.bottom_left:
            end_x = rect_now.left()
            end_y = rect_now.bottom() - self.mini_size.height()
        elif self.shrink_to == ShrinkTo.top_center:
            end_x = int((rect_now.left() + rect_now.right()) / 2 - self.mini_size.width() / 2)
            end_y = rect_now.top()
        elif self.shrink_to == ShrinkTo.center:
            end_x = int((rect_now.left() + rect_now.right()) / 2 - self.mini_size.width() / 2)
            end_y = int((rect_now.top() + rect_now.bottom()) / 2 - self.mini_size.height() / 2)
        elif self.shrink_to == ShrinkTo.bottom_center:
            end_x = int((rect_now.left() + rect_now.right()) / 2 - self.mini_size.width() / 2)
            end_y = rect_now.bottom() - rect_now.height()
        elif self.shrink_to == ShrinkTo.top_right:
            end_x = rect_now.right() - self.mini_size.width()
            end_y = rect_now.top()
        elif self.shrink_to == ShrinkTo.vcenter_right:
            end_x = rect_now.right() - self.mini_size.width()
            end_y = int((rect_now.top() + rect_now.bottom()) / 2 - self.mini_size.height() / 2)
        elif self.shrink_to == ShrinkTo.bottom_right:
            end_x = rect_now.right() - self.mini_size.width()
            end_y = rect_now.bottom() - self.mini_size.height()
        else:
            print("Unknown ShrinkTo Pos")
        
        start_rect = rect_now
        end_rect = QRect(end_x, end_y, self.mini_size.width(), self.mini_size.height())
        # 设置动画的起始值和结束值
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setDuration(duration) # 设置动画持续时间
        self.animation.setEasingCurve(easing_curve) # 出弹跳动画
        self.animation.start()
    
    @typing.overload
    def start_restore_animation(self): ...
    @typing.overload
    def start_restore_animation(self, duration): ...
    @typing.overload
    def start_restore_animation(self, easing_curve): ...
    @typing.overload
    def start_restore_animation(self, duration, easing_curve): ...
    
    def start_restore_animation(self, *args):
        
        duration = self.default_duration
        easing_curve = self.default_restore_easing_curve
        
        if len(args) == 1 and isinstance(args[0], bool):
            pass
        elif len(args) == 1 and isinstance(args[0], int):
            duration = args[0]
        elif len(args) == 1 and isinstance(args[0], QEasingCurve.Type):
            easing_curve = args[0]
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], QEasingCurve.Type):
            duration = args[0]
            easing_curve = args[0]
            
        start_rect = self.window.geometry()
        end_rect = QRect(self.restore_pos.x(), self.restore_pos.y(), self.normal_size.width(), self.normal_size.height())
        # 设置动画的起始值和结束值
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setDuration(duration) # 设置动画持续时间
        self.animation.setEasingCurve(easing_curve) # 出弹跳动画
        self.animation.start()
    
    def stop_animation(self):
        self.animation.stop()
