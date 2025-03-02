import sys
import serial
import threading
import math
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer

# Configurare Serial
SERIAL_PORT = "COM3"
BAUD_RATE = 115200

# Frecvențele note
NOTES = [
    ("C0", 16.35), ("C#0", 17.32), ("D0", 18.35), ("D#0", 19.45), ("E0", 20.60),
    ("F0", 21.83), ("F#0", 23.12), ("G0", 24.50), ("G#0", 25.96), ("A0", 27.50),
    ("A#0", 29.14), ("B0", 30.87), ("C1", 32.70), ("C#1", 34.65), ("D1", 36.71),
    ("D#1", 38.89), ("E1", 41.20), ("F1", 43.65), ("F#1", 46.25), ("G1", 49.00),
    ("G#1", 51.91), ("A1", 55.00), ("A#1", 58.27), ("B1", 61.74), ("C2", 65.41),
    ("C#2", 69.30), ("D2", 73.42), ("D#2", 77.78), ("E2", 82.41), ("F2", 87.31),
    ("F#2", 92.50), ("G2", 98.00), ("G#2", 103.83), ("A2", 110.00), ("A#2", 116.54),
    ("B2", 123.47), ("C3", 130.81), ("C#3", 138.59), ("D3", 146.83), ("D#3", 155.56),
    ("E3", 164.81), ("F3", 174.61), ("F#3", 185.00), ("G3", 196.00), ("G#3", 207.65),
    ("A3", 220.00), ("A#3", 233.08), ("B3", 246.94), ("C4", 261.63), ("C#4", 277.18),
    ("D4", 293.66), ("D#4", 311.13), ("E4", 329.63), ("F4", 349.23), ("F#4", 369.99),
    ("G4", 392.00), ("G#4", 415.30), ("A4", 440.00), ("A#4", 466.16), ("B4", 493.88),
]

def closest_note(freq):
    return min(NOTES, key=lambda note: abs(note[1] - freq))

class TunerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 300)
        self.current_frequency = 440.0
        self.target_frequency = 440.0
        self.smooth_frequency = 440.0
        self.note = "A4"
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 20

        #semicerc
        painter.setPen(QPen(Qt.GlobalColor.black, 4))
        painter.drawArc(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius, 30 * 16, 120 * 16)


        self.smooth_frequency += (self.current_frequency - self.smooth_frequency) * 0.1

        # Indicator ac
        error = self.smooth_frequency - self.target_frequency
        angle = -error * 2
        angle = max(-30, min(30, angle))

        painter.setPen(QPen(Qt.GlobalColor.white, 4))
        painter.drawLine(center.x(), center.y(), center.x() + int(math.sin(math.radians(angle)) * radius),
                         center.y() - int(math.cos(math.radians(angle)) * radius))

    
        painter.setFont(QFont("Arial", 24))
        painter.drawText(center.x() - 30, center.y() + radius - 20, 60, 40, Qt.AlignmentFlag.AlignCenter, self.note)

    def update_frequency(self, freq, target_freq, note):
        self.current_frequency = freq
        self.target_frequency = target_freq
        self.note = note
        self.update()

class NoteDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tuner muzical")
        self.setGeometry(100, 100, 400, 400)
        self.layout = QVBoxLayout()

        self.freq_label = QLabel("Frecvență: ---")
        self.freq_label.setFont(QFont("Arial", 18))
        self.freq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.freq_label)

        self.tuner_widget = TunerWidget()
        self.layout.addWidget(self.tuner_widget)

        self.setLayout(self.layout)
        self.thread = threading.Thread(target=self.read_serial, daemon=True)
        self.thread.start()

    def update_display(self, note, freq, target_freq):
        self.freq_label.setText(f"Frecvență: {freq:.2f} Hz")
        self.tuner_widget.update_frequency(freq, target_freq, note)

    def read_serial(self):
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            while True:
                data = ser.readline().decode().strip()
                if data:
                    try:
                        freq = float(data)
                        note, target_freq = closest_note(freq)
                        self.update_display(note, freq, target_freq)
                    except ValueError:
                        pass
        except serial.SerialException:
            print("Eroare: Nu se poate conecta la ESP32")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteDetectorApp()
    window.show()
    sys.exit(app.exec())
*.cpp linguist-vendored
*.h linguist-vendored
