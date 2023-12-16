import sys
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLineEdit, QApplication, QWidget, QTextEdit, QInputDialog, QCheckBox, QMessageBox, QMainWindow, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction

# VARIANTE EINS:
# - VERWENDET NICHT ALPYCA Library
# - SONDERN GEHT DIREKT ÜBER HTTP
# - DAZU MUSS ASCOM REMOTE SERVER LAUFEN
# - import requests und jason library
# import requests
# import json
#
# VARIANTE ZWEI:
# - VERWENDET ALPYCA Library
# - import ascom alpaca interface for python
# from alpaca.telescope import *          # py -m pip install alpyca
from myAlpacaTelescope import *
# from myAlpacaDevice import *
from alpaca.exceptions import *
from alpaca.device import *


class MainWindow(QMainWindow):

    # globale Variablen
    MyMount = None # mit Alpyca ist MyMount das Mount Objekt
    slew_rate = 0.0
    slewing = False

    # Verweis auf das Kamera Objekt, damit diese Klasse mit der Kamera kommunizieren kann.
    myCamera = None

    # Verweis auf das Debugging Objekt
    myDebug = None

    myvar = None


    # Signals are notifications emitted by widgets when something happens. That something can be any number 
    # of things, from pressing a button, to the text of an input box changing, to the text of the window changing. 
    # Many signals are initiated by user action, but this is not a rule.
    evtCallback = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 600)
        self.timer = QTimer(self)

        # Hauptlayout
        layout = QVBoxLayout()

        # Connection group
        group_box_connection = QGroupBox("Connection")
        group_layout_connection = QVBoxLayout()

        # Connect Button in Connection Group
        self.button_connect = QPushButton('Connect')
        self.button_connect.clicked.connect(self.button_connect_clicked)
        group_layout_connection.addWidget(self.button_connect)
        group_box_connection.setLayout(group_layout_connection)        
        layout.addWidget(group_box_connection)


        # GET group
        group_box_GET = QGroupBox("GET")
        group_layout_GET = QVBoxLayout()

        self.combo_box_GET = QComboBox()
        # füge die GET Befehle in die Combobox ein
        # die möglichen Methoden werden aus dem Objekt Telescope ausgelesen
        TelescopGetterList, TelescopeSetterList, TelescopeMethodList = self.getMethodsInClass(Telescope)
        for wert in TelescopGetterList: 
            self.combo_box_GET.addItem(wert)
        group_layout_GET.addWidget(self.combo_box_GET)
        self.combo_box_GET.activated.connect(self.onChangecombo_box_GET)

        group_box_GET.setLayout(group_layout_GET)
        layout.addWidget(group_box_GET)



        # PUT group
        group_box_PUT = QGroupBox("PUT")
        group_layout_PUT = QVBoxLayout()

        self.combo_box_PUT = QComboBox()
        # füge die PUT Befehle in die Combobox ein
        # die möglichen Methoden werden aus dem Objekt Telescope ausgelesen
        TelescopGetterList, TelescopeSetterList, TelescopeMethodList = self.getMethodsInClass(Telescope)
        for wert in TelescopeSetterList: 
            self.combo_box_PUT.addItem(wert)
        group_layout_PUT.addWidget(self.combo_box_PUT)
        self.combo_box_PUT.activated.connect(self.onChangecombo_box_PUT)

        # Eingabefelder zu der PUT Gruppe
        self.param1_input = QLineEdit(self)
        # Setze die Standardwerte
        self.param1_input.setText("default1")
        group_layout_PUT.addWidget(self.param1_input)

        self.param2_input = QLineEdit(self)
        self.param2_input.setText("default2")
        group_layout_PUT.addWidget(self.param2_input)


        group_box_PUT.setLayout(group_layout_PUT)
        layout.addWidget(group_box_PUT)





        # Movement group

        # Listbox
        group_box_movement = QGroupBox("Movement")
        group_layout_movement = QVBoxLayout()

        self.combo_box = QComboBox()
        self.combo_box.addItem("0.5sec")
        self.combo_box.addItem("1sec")
        self.combo_box.addItem("2sec")
        group_layout_movement.addWidget(self.combo_box)
        self.combo_box.activated.connect(self.onChangeSlewRateCB)

        self.button_oben = QPushButton('oben')
        self.button_oben.clicked.connect(self.button_oben_clicked)
        group_layout_movement.addWidget(self.button_oben)

        h_layout = QHBoxLayout()
        self.button_links = QPushButton('links')
        self.button_links.clicked.connect(self.button_links_clicked)
        h_layout.addWidget(self.button_links)

        self.button_stop = QPushButton('stop') 
        self.button_stop.clicked.connect(self.button_stop_clicked)  
        h_layout.addWidget(self.button_stop) 

        self.button_rechts = QPushButton('rechts')
        self.button_rechts.clicked.connect(self.button_rechts_clicked)
        h_layout.addWidget(self.button_rechts)

        group_layout_movement.addLayout(h_layout)

        self.button_unten = QPushButton('unten')
        self.button_unten.clicked.connect(self.button_unten_clicked)
        group_layout_movement.addWidget(self.button_unten)

        self.button_calibrate = QPushButton('calibrate')
        self.button_calibrate.clicked.connect(self.button_calibrate_clicked)
        group_layout_movement.addWidget(self.button_calibrate)


        # Deaktivieren der Buttons in der Gruppe "Movement" beim Start des Programms
        self.button_oben.setEnabled(False)
        self.button_links.setEnabled(False)
        self.button_rechts.setEnabled(False)
        self.button_unten.setEnabled(False)
        self.button_stop.setEnabled(False)
        self.button_calibrate.setEnabled(False)

        group_box_movement.setLayout(group_layout_movement)

        layout.addWidget(group_box_movement)



        # Logging group
        group_box_logging = QGroupBox("Logging")
        group_layout_logging = QVBoxLayout()
        self.text_field = QTextEdit()
        self.text_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        group_layout_logging.addWidget(self.text_field)
        group_box_logging.setLayout(group_layout_logging)
        layout.addWidget(group_box_logging)


        # wg_ctrl ist offenbar Hauptobjekt für das Window mit den Objekten Button, Slider, ...
        wg_ctrl = QWidget()
        wg_ctrl.setLayout(layout)

        grid_main = QGridLayout()
        grid_main.setColumnStretch(0, 1)
        grid_main.setColumnStretch(1, 4)
        grid_main.addWidget(wg_ctrl)
        w_main = QWidget()
        w_main.setWindowTitle('PyQt5 App')
        w_main.setLayout(grid_main)
        self.setCentralWidget(w_main)

        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1000)


    def ConnectMyCameraToMyTelescope(self, myNewCamera):
        self.myCamera = myNewCamera
        self.printLoggingInfo("Connected myCamera to MyTelescope")



    def printLoggingInfo(self, logText):
        # Aktuelle Zeit und Datum holen
        jetzt = datetime.now()
        # In String umwandeln
        zeit_string = jetzt.strftime("%d-%m-%Y - %H_%M_%S_%f")
        # baue Logging String zusammen
        finalLogText = zeit_string + " - " + logText

        # zusätzliche Ausgabe im Logging Textfeld
        self.text_field.append(finalLogText)
        if self.myDebug != None:
            self.myDebug.printLoggingText(finalLogText)



    def button_connect_clicked(self):

        # global MyMount

        if self.button_connect.text() == 'Connect':
            self.printLoggingInfo("Button Connect gedrückt") # das bleibt als Hauptstart Logging

            # try to connect Mount
            # real Mount on Port 11111
            # alpaca simulator on port 32323
            self.MyMount = Telescope('127.0.0.1:32323', 0)
            try:
                self.MyMount.Connected = True
                self.printLoggingInfo(f'Connected to {self.MyMount.Name}')
                self.printLoggingInfo(self.MyMount.Description)
            except Exception as e:              # Should catch specific InvalidOperationException
                # couldn't connect to mount
                self.printLoggingInfo(f'exeption: {str(e)}')

            if self.MyMount is not None:
                self.button_connect.setText('Disconnect')
                # Deaktivieren der Buttons in der Gruppe "Movement", wenn der Button "Connect" geklickt wird
                self.button_oben.setEnabled(True)
                self.button_links.setEnabled(True)
                self.button_rechts.setEnabled(True)
                self.button_unten.setEnabled(True)
                self.button_stop.setEnabled(True)
                self.button_calibrate.setEnabled(True)
            else:
                self.printLoggingInfo("Could NOT connect to mount")

        else:
            self.printLoggingInfo("Button Disconnect gedrückt")

            if self.MyMount is not None:
                self.MyMount = None

                self.button_connect.setText('Connect')
                # Aktivieren der Buttons in der Gruppe "Movement", wenn der Button "Disconnect" geklickt wird
                self.button_oben.setEnabled(False)
                self.button_links.setEnabled(False)
                self.button_rechts.setEnabled(False)
                self.button_unten.setEnabled(False)
                self.button_stop.setEnabled(False)
                self.button_calibrate.setEnabled(False)


    def button_oben_clicked(self):
        self.printLoggingInfo("Button DEC/ALT UP gedrückt")
        axis = 1 # axisSecondary	1	Secondary axis (e.g., Declination or Altitude).
        # The rate of motion (deg/sec) about the specified axis
        rate = self.slew_rate 
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # Starte Bewegung
        self.MyMount.MoveAxis(TelescopeAxes.axisSecondary, rate)
        # telescope.PulseGuide(0, 500)


    def button_links_clicked(self):
        self.printLoggingInfo("Button RA/AZ LEFT gedrückt")
        # ascominterface.MoveTo(telescope, 0.01, 0.01, text_field)
        axis = 0 # axisPrimary	0	Primary axis (e.g., Right Ascension or Azimuth).
        # The rate of motion (deg/sec) about the specified axis
        rate = self.slew_rate * (-1.0) # entgegengesetze Richtung
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # Starte Bewegung
        self.MyMount.MoveAxis(TelescopeAxes.axisPrimary, rate)


    def button_rechts_clicked(self):
        self.printLoggingInfo("Button RA/AZ RIGHT gedrückt")
        # ascominterface.MoveTo(telescope, 0.01, 0.01, text_field)
        axis = 0 # axisPrimary	0	Primary axis (e.g., Right Ascension or Azimuth).
        # The rate of motion (deg/sec) about the specified axis
        rate = self.slew_rate
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # starte Bewegung
        self.MyMount.MoveAxis(TelescopeAxes.axisPrimary, rate)


    def button_unten_clicked(self):
        self.printLoggingInfo("Button DEC/ALT DOWN gedrückt")
        # ascominterface.MoveTo(telescope, 0.01, 0.01, text_field)
        axis = 1 # axisSecondary	1	Secondary axis (e.g., Declination or Altitude).
        # The rate of motion (deg/sec) about the specified axis
        rate = -1.0 * self.slew_rate #  entgegengesetzte Richtung
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # starte Bewegung
        self.MyMount.MoveAxis(TelescopeAxes.axisSecondary, rate)


    def button_stop_clicked(self):
        self.printLoggingInfo("Button Stop gedrückt")
        self.MyMount.AbortSlew()
        # globale Variable ändern dass Montierung gestoppt wird
        self.slewing = False


    def button_calibrate_clicked(self):
        self.printLoggingInfo("Button Calibrate gedrückt")
        if self.myCamera.myCameraConnected == False:
            self.printLoggingInfo("Camera NOT connected")
        # else:
            self.printLoggingInfo("1. Take First Picture ")
            self.printLoggingInfo("2. Move Mount to +X")
            # Achtung => rauscht durch
            self.MyMount.PulseGuide(GuideDirections.guideEast, 1500)
            # warte auf Ende
            while self.MyMount.IsPulseGuiding == True:
                self.printLoggingInfo("2b. Waiting for ending Pulse Guide ")    
            self.printLoggingInfo("3. Take Second Picture ")
            self.printLoggingInfo("4. Move Mount to +Y ")
            self.MyMount.PulseGuide(GuideDirections.guideNorth, 1500)
            self.printLoggingInfo("5. Take Thrid Picture ")
            self.printLoggingInfo("6. Move Mount to -Y ")
            self.MyMount.PulseGuide(GuideDirections.guideSouth, 1500)            
            self.printLoggingInfo("7. Move Mount to -X ")
            self.MyMount.PulseGuide(GuideDirections.guideWest, 1500)            
            self.printLoggingInfo("8. Take Fourth Picture ")
    


    def onChangeSlewRateCB(self):
        # Definiere die möglichen Slew Rates
        slew_rates = [0.5, 1.0, 2.0]
        # Welcher Index wurde in der Combobox ausgewählt
        index = self.combo_box.currentIndex()
        # Setze nun die aktuelle slew_rate
        self.slew_rate = slew_rates[index]
        # Loggingdaten ausgeben
        self.printLoggingInfo(f"slew_rate {self.slew_rate} changed")



    def onChangecombo_box_GET(self):
        # Welcher Index wurde in der Combobox ausgewählt
        index = self.combo_box_GET.currentIndex()
        # Welcher Befehl ist das
        methodenname = self.combo_box_GET.itemText(index)
        # führe jetzt den Befehl aus
        # response = self.MyMount.CallbackMyTelescope(methodenname)
        response = getattr(self.MyMount, methodenname) # GET Methode ohne Parameter
     
        # Loggingdaten ausgeben
        self.printLoggingInfo(f"ComboBox GET request: {methodenname}")
        self.printLoggingInfo(f"ComboBox GET response: {response}")


    def onChangecombo_box_PUT(self):
        # Welcher Index wurde in der Combobox ausgewählt
        index = self.combo_box_PUT.currentIndex()
        # Welcher Befehl ist das
        methodenname = self.combo_box_PUT.itemText(index)

        # lasse den Nutzer nun notwendige Parameter eingeben
        # Öffne ein Texteingabefeld und speichere den eingegebenen Wert in param1_input
        text, ok = QInputDialog.getText(self, 'Texteingabe', 'Bitte geben Sie einen Wert ein:')
        if ok:
            self.param1_input.setText(text)
        else:
            self.param1_input.setText("")

        newDirection = GuideDirections.guideNorth
        funktion = getattr(self.MyMount, methodenname)
        response = funktion(newDirection, 100) # PUT Methode mit Parametern !achte auf die übergebenen Variablen
       
        # Loggingdaten ausgeben
        self.printLoggingInfo(f"ComboBox PUT request: {methodenname}")
        self.printLoggingInfo(f"ComboBox PUT response: {response}")


    def onTimer(self):
        if self.MyMount != None:
            if self.slewing == True:
                self.printLoggingInfo(f"mount slewing with {self.slew_rate}")
            if self.MyMount.IsPulseGuiding == True:
                self.printLoggingInfo(f"mount pulseguiding with {self.slew_rate}")    
        


    def getMethodsInClass(self, myClass):
        """ returns a listof methods of the given class.
              
        Args:
            myClass (class): class which methods shall be identified
        
        Returns:
            List of methods

        """
        method_list = dir(myClass)
        getter_list = [method for method in method_list if isinstance(getattr(myClass, method), property) and getattr(myClass, method).fget is not None]
        setter_list = [method for method in method_list if isinstance(getattr(myClass, method), property) and getattr(myClass, method).fset is not None]
        method_list = [method for method in method_list if method not in getter_list and method not in setter_list]

        # wieviele Parameter hat eine Setter Methode
        for setter in setter_list:
            num_params = getattr(myClass, setter).fset.__code__.co_argcount - 1
            print(f"Setter-Methode {setter} hat {num_params} Parameter.")

        print("Methoden:")
        print(method_list)
        print("Getter:")
        print(getter_list)
        print("Setter:")
        print(setter_list)

        return getter_list, setter_list, method_list


    @staticmethod
    def eventCallBack(nEvent, self):
        '''callbacks come from omegonprocam.dll/so internal threads, so we use qt signal to post this event to the UI thread'''
        self.printLoggingInfo("eventCallBack(nEvent, self)")
        self.evtCallback.emit(nEvent)

    def onevtCallback(self, nEvent):
        '''this run in the UI thread'''
        self.printLoggingInfo("onevtlCallback()")





if __name__ == '__main__':
    # QApplication specializes QGuiApplication with some functionality needed for QWidget -based applications. 
    # It handles widget specific initialization, finalization. For any GUI application using Qt, there is 
    # precisely one QApplication object, no matter whether the application has 0, 1, 2 or more windows at 
    # any given time.
    app = QApplication(sys.argv)    
    w = MainWindow()    
    w.show()
        
    sys.exit(app.exec_())