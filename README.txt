# 🐸 Frogger v1.0

*(Scroll down for the Spanish version / Desplázate hacia abajo para la versión en español)*

A modernized and highly polished clone of the classic **Frogger** arcade game, fully developed in Python using the Pygame library and an object-oriented architecture.

This project goes beyond recreating the classic mechanics of dodging traffic and crossing rivers. It integrates advanced concepts of "Game Juice", local data persistence, and a clean architecture based on Finite State Machines (FSM).

## ✨ Key Features

* **State Machine Architecture (FSM):** Smooth and isolated transitions between `MenuState`, `GameplayState`, and `GameOverState`.
* **Classic & Modern Mechanics:**
  * Dynamic vehicle traffic with varying speeds and hitboxes.
  * Interactive river featuring logs, turtles (with timer-based submersion), and crocodiles (with lethal jaw hitboxes).
  * Patrolling enemies (Snakes) with automatic sprite flipping.
  * Autonomous coin spawners for extra points with a limited lifespan.
* **Game Feel & Game Juice:** * Sine wave (`math.sin`) breathing and blinking effects for UI elements.
  * Slot-machine style animated scoring using Linear Interpolation (Lerp).
  * Floating pop-up texts with Alpha Channel fading when scoring points.
* **Data Persistence:** Automatic local saving of the *High Score* using `.json` files.
* **Infinite Scaling:** Global game speed increases by 15% each time the 5 goal slots are filled.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Graphics & Audio Engine:** Pygame
* **Native Libraries:** `math` (UI animations), `json` (data persistence), `os` (file routing), `random` (spawn logic).
* **Base Framework:** `arcade_machine_sdk`

## 🎮 Controls

| Key | Action |
| :--- | :--- |
| `Arrows (Up, Down, Left, Right)` | Move Frog / Navigate Menus |
| `Enter` | Select menu option |
| `P` / `ESC` | Pause Game |
| `G` | *(Debug)* Toggle God Mode |
| `L` | *(Debug)* Add Extra Lives |


1. Clone this repository to your local machine:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/frogger-arcade-clone.git](https://github.com/YOUR_USERNAME/frogger-arcade-clone.git)
