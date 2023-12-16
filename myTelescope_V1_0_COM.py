import sys
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QTextEdit, QDesktopWidget, QCheckBox, QMessageBox, QMainWindow, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction

import ascominterface

class MainWindow(QMainWindow):

    # globale Variablen
    ALPACA = False
    telescope = None
    slew_rate = 0.0
    slewing = False

    # Verweis auf das Kamera Objekt, damit diese Klasse mit der anderen kommunizieren kann.
    myCamera = None

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
        print(finalLogText)

        # zusätzliche Ausgabe im Logging Textfeld
        self.text_field.append(finalLogText)



    def button_connect_clicked(self):

        global telescope

        if self.button_connect.text() == 'Connect':
            self.printLoggingInfo("Button Connect gedrückt") # das bleibt als Hauptstart Logging

            # Wenn ALPACA == True dann wird ASCOM ALPACA verwendet
            # Wenn ALPACA = False dann wird ASCAM COM verwendet
            if self.ALPACA == True:
                telescope = self.Telescope('127.0.0.1:11111', 0) # Local Omni Simulator
                telescope.Connected = True
            else:
                telescope = ascominterface.ConnectTelescope(self.text_field)

            if telescope is not None:
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
            self.printLoggingInfo("Button Disconnect gedrückt") # das bleibt als Hauptende Logging

            if telescope is not None:
                ascominterface.DisconnectTelescope(telescope)
                telescope = None

                self.printLoggingInfo("Connect")
                self.button_connect.setText('Connect')
                # Aktivieren der Buttons in der Gruppe "Movement", wenn der Button "Disconnect" geklickt wird
                self.button_oben.setEnabled(False)
                self.button_links.setEnabled(False)
                self.button_rechts.setEnabled(False)
                self.button_unten.setEnabled(False)
                self.button_stop.setEnabled(False)


    def button_oben_clicked(self):
        self.printLoggingInfo("Button DEC/ALT UP gedrückt")
        axis = 1 # axisSecondary	1	Secondary axis (e.g., Declination or Altitude).
        # The rate of motion (deg/sec) about the specified axis
        rate = self.slew_rate 
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # Starte Bewegung
        ascominterface.MoveAxis(telescope, axis, rate, self.text_field)
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
        ascominterface.MoveAxis(telescope, axis, rate, self.text_field)


    def button_rechts_clicked(self):
        self.printLoggingInfo("Button RA/AZ RIGHT gedrückt")
        # ascominterface.MoveTo(telescope, 0.01, 0.01, text_field)
        axis = 0 # axisPrimary	0	Primary axis (e.g., Right Ascension or Azimuth).
        # The rate of motion (deg/sec) about the specified axis
        rate = self.slew_rate
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # starte Bewegung
        ascominterface.MoveAxis(telescope, axis, rate, self.text_field)


    def button_unten_clicked(self):
        self.printLoggingInfo("Button DEC/ALT DOWN gedrückt")
        # ascominterface.MoveTo(telescope, 0.01, 0.01, text_field)
        axis = 1 # axisSecondary	1	Secondary axis (e.g., Declination or Altitude).
        # The rate of motion (deg/sec) about the specified axis
        rate = -1.0 * self.slew_rate #  entgegengesetzte Richtung
        # globale Variable ändern dass Montierung bewegt wird
        self.slewing = True
        # starte Bewegung
        ascominterface.MoveAxis(telescope, axis, rate, self.text_field)


    def button_stop_clicked(self):
        self.printLoggingInfo("Button Stop gedrückt")
        ascominterface.AbortSlew(telescope, self.text_field)
        # globale Variable ändern dass Montierung gestoppt wird
        self.slewing = False


    def button_calibrate_clicked(self):
        self.printLoggingInfo("Button Calibrate gedrückt")
        if self.myCamera.myCameraConnected == False:
            self.printLoggingInfo("Camera NOT connected")
        else:
            self.printLoggingInfo("1. Take First Picture ")
            self.printLoggingInfo("2. Move Mount to +X")
            self.printLoggingInfo("3. Take Second Picture ")
            self.printLoggingInfo("4. Move Mount to +Y ")
            self.printLoggingInfo("5. Take Thrid Picture ")
            self.printLoggingInfo("6. Move Mount to -Y ")
            self.printLoggingInfo("7. Move Mount to -X ")
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




    def onTimer(self):
        if self.slewing == True:
            self.printLoggingInfo(f"mount slewing with {self.slew_rate}")





    @staticmethod
    def eventCallBack(nEvent, self):
        '''callbacks come from omegonprocam.dll/so internal threads, so we use qt signal to post this event to the UI thread'''
        print("eventCallBack(nEvent, self)")
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