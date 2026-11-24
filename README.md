# EGG-Ninja-
A Python-based Fruit/Egg Ninja style vision game built with OpenCV, MediaPipe Hand Tracking, Pygame Audio, and NumPy. Slice items with your fingers, avoid bombs, and watch characters scream and shatter!


# 🥚 Egg Ninja - Hand Tracking Slice Game

An interactive, computer vision-based arcade game inspired by Fruit Ninja, built in Python. Players use their hand gestures (tracked via MediaPipe) to slice flying eggs and characters while avoiding dangerous bombs, complete with dynamic audio effects and progressive difficulty scaling!

---

## 🎮 Features
- **Hand Tracking Integration:** Powered by `cvzone` and `MediaPipe` to track your index fingertip in real-time. Make a fist to disable your cutting blade!
- **Dynamic Character System:** Diverse character presets with randomized ethnicities, hairstyles, outfits, and dramatic screaming expressions when sliced.
- **Physics & Particle Slicing:** Slicing splits objects into animated halves and exploding body pieces (head, torso, arms, legs).
- **Progressive Difficulty:** Launch speed and gravity dynamically scale up every 5 seconds.
- **Audio Management:** Background music loops (`pygame.mixer`), custom sound effects for slicing/screaming, and an immersive Game Over state.
- **Window Resizing Support:** Fully adjustable window resolution.

---

## 🛠️ Prerequisites & Installation

Make sure you have **Python 3.10+** (or Python 3.14 compatible environment) installed on your system.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/egg-ninja.git
   cd egg-ninja
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # venv\Scripts\activate     # On Windows
   ```

3. **Install the required packages:**
   > **Note for Linux / Raspberry Pi / Ubuntu users:** Make sure you have SDL2 development libraries installed first if you encounter audio/pygame compilation issues.
   
   Run the following pip command to install all necessary dependencies:
   ```bash
   pip install opencv-python mediapipe numpy pygame-ce cvzone
   ```
   *(If standard `pygame` gives compilation errors on newer Python versions, `pygame-ce` is used as a drop-in robust alternative).*

---

## 🎵 Audio Assets Setup
Ensure you place the following audio files in the project root directory (alongside `egg_ninja.py`):
- `bgm.mp3` (Background music)
- `scream.wav` (Character scream sound effect)
- `gameover.wav` (Game over sound effect)

---

## 🚀 How to Run
Run the main game script using:
```bash
python egg_ninja.py
```

- **Controls:**
  - Move your index finger in front of the webcam to slice items.
  - Make a **fist** to pause/disable the blade.
  - Press **`R`** to restart when Game Over.
  - Press **`Q`** to quit.

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
```
