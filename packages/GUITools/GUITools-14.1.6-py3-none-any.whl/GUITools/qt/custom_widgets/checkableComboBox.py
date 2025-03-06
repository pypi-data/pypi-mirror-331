# coding: utf-8

from PyQt6.QtWidgets import (
    QComboBox, QWidget, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFrame,  QCheckBox, QMenu, QWidgetAction, QSizePolicy
)
from PyQt6.QtCore import Qt, QEvent, QCoreApplication
from pydantic import BaseModel
from ..style import Styles

class StyleSheetMenu(Styles.menu):
     def __init__(self):
          super().__init__()
          self.menu.border = Styles.Property.Border(color=Styles.Color.Widget.focus_border, bottom_left_radius=5, bottom_right_radius=0, top_left_radius=0, top_right_radius=0)
          self.menu.background_color.value = Styles.Color.Widget.background

class CustomMenu(QMenu):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Alt:
            event.accept()  
        else:
            super().keyPressEvent(event)
       
class CheckableComboBox(QComboBox):

     class DataItem(BaseModel):
          text: str
          check : bool

     class StyleSheet(Styles.comboBox):
          def __init__(self):
               super().__init__()
               self.listView.itemHover.background_color.value = Styles.Color.table
               self.listView.itemSelectedHover.background_color.value = Styles.Color.table
               self.listView.listView.add_additional_style('border: 0px solid;')

     def __init__(self, initial_check_item : bool = True , placeholder_combo = '', placeholder_new_item = '', *, parent=None):
          super().__init__(parent)
          self.setProperty("popup_open", False)
          self.initial_check_item = initial_check_item
          self.setEditable(True)
          self.lineEdit().setReadOnly(True)
          if placeholder_combo.strip():
               self.lineEdit().setPlaceholderText(placeholder_combo)
          self.placeholder_new_item = placeholder_new_item
          self.lineEdit().installEventFilter(self)
          self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

          self.menu = CustomMenu(self)
          self.menu.aboutToHide.connect(self.resetStyle)
          self.popupWidget = CustomPopup(self)
          self.popupAction = QWidgetAction(self)
          self.popupAction.setDefaultWidget(self.popupWidget)
          self.menu.addAction(self.popupAction)

          Styles.set_widget_style_theme(StyleSheetMenu(), self.menu)
          Styles.set_widget_style_theme(self.StyleSheet(), self)

     def validateNewItem(self, text : str) -> bool:
          return False

     def wheelEvent(self, e):
          e.ignore() 
         
     def eventFilter(self, obj, event):
          if obj == self.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
               self.showPopup()
               return True
          return super().eventFilter(obj, event)
     
     def addItem(self, data : DataItem | dict):
          if isinstance(data, dict):
               data = self.DataItem(**data)
          super().addItem(data.text)
          index = self.count() - 1
          self.setItemData(index, Qt.CheckState.Checked if data.check else Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)

     def addItems(self, *data : DataItem | dict):
          for d in data:
               self.addItem(d)
          self.popupWidget.updateList()
          self.updateText()

     def clear(self):
          super().clear()
          self.popupWidget.listWidget.clear()
          self.updateText()
        
     def showPopup(self):
          self.updatePopupSize()
          point = self.mapToGlobal(self.rect().bottomLeft())
          self.setProperty("popup_open", True)
          self.style().unpolish(self)
          self.style().polish(self)
          self.menu.exec(point)

     def hidePopup(self):
          self.menu.hide()
          self.updateText()

     def resetStyle(self):
          self.setProperty("popup_open", False)
          self.style().unpolish(self)
          self.style().polish(self)

     def updatePopupSize(self):
          line_edit_width = self.width()
          self.popupWidget.setFixedWidth(line_edit_width - 4)
          self.menu.setFixedWidth(line_edit_width)

          content_height = self.popupWidget.listWidget.sizeHintForRow(0) * self.popupWidget.listWidget.count() + 45
          content_height = max(content_height, 72)
          self.popupWidget.setFixedHeight(min(content_height, 300) - 4)
          self.menu.setFixedHeight(min(content_height, 300))

          self.popupWidget.adjustSize()
          self.menu.adjustSize()

          QCoreApplication.processEvents()

     def updateText(self):
          texts = []
          for i in range(self.model().rowCount()):
               item = self.model().item(i)
               if item.checkState() == Qt.CheckState.Checked:
                    texts.append(item.text())
          text = ", ".join(texts)
          words = text.split()
          lines = [" ".join(words[i:i + 4]) for i in range(0, len(words), 4)]
          formatted_text = "\n".join(lines)
          self.setToolTip(formatted_text)
          self.lineEdit().setText(str(text))

     def getItemsData(self) -> list['DataItem']:
          res = []
          for i in range(self.model().rowCount()):
               check = self.model().item(i).checkState()
               res.append(self.DataItem(text=self.model().item(i).text(), check=True if check == Qt.CheckState.Checked else False))
          return res

class ListItemWidget(QWidget):
     def __init__(self, text: str, check_state, remove_callback, check_callback, parent=None):
          super().__init__(parent)
          self.text = text
          self.remove_callback = remove_callback
          self.check_callback = check_callback
          
          self.checkbox = QCheckBox(text, self)
          if not isinstance(check_state, Qt.CheckState):
                    check_state = Qt.CheckState(check_state)
          self.checkbox.setCheckState(check_state)
          self.checkbox.stateChanged.connect(self.on_state_changed)
          
          self.remove_button = QPushButton(self)
          self.remove_button.setObjectName('BtnDelete')
          self.remove_button.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
          self.remove_button.clicked.connect(self.on_remove_clicked)
          Styles.set_icon(self.remove_button, Styles.Resources.lixo.gray, Styles.Resources.lixo.original)
          
          layout = QHBoxLayout(self)
          layout.setContentsMargins(0, 0, 0, 0)
          layout.addWidget(self.checkbox)
          layout.addStretch()
          layout.addWidget(self.remove_button)
          self.setLayout(layout)

     def mousePressEvent(self, event):
          if not self.remove_button.underMouse():  
               new_state = (
                    Qt.CheckState.Unchecked
                    if self.checkbox.checkState() == Qt.CheckState.Checked
                    else Qt.CheckState.Checked
               )
               self.checkbox.setCheckState(new_state)
          super().mousePressEvent(event)
     
     def on_state_changed(self, state):
          self.check_callback(Qt.CheckState(state))
    
     def on_remove_clicked(self):
          self.remove_callback()

class CustomPopup(QFrame):
     class StyleSheet(Styles.Standard.StyleSheet):
          def __init__(self):
               super().__init__()
               
          def style(self):
               return f'''
                    QFrame, QCheckBox {{background-color: {Styles.Color.table}}}
                    QFrame {{{Styles.Property.Border(bottom_left_radius=5, bottom_right_radius=0, top_left_radius=0, top_right_radius=0)}}}
                    {Styles.button(prefix='#BtnAdd').styleSheet(use_class_name=False)}
                    {Styles.button(prefix='#BtnDelete', transparent=True, hover=True).styleSheet(use_class_name=False)}
               '''
           
     def __init__(self, parentComboBox: CheckableComboBox):
          super().__init__(parentComboBox, Qt.WindowType.Popup)
          self.parentComboBox = parentComboBox
          self.setWindowFlags(Qt.WindowType.Popup)
          
          self.listWidget = QListWidget(self)
          self.listWidget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
     
          self.lineEdit = QLineEdit(self)
          if parentComboBox.placeholder_new_item.strip():
               self.lineEdit.setPlaceholderText(parentComboBox.placeholder_new_item)
          self.lineEdit.returnPressed.connect(self.onAddClicked)
          self.addButton = QPushButton(self)
          self.addButton.setObjectName('BtnAdd')
          self.addButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
          self.addButton.clicked.connect(self.onAddClicked)
          Styles.set_icon(self.addButton, Styles.Resources.add.gray, Styles.Resources.add.blue)

          bottomWidget = QFrame(self)
          bottomLayout = QHBoxLayout(bottomWidget)
          bottomLayout.setContentsMargins(2, 2, 2, 2)
          bottomLayout.addWidget(self.lineEdit)
          bottomLayout.addWidget(self.addButton)
          
          layout = QVBoxLayout(self)
          layout.setContentsMargins(2, 2, 2, 2)
          layout.setSpacing(2)
          layout.addWidget(self.listWidget)
          layout.addWidget(bottomWidget)
          self.setLayout(layout)
          self.updateList()
          Styles.set_widget_style_theme(self.StyleSheet(), self)
     
     def updateList(self):
          self.listWidget.clear()
          for i in range(self.parentComboBox.count()):
               text = self.parentComboBox.itemText(i)
               check_state = self.parentComboBox.itemData(i, Qt.ItemDataRole.CheckStateRole)
               
               item = QListWidgetItem(self.listWidget)
               widget = ListItemWidget(
                    text,
                    check_state,
                    remove_callback=lambda i=i: self.removeItem(i),
                    check_callback=lambda state, i=i: self.onItemChecked(i, state),
                    parent=self.listWidget
               )
               item.setSizeHint(widget.sizeHint())
               self.listWidget.addItem(item)
               self.listWidget.setItemWidget(item, widget)
    
     def onItemChecked(self, index, state):
          self.parentComboBox.setItemData(index, state, Qt.ItemDataRole.CheckStateRole)
          self.parentComboBox.updateText()
       
     def removeItem(self, index):
          self.parentComboBox.removeItem(index)
          self.updateList()
          self.parentComboBox.updateText()
          self.parentComboBox.updatePopupSize()
    
     def onAddClicked(self):
          text = self.lineEdit.text().strip()
          if self.parentComboBox.validateNewItem(text) and text.strip():
               self.parentComboBox.addItem(CheckableComboBox.DataItem(text=text, check=self.parentComboBox.initial_check_item))
               self.lineEdit.clear()
               self.updateList()
               self.parentComboBox.updatePopupSize()
               self.parentComboBox.updateText()