from PyQt5.QtGui import QColor

class Palette:
    white = QColor(255, 255, 255)
    blue = QColor(112, 169, 254)
    blue_light = QColor(169, 206, 254)
    blue_dark = QColor(69, 109, 200)
    orange = QColor(254, 169, 112)
    orange_light = QColor(254, 206, 169)
    orange_dark = QColor(200, 109, 69)
    green = QColor(80, 171, 66)
    green_light = QColor(178, 235, 188)
    green_dark = QColor(71, 143, 77)
    red = QColor(219, 101, 101)
    red_light = QColor(240, 188, 186)
    red_dark = QColor(173, 94, 72)
    gray = QColor(70, 70, 70) 
    gray_light = QColor(240, 240, 240)
    gray_dark = QColor(50, 50, 50)
    
# QColor 的lighter和darker方法

# 根据主题颜色获取颜色
def get_theme_colors(theme_color):
    # 如果在palette中，则直接返回
    if theme_color == Palette.blue:
        return [Palette.blue, Palette.blue_light, Palette.blue_dark]
    elif theme_color == Palette.orange:
        return [Palette.orange, Palette.orange_light, Palette.orange_dark]
    elif theme_color == Palette.green:
        return [Palette.green, Palette.green_light, Palette.green_dark]
    elif theme_color == Palette.red:
        return [Palette.red, Palette.red_light, Palette.red_dark]
    elif theme_color == Palette.gray:
        return [Palette.gray, Palette.gray_light, Palette.gray_dark]
    else:
        return [theme_color, theme_color.lighter(130), theme_color.darker(130)]

