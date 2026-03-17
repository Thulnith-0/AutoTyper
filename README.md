# 🚀 AutoTyper

<p align="center">
  <img src="assets/icon.ico" width="120" />
</p>

<p align="center">
  Lightweight Python desktop app for controlled text typing automation
</p>

---

## 📸 Preview

<p align="center">
  <img src="assets/screenshot.png" width="700"/>
</p>

---

## ✨ Features

- ⏱️ **Time-based typing**
  - Complete text within a user-defined duration

- 🎛️ **Custom typing behavior**
  - Adjustable speed and rhythm
  - Sentence-aware pauses

- 🧠 **Natural pacing**
  - Smooth typing flow instead of instant paste

- 🖥️ **Modern UI**
  - Built with CustomTkinter
  - Clean dark-mode interface

- ⚡ **Responsive performance**
  - Background threading prevents freezing

- 🛑 **Safety system**
  - Start delay before typing begins
  - Mouse corner emergency stop (failsafe)

---

## 🧰 Tech Stack

- Python  
- CustomTkinter  
- PyAutoGUI  
- Threading  

---

## 📦 Installation

```bash
git clone https://github.com/Thulnith-0/AutoTyper.git
cd AutoTyper
pip install -r requirements.txt
python autotyper.py
```

---

## ▶️ Usage

1. Enter your text  
2. Set completion time  
3. Click **Start**  
4. Switch to your target window before typing begins  

---

## ⚠️ Notes

- Make sure the correct window is selected before typing starts  
- Move your mouse to any screen corner to instantly stop typing  

---

## 📁 Project Structure

```
AutoTyper/
│
├── app/
│   ├── core/
│   ├── ui/
│   └── __init__.py
│
├── assets/
│   ├── icon.ico
│   └── screenshot.png
│
├── autotyper.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Future Improvements

- 🔹 Hotkey support (Start / Stop)
- 🔹 Save & load presets
- 🔹 Progress tracking UI
- 🔹 Typing profiles
- 🔹 UI enhancements

---

## 📄 License

MIT License

---

## ⭐ Support

If you found this project useful, consider giving it a star ⭐