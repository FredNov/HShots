from PySide6 import QtWidgets
import hou, os, re, toolutils, subprocess, pyperclip
from PySide6 import QtCore

class HShots (QtWidgets.QWidget):
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.resize(295, 193)
        #hou.qt.styleSheet()
        main = QtWidgets.QVBoxLayout()
        shotLay = QtWidgets.QHBoxLayout()
        btns = QtWidgets.QHBoxLayout()
        btns2 = QtWidgets.QHBoxLayout()
        self.coll = QtWidgets.QGroupBox('Settings')
        self.coll.setCheckable(True)
        self.coll.setChecked(True)
        vbox =  QtWidgets.QVBoxLayout()
        self.shots = QtWidgets.QTreeWidget()
        self.shots.setColumnCount(6)
        self.shots.setHeaderLabels(['Shot','Range','Camera','Bundle','Take','Comment'])
        self.shots.setSortingEnabled(0) 
        self.shots.setColumnWidth (0, 200)
        self.shots.setColumnWidth (2, 300)
        self.shots.setIndentation(0)
        self.shots.setItemsExpandable(0)
        self.ln_name = QtWidgets.QLineEdit()
        self.ln_notes = QtWidgets.QLineEdit()
        self.ln_name.setPlaceholderText('Shot name')
        self.ln_notes.setPlaceholderText('Additional notes')
        self.ln_begin = QtWidgets.QLineEdit()
        self.ln_end = QtWidgets.QLineEdit()
        self.ln_begin.setPlaceholderText('Start Frame')
        self.ln_end.setPlaceholderText('End Frame')
        self.ln_begin.setInputMask('00000000')
        self.ln_end.setInputMask('00000000')
        self.combo_cam = QtWidgets.QComboBox()
        self.combo_cam.setMaxVisibleItems(6)
        self.combo_bundle = QtWidgets.QComboBox()
        self.combo_bundle.setMaxVisibleItems(6)
        self.combo_takes = QtWidgets.QComboBox()
        self.combo_takes.setMaxVisibleItems(6)
        self.ch = QtWidgets.QHBoxLayout()
        self.ch_cam = QtWidgets.QCheckBox('Camera')
        self.ch_bundle = QtWidgets.QCheckBox('Bundle')
        self.ch_flipbook = QtWidgets.QCheckBox('Flipbook')
        self.ch_hide = QtWidgets.QCheckBox('Hide Other')
        self.ch_cam.setCheckState(QtCore.Qt.Checked)
        self.ch_bundle.setCheckState(QtCore.Qt.Checked)
        self.ch_flipbook.setCheckState(QtCore.Qt.Checked)
        self.ch_hide.setCheckState(QtCore.Qt.Unchecked)
        self.ch_hide.setDisabled(0)
        self.ch.addWidget(self.ch_cam)
        self.ch.addWidget(self.ch_bundle)
        self.ch.addWidget(self.ch_hide)
        self.ch.addWidget(self.ch_flipbook)
        self.btn_addShot = QtWidgets.QPushButton('Add')
        self.btn_upd = QtWidgets.QPushButton('Update')
        self.btn_up = QtWidgets.QPushButton('<   Move UP')
        self.btn_down = QtWidgets.QPushButton('Move DOWN   >')
        self.btn_delShot = QtWidgets.QPushButton('Delete')
        self.btn_upd_list = QtWidgets.QPushButton('Update List')
        shotLay.addWidget(self.ln_name)
        shotLay.addWidget(self.ln_begin)
        shotLay.addWidget(self.ln_end)
        shotLay.addWidget(self.combo_cam)
        shotLay.addWidget(self.combo_bundle)
        shotLay.addWidget(self.combo_takes)
        btns.addWidget(self.btn_addShot)
        btns.addWidget(self.btn_upd)
        btns.addWidget(self.btn_delShot)
        btns2.addWidget(self.btn_up) 
        btns2.addWidget(self.btn_down)
        btns2.addLayout(self.ch) 
        vbox.addLayout(btns2)
        vbox.addLayout(shotLay)
        vbox.addWidget(self.ln_notes)
        vbox.addLayout(btns)
        vbox.addWidget(self.btn_upd_list)
        self.coll.setLayout(vbox)
        main.addWidget(self.shots)
        main.addWidget(self.coll)

        self.coll.toggled.connect(lambda: self.cGroup(self.coll))
        self.setLayout(main)
        self.setProperty("houdiniStyle", True)


        self.btn_addShot.clicked.connect(self.addShot)
        self.ch_hide.clicked.connect(self.hide_toggle)
        self.ch_bundle.clicked.connect(self.hide_disable)
        self.btn_delShot.clicked.connect(self.deleteItem)
        self.btn_upd_list.clicked.connect(self.updateList)
        self.btn_up.clicked.connect(self.moveUp)
        self.btn_down.clicked.connect(self.moveDown)
        self.btn_upd.clicked.connect(self.updateShot)
        self.shots.itemClicked.connect(self.setShot)
        self.shots.itemDoubleClicked.connect(self.copyCam)
        self.updateList()
    
    def cGroup(self, ctrl):
        state = ctrl.isChecked()
        if state:
            ctrl.setFixedHeight(ctrl.sizeHint().height())
        else:
            ctrl.setFixedHeight(30) 

    def copyCam(self):
        selected = self.shots.selectedItems()
        if not selected:
            return
        s=selected[0]
        pyperclip.copy(s.text(2).rstrip())

    def setShot(self):
        print("setShot method called")
        selected = self.shots.selectedItems()
        if not selected:
            return
        s=selected[0]
        name=s.text(0)
        fr=list(map(int, re.findall(r'(\d+)',s.text(1))))
        #fr=map(int, re.findall(r'(\d+)',s.text(1)))
        combo_cam=s.text(2).rstrip()
        bundle=s.text(3).rstrip()
        take=s.text(4).rstrip()
        notes=s.text(5).rstrip()
        
        # Add print statements to print the values of variables
        #print('name:', name)
        #print('fr:', fr)
        #print('combo_cam:', combo_cam)
        #print('bundle:', bundle)
        #print('take:', take)
        #print('notes:', notes)

        self.ln_name.setText(name) 
        self.ln_begin.setText(str(fr[0])) 
        self.ln_end.setText(str(fr[1])) 
        self.combo_cam.setCurrentIndex(self.combo_cam.findText(combo_cam))
        self.ln_notes.setText(notes)
        self.combo_bundle.setCurrentIndex(self.combo_bundle.findText(bundle))    
        self.combo_takes.setCurrentIndex(self.combo_takes.findText(take))
        hou.playbar.setPlaybackRange(min(fr), max(fr))
        hou.setFrame(min(fr))
        if self.ch_flipbook.isChecked():
            viewer=toolutils.sceneViewer()
            settings=viewer.flipbookSettings()
            settings.frameRange(fr)
        if combo_cam !='Camera' and self.ch_cam.isChecked() :
            camera_node=hou.node(combo_cam)
            if camera_node:
                hou.ui.paneTabOfType(hou.paneTabType.SceneViewer, 0).curViewport().setCamera(camera_node)
                try:
                    camera_node.parm('vcomment').eval()
                except:
                    camera_node.addSpareParmTuple(hou.StringParmTemplate('vcomment', 'Viewport Comment', 1, ''))
                camera_node.parm('vcomment').set('Name: '+name+'\n'+'Camera: '+combo_cam+' ( '+str(min(fr))+'-'+str(max(fr))+'f ) '+str(hou.fps())+'fps '+str(camera_node.parm('resx').eval())+'x'+str(camera_node.parm('resy').eval())+'px\n'+'Notes: '+notes)
                camera_node.setCurrent(True, True)
        else:
            hou.ui.paneTabOfType(hou.paneTabType.SceneViewer, 0).curViewport().homeAll()
        if bundle!='No Bundle':
            if self.ch_bundle.isChecked():
                displNodes=hou.nodeBundle(bundle).nodes()
                hideNodes=hou.node('/obj').children()
                for n in hideNodes:
                    try:
                        n.setDisplayFlag(False)
                    except:
                        pass
                hou.clearAllSelected()
                for n in displNodes:
                    try:
                        n.setDisplayFlag(True)
                    except:
                        pass
                    n.setSelected(1, clear_all_selected=0, show_asset_if_selected=0)

                if self.ch_hide.isChecked(): 
                    hou.clearAllSelected()
                    nds=hou.nodeBundle(bundle).nodes()
                    for n in nds:
                        n.setSelected(1, clear_all_selected=0, show_asset_if_selected=0)
                    self.hide(nds)
        if take!='No Take':
            hou.takes.setCurrentTake(hou.takes.findTake(take))
        else:
            hou.takes.setCurrentTake(hou.takes.rootTake())
        print()

    def saveFile(self):
        pth=hou.getenv('HIP')+'\\shots.txt'
        file = open(pth, 'w+')
        it = QtWidgets.QTreeWidgetItemIterator(self.shots)
        while it.value():
            data=[]
            for c in range(0,6):
                val=it.value().text(c)
                if c<5:
                    val=val+r'***'
                data.append(val)
            file.write(''.join(data)+'\n')
            next(it)     
        file.close()

    def loadFile(self):
        pth=hou.getenv('HIP')+'\\shots.txt'
        if os.path.exists(pth):
            file = open(pth, 'r')
            self.shots.clear()
            data = file.readlines()
            s=0
            for i in data:
                line = i.rstrip()
                if line:
                    data=i.split(r'***')
                    item = QtWidgets.QTreeWidgetItem(self.shots,data)
            file.close()
            self.resz()

    def resz(self):
        for t in range(0,6):
            self.shots.resizeColumnToContents(t) 
            if t<5:
                self.shots.setColumnWidth(t,self.shots.columnWidth(t)+20)
        it = QtWidgets.QTreeWidgetItemIterator(self.shots)
        while it.value():
            for t in range(0,6):
                it.value().setTextAlignment(t, QtCore.Qt.AlignCenter)
            it.value().setTextAlignment(5, QtCore.Qt.AlignLeft)
            next(it)

    def assemblehotLine(self):
        shotline=[]
        if len(self.ln_begin.text())>0 and len(self.ln_end.text())>0:
            if len(self.ln_name.text())>0:
                shotline.append(self.ln_name.text())
            else:
                shotline.append(' ')   
            shotline.append(self.ln_begin.text()+' - '+self.ln_end.text())
            shotline.append(self.combo_cam.currentText())
            shotline.append(self.combo_bundle.currentText())
            shotline.append(self.combo_takes.currentText())
            if len(self.ln_notes.text())>0:
                shotline.append(self.ln_notes.text())
            else:
                shotline.append('None')
            shotline=r'***'.join(shotline)
            return shotline
    
    def addShot(self):
        shotline = self.assemblehotLine()
        if shotline is None:
            return
        data=shotline.split(r'***')
        item=QtWidgets.QTreeWidgetItem(self.shots,data)
        self.saveFile()
        self.updateList()

    def updateShot(self):
        selected = self.shots.selectedItems()
        if not selected:
            return
        item=selected[0]
        root = self.shots.invisibleRootItem()
        root.removeChild(item)
        shotline = self.assemblehotLine()
        if shotline is None:
            return
        data=shotline.split(r'***')
        item=QtWidgets.QTreeWidgetItem(self.shots,data)
        self.saveFile()
        self.updateList()

    def updateList(self): 
        self.loadFile()
        nodes=['Camera']
        bundles=['No Bundle']
        takes=[]
        allnodesIterate=hou.node('/').allSubChildren(True)
        for node in allnodesIterate:
            if node.type().nameWithCategory()=='Object/cam':
                nodes.append(node.path())
        self.combo_cam.clear()
        self.combo_cam.addItems(nodes)
        bndls=hou.nodeBundles()
        for b in bndls:
            bundles.append(b.name())
        tks=hou.takes.takes()
        for t in tks:
            takes.append(t.name())
        self.combo_bundle.clear()
        self.combo_bundle.addItems(bundles)
        self.combo_takes.clear()
        takes.sort()
        takes=['No Take']+takes
        self.combo_takes.addItems(takes)
        self.ln_name.clear() 
        self.ln_begin.clear()  
        self.ln_end.clear() 
        self.ln_notes.clear()
        self.resz()

    def deleteItem(self):
        selected = self.shots.selectedItems()
        if not selected:
            return
        item=selected[0]
        root = self.shots.invisibleRootItem()
        for item in self.shots.selectedItems():
            (item.parent() or root).removeChild(item)
        self.saveFile()
        self.resz()

    def moveUp(self):
        selected = self.shots.selectedItems()
        if not selected:
            return
        item=selected[0]
        root = self.shots.invisibleRootItem()
        index=root.indexOfChild(item)
        shts=root.childCount()
        if (index-1>=0):
            root.removeChild(item)
            root.insertChild(index-1, item)
            self.saveFile()
            self.shots.setCurrentItem(item, 0)

    def moveDown(self):    
        selected = self.shots.selectedItems()
        if not selected:
            return
        item=selected[0]
        root = self.shots.invisibleRootItem()
        index=root.indexOfChild(item)
        shts=root.childCount()
        if (index+1<shts):
            root.removeChild(item)
            root.insertChild(index+1, item)
            self.saveFile()
            self.shots.setCurrentItem(item, 0)

#------------------------ISOLATE----------------------

    def hide(self,nodes):
        allnodes = hou.node('/obj/').children() 

        for nd in allnodes:

            if nd not in nodes:
                try:
                    nd.setDisplayFlag(0)
                    nd.hide(1)
                except:
                    pass
            else:
                try:
                    nd.setDisplayFlag(1)
                    nd.hide(0)
                except:
                    pass

    def hide_disable(self):
        if self.ch_bundle.isChecked():  
            self.ch_hide.setDisabled(0)
        else:
            self.ch_hide.setDisabled(1)

    def hide_toggle(self):
        if self.ch_hide.isChecked():
            self.setShot()
        else:
            nodes = hou.node('/obj').children() 
            for nd in nodes:
                nd.hide(0)