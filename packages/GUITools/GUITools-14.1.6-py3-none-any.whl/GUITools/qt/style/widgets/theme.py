# -*- coding: latin -*-

from ..styleSheet import BaseColor
from .base import BaseWidgetStyleSheet, BaseStyleSheet
from PyQt6.sip import isdeleted
from PyQt6.QtGui import QPalette, QIcon
from PyQt6.QtCore import QEvent, QObject, Qt, QRect
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QTextBrowser, QTextEdit, QTreeWidget, QStyledItemDelegate
from typing import Callable
from ..utils import Global

class ThemedIconWidget(QObject):
    def __init__(self, widget: QPushButton | QLabel, icon_leave : Callable[[], QIcon], icon_enter : Callable[[], QIcon], pixmap_size: int = None):
        super().__init__(widget)
        self.widget = widget
        self.theme = Global.theme
        self.is_themed = 'theme' in icon_leave.__name__.lower() or 'theme' in icon_enter.__name__.lower()
        self.active = False
        self.update_data(icon_leave, icon_enter, pixmap_size)

        # Instala o filtro de eventos para capturar enter/leave
        self.widget.installEventFilter(self)

    def update_data(self, icon_leave : Callable[[], QIcon], icon_enter : Callable[[], QIcon], pixmap_size: int = None):
        self.icon_leave = icon_leave
        self.icon_enter = icon_enter
        self.pixmap_size = pixmap_size
        self.apply_icon(self.icon_leave())

    def toggle_active(self):
        self.active = not self.active
        if self.active:
            self.apply_icon(self.icon_enter())
        else:
            self.apply_icon(self.icon_leave())

    def apply_icon(self, icon : QIcon = None):
        if not self.active:
            icon = icon if icon else self.icon_leave()
            if isinstance(self.widget, QPushButton):
                self.widget.setIcon(icon)
            elif isinstance(self.widget, QLabel):
                self.widget.setPixmap(icon.toPixmap(self.pixmap_size))

    def eventFilter(self, obj, event):
        if obj is self.widget:
            if not self.active:
                if event.type() == QEvent.Type.Enter and self.widget.isEnabled():
                    self.apply_icon(self.icon_enter())
                elif event.type() == QEvent.Type.Leave:
                    if isinstance(self.widget, QPushButton) and not self.widget.isChecked():
                        self.apply_icon(self.icon_leave())
                    elif isinstance(self.widget, QLabel):
                        self.apply_icon(self.icon_leave())
                elif obj is self.widget and event.type() == QEvent.Type.Show and self.is_themed:
                    if self.theme != Global.theme:
                        self.apply_icon(self.icon_leave())
                        self.theme == Global.theme

        return super().eventFilter(obj, event)

class ThemedWidget(QObject):
    def __init__(self, widget: QWidget, styleSheet : BaseWidgetStyleSheet | BaseStyleSheet): 
        super().__init__(widget)
        self.widget = widget
        self.theme = Global.theme
        self.styleSheet = styleSheet
        self.widget.installEventFilter(self) 

    def update_style(self):
        if self.theme != Global.theme:
            self.widget.setStyleSheet(self.styleSheet.styleSheet())
            self.theme = Global.theme

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QEvent.Type.Show:
            self.update_style()
        return super().eventFilter(obj, event)  
    
class ThemedTextWidget(QObject):
    def __init__(self, widget: QTextBrowser | QTextEdit): 
        super().__init__(widget)
        self.widget = widget
        self.theme = None
        self.update_style()
        self.widget.installEventFilter(self) 

    def update_style(self):
        if self.theme != Global.theme:
            palette = self.widget.palette()
            palette.setColor(QPalette.ColorRole.PlaceholderText, BaseColor.placeholder.QColor)
            self.widget.setPalette(palette)
            self.theme = Global.theme

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QEvent.Type.Show:
            self.update_style()
        return super().eventFilter(obj, event) 
    
class ThemedTreeWidget(QObject):

    class AlternateBackgroundDelegate(QStyledItemDelegate):
        def __init__(self, parent=None):
            super().__init__(parent)

        def paint(self, painter, option, index):
            custom_color = BaseColor.table_alternate.QColor
            tree_widget : QTreeWidget = option.widget
            item  = tree_widget.itemFromIndex(index)
            should_paint = False

            if item:
                if item.parent() is None:
                    top_index = tree_widget.indexOfTopLevelItem(item)
                    if top_index % 2 != 0: 
                        should_paint = True
                else:
                    top_item = item
                    while top_item.parent():
                        top_item = top_item.parent()
                    top_index = tree_widget.indexOfTopLevelItem(top_item)
                    if top_index % 2 != 0:
                        should_paint = True

            if should_paint:
                full_rect = QRect(
                    option.rect.x(),
                    option.rect.y(),
                    tree_widget.viewport().width() - option.rect.x(),
                    option.rect.height()
                )
                painter.save()
                painter.fillRect(full_rect, custom_color)
                painter.restore()

            super().paint(painter, option, index)

    def __init__(self, widget: QTreeWidget): 
        super().__init__(widget)
        self.widget = widget
        self.widget.setItemDelegate(self.AlternateBackgroundDelegate(self.widget))
        self.theme = None
        self.widget.installEventFilter(self) 

    def update(self):
        if self.theme != Global.theme:
            self.widget.viewport().update()
            self.theme = Global.theme

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QEvent.Type.Show:
            self.update()
        return super().eventFilter(obj, event) 

class WidgetsTheme(object):
    themedWidgets : list[ThemedWidget | ThemedTextWidget] = []
    themedIconWidget : list[ThemedIconWidget] = []
    themedTreeWidget : list[ThemedTreeWidget] = []

    @classmethod
    def set_widget_style_theme(cls, widget : QWidget, styleSheet : BaseWidgetStyleSheet | BaseStyleSheet):
        for w in cls.themedWidgets:
            if w.widget == widget:
                if str(styleSheet) != str(w.styleSheet):
                    w.styleSheet = styleSheet
                    w.widget.setStyleSheet(str(styleSheet))
                    return
        cls.themedWidgets.append(ThemedWidget(widget, styleSheet))

    @classmethod
    def set_icon(cls, widget : QPushButton | QLabel, callable_icon : Callable, hover_callable_icon : Callable = None, pixmap_size : int = None):
        for w in cls.themedIconWidget:
            if w.widget == widget:
                w.update_data(callable_icon, hover_callable_icon, pixmap_size)
                return
        cls.themedIconWidget.append(ThemedIconWidget(widget, callable_icon, hover_callable_icon, pixmap_size))

    @classmethod
    def toggle_icon_active(cls, widget : QPushButton | QLabel):
        for w in cls.themedIconWidget:
            if w.widget == widget:
                w.toggle_active()

    @classmethod
    def set_text_placeholder_text(cls, widget: QWidget):
        for w in cls.themedWidgets:
            if w.widget == widget:
                return
        cls.themedWidgets.append(ThemedTextWidget(widget))

    @classmethod
    def set_tree_widget_alternate_background_color(cls, widget: QTreeWidget):
        for w in cls.themedTreeWidget:
            if w.widget == widget:
                return
        cls.themedTreeWidget.append(ThemedTreeWidget(widget))

    @classmethod
    def update(cls):
        # Filtrar widgets destruídos
        cls.themedWidgets = [w for w in cls.themedWidgets if w.widget and not isdeleted(w.widget)]
        cls.themedIconWidget = [w for w in cls.themedIconWidget if w.widget and not isdeleted(w.widget)]
        cls.themedTreeWidget = [w for w in cls.themedTreeWidget if w.widget and not isdeleted(w.widget)]

        for widget in cls.themedWidgets:
            if widget.widget.isVisible():
                widget.update_style()

        for widget in cls.themedIconWidget:
            if widget.widget.isVisible():
                widget.apply_icon()

        for widget in cls.themedTreeWidget:
            if widget.widget.isVisible():
                widget.update()

        

    



