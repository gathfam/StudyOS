# StudyOS

StudyOS adalah aplikasi workspace produktivitas berbasis desktop yang dirancang untuk membantu mahasiswa mengatur tugas, mencatat materi, dan menjaga fokus belajar dalam satu sistem yang sederhana, ringan, dan modular.

## Main Goals

* lightweight
* offline-first
* modular architecture
* scalable foundation
* fokus pada workflow belajar mahasiswa

---

# Tech Stack

| Technology   | Usage                     |
| ------------ | ------------------------- |
| Python 3.12+ | Main programming language |
| PySide6      | Desktop UI Framework      |
| SQLite       | Local database            |
| Git + GitHub | Version control           |

---

# Current Phase

## Phase 1 — Foundation Setup

Focus:

* project structure
* navigation system
* SQLite integration
* event bus
* modular architecture
* reusable UI foundation

Target:

* app launch successfully
* sidebar navigation works
* database initialized
* stable code structure
* integration-ready architecture

---

# Project Structure

```text
studyos/
│
├── core/
│   ├── database/
│   ├── events/
│   ├── services/
│   └── utils/
│
├── modules/
│   ├── planner/
│   ├── deadlines/
│   ├── notes/
│   ├── pomodoro/
│   └── progress/
│
├── ui/
│   ├── pages/
│   ├── widgets/
│   ├── themes/
│   └── main_window.py
│
├── assets/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Architecture

```text
UI Layer
   ↓
Module Layer
   ↓
Service Layer
   ↓
Database Layer (SQLite)
```

## Layer Responsibilities

### UI Layer

Responsible for:

* windows
* navigation
* widgets
* user interaction

### Module Layer

Responsible for:

* feature modules
* controller logic
* communication between UI and services

### Service Layer

Responsible for:

* business logic
* database interaction
* event handling

### Database Layer

Responsible for:

* SQLite connection
* schema
* data persistence

---

# Features (Planned)

* Planner / Task Management
* Deadlines Tracker
* Notes System
* Pomodoro Timer
* Progress Tracking

---

# Event System

StudyOS menggunakan event bus sederhana untuk komunikasi antar module.

Supported events:

* task_created
* task_completed
* deadline_added
* note_created
* pomodoro_finished

---

# Git Workflow

## Branch Structure

```text
main
develop
feature/database
feature/ui
feature/modules
```

## Rules

* Jangan push langsung ke `main`
* Semua feature merge ke `develop`
* Gunakan commit message yang jelas
* Pull latest changes sebelum coding

Example commits:

```bash
feat: add sidebar navigation
feat: create sqlite schema
fix: resolve stacked widget issue
```

---

# Setup Instructions

## Clone Repository

```bash
git clone <repository-url>
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Application

```bash
python main.py
```

---

# Team Roles

| Member   | Responsibility        |
| -------- | --------------------- |
| Nabil Gathfan Putra Mulyana | Core & Infrastructure |
| Putri Balqis | UI & Navigation       |
| Raja Maulidinsyah Putra | Modules & Integration |

---

# Phase 1 Success Criteria

* application launches successfully
* sidebar navigation works
* SQLite connection stable
* database schema initialized
* event bus functional
* reusable card widget available
* dummy pages rendered
* modular architecture stable

---

# Notes

Phase 1 focuses on:

* stable foundation
* clean architecture
* integration workflow

Not:

* visual perfection
* advanced features
* overengineering

---
