# coding: utf-8
from PyQt6.QtGui import QIcon, QPixmap, QImage, QColor
from PyQt6.QtCore import QSize
from ...utils import Utils
from pathlib import Path
from .utils import TypeTheme, Global
from PyQt6.QtCore import QFile

class Color(object):
    THEME = "theme"
    THEME_REVERSE = "theme_reverse"
    ORIGINAL = "original"
    LIGHT = "200_200_200"
    DARK = "55_55_55"
    BLUE = "73_145_246"
    GRAY = "130_130_130"

class Data(object):
    dict_icons = {}
    dict_icons_clolor = {}

class Name(object):

    def add_suffix(icon_name : str, suffix : str):
        extension = Path(icon_name).suffix
        return f"{icon_name.replace(extension, '')}_{suffix}{extension}"

    def add_suffix_theme(icon_name : str):
        suffix = Color.DARK if Global.theme == TypeTheme.light else Color.LIGHT
        extension = Path(icon_name).suffix
        return f"{icon_name.replace(extension, '')}_{suffix}{extension}"
    
    def add_suffix_reverse_theme(icon_name : str):
        suffix = Color.LIGHT if Global.theme == TypeTheme.light else Color.DARK
        extension = Path(icon_name).suffix
        return f"{icon_name.replace(extension, '')}_{suffix}{extension}"

    seta_baixo = "seta-baixo.png" 
    seta_cima = "seta-cima.png" 
    check_alt = "check-alt.png" 
    branch_closed = "branch_closed.png" 
    branch_open = "branch_open.png" 
    
class Icon(QIcon):
        def __init__(self, icon_name : Name , icon_color : Color | str = Color.THEME):
            self.name = icon_name
            if icon_name in Data.dict_icons:
                name_icon_color = Color.THEME
                if icon_color == Color.THEME:
                    if Global.theme == "dark":
                        name_icon_color = Color.DARK
                    else:
                        name_icon_color = Color.LIGHT
                else:
                    if icon_color == Color.THEME_REVERSE:
                        if Global.theme == "dark":
                            name_icon_color = Color.LIGHT
                        else:
                            name_icon_color = Color.DARK
                    else:
                        if icon_color in Data.dict_icons[icon_name]:
                            name_icon_color = icon_color

                if name_icon_color != Color.ORIGINAL:
                    if not QFile.exists(u':' + Name.add_suffix(icon_name, name_icon_color)):
                        icon = QIcon(u':' + icon_name)
                    else:
                        icon = Data.dict_icons[icon_name][name_icon_color]
                else:
                    icon = Data.dict_icons[icon_name][name_icon_color]
            else:
                icon = QIcon(u':' + icon_name)
            super().__init__(icon)

        def toPixmap(self, size : int = None):
            return Icons.to_pixmap(self, size)

class Icons(object):

    QMessageBox : Icon = None

    @classmethod
    def change_color(cls, icon : QIcon, new_color : QColor | tuple[int] | list[int] | str, index_available_size = -1):

        color = new_color
        if type(new_color) == str:
            color = QColor(new_color)
        elif type(new_color) == tuple or type(new_color) == list:
            color = QColor(*new_color)

        original_size = QSize(32, 32)
        if icon.availableSizes():
            sizes = icon.availableSizes()
            if 0 <= index_available_size < len(sizes):
                original_size = icon.availableSizes()[index_available_size]
            else:
                original_size = icon.availableSizes()[-1]

        pixmap : QPixmap  = icon.pixmap(original_size)  # Defina o tamanho desejado
        image = pixmap.toImage()

        new_image = QImage(image.size(), QImage.Format.Format_ARGB32)
        new_image.fill(0) 
        
        for x in range(image.width()):
            for y in range(image.height()):
                pixel_color = image.pixelColor(x, y)
                if not pixel_color.alpha():
                    continue

                new_image.setPixelColor(x, y, color)

        # Converta a imagem resultante de volta para um �cone
        new_pixmap = QPixmap.fromImage(new_image)
        new_icon = QIcon(new_pixmap)

        return new_icon
    
    @classmethod
    def download(cls, img_path : str, icon : QIcon, img_format = 'png', new_color : QColor | tuple[int] | list[int] | str = None):
        if new_color:
            icon = cls.change_color(icon, new_color)
        original_size = QSize(32, 32)
        if icon.availableSizes():
            original_size = icon.availableSizes()[0]
        pixmap : QPixmap = icon.pixmap(original_size)  # Defina o tamanho desejado
        image = pixmap.toImage()
        return image.save(img_path, img_format)

    class Data(object):
        def __init__(self, name : Name, hover_name : Name = None, color = Color.THEME, hover_color = Color.BLUE):
            self.name = name
            self.hover_name = hover_name
            self.color = color
            self.hover_color = hover_color

    class Color(Color):
        ...

    @Utils.run_once_class
    class Load(object):
        def __init__(self):
            list_args = []
            atributos = vars(Name)
            variaveis_dict = {atributo: valor for atributo, valor in atributos.items() if isinstance(valor, str)}
            
            for variavel in variaveis_dict:
                if variavel != "__module__":
                    icon_name = variaveis_dict[variavel]

                    Data.dict_icons[icon_name] = {Color.LIGHT: None,  Color.DARK : None, "original" : None, Color.BLUE: None, Color.GRAY : None}
                    icon_name_light = Icons.Name.add_suffix(icon_name, Color.LIGHT) 
                    icon_name_dark = Icons.Name.add_suffix(icon_name, Color.DARK) 
                    icon_name_blue = Icons.Name.add_suffix(icon_name, Color.BLUE) 
                    icon_name_gray = Icons.Name.add_suffix(icon_name, Color.GRAY) 

                    Data.dict_icons[icon_name]["original"] = QIcon(u':' + icon_name)
                    Data.dict_icons[icon_name][Color.LIGHT] = QIcon(u':' + icon_name_dark)
                    Data.dict_icons[icon_name][Color.DARK] = QIcon(u':' + icon_name_light)
                    Data.dict_icons[icon_name][Color.BLUE] = QIcon(u':' + icon_name_blue)
                    Data.dict_icons[icon_name][Color.GRAY] = QIcon(u':' + icon_name_gray)

                    if icon_name in Data.dict_icons_clolor:
                        list_args.append(icon_name)

            if list_args:
                Utils.Multiprocessing(list_args, self._target_function, len(list_args))

        def _target_function(self, icon_name : str):
            dict_icon_color : dict[str, str] = Data.dict_icons_clolor[icon_name]
            if not dict_icon_color['color_name'] in Data.dict_icons[icon_name]:
                custom_icon = QIcon(u':' + icon_name)
                custom_icon = Icons.change_color(custom_icon, dict_icon_color['color'])
                Data.dict_icons[icon_name][dict_icon_color['color_name']] = custom_icon

    class Name(Name):
        ...

    @classmethod
    def set_color_icon(cls, icon_name : Name , color_name : str, color : QColor | tuple[int] | list[int] | str):
        Data.dict_icons_clolor[icon_name] = {'color_name': color_name ,'color': color}

    @classmethod
    def to_pixmap(cls, icon : str | QIcon | Icon, new_size : int = None):
        if type(icon) == str:
            icon = QIcon(u':' + icon)

        if new_size:
            return icon.pixmap(new_size)
        original_size = (32, 32)
        if icon.availableSizes():
            original_size = icon.availableSizes()[0]
        return icon.pixmap(original_size)

    class Icon(Icon):
        ...






