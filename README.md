# 🏭 AI-Powered Industrial IoT Machine Monitoring System

An end-to-end condition monitoring platform designed for real-time machinery health tracking, failure prediction, and maintenance log inspection. The system captures multi-sensor edge telemetry using an **ESP32**, streams JSON data to a **Firebase Realtime Database**, and visualizes real-time metrics alongside historical maintenance records on an interactive **Streamlit** web dashboard.

---

## ✨ Key Features

* **Real-Time Edge Telemetry:** Samples live temperature (°C) and vibration magnitude (m/s²) every second.
* **Automated Safety Thresholds:** Triggers visual critical alert banners on the dashboard if temperature exceeds **45°C** or vibration magnitude exceeds **15 m/s²**.
* **Interactive Maintenance Inspection:** Filters historical workshop records (`workshop.csv`) by Work Order / Deme Number and displays machine defect breakdowns.
* **AI Technical Assistant:** Rule-based diagnostic helper module offering instant repair recommendations and check actions based on recorded defect logs.
* **Custom Hardware Design:** Built on a custom-soldered Zero PCB with modular sensor routing.

---

## 🛠️ Tech Stack

* **Hardware:** ESP32 Microcontroller, MPU6050 Accelerometer (I2C), DS18B20 Temperature Probe (OneWire).
* **Firmware:** Embedded C++ (Arduino Framework).
* **Cloud Infrastructure:** Firebase Realtime Database (HTTPS REST API endpoints).
* **Frontend Dashboard:** Python 3.x, Streamlit, Pandas, Requests.
* **Testing & DevOps:** Pytest, Git & GitHub Actions.

---

## 📂 Repository Structure

```text
├── 510_ABW.py          # Main Streamlit dashboard application
├── 510code.ino         # ESP32 C++ firmware (sensor acquisition & REST telemetry)
├── workshop.csv        # Historical maintenance logs dataset
├── tests/              # Unit testing suite
│   └── test_app.py     # Streamlit and helper function tests
├── .gitignore          # Git exclusion rules
└── README.md           # Project documentation
