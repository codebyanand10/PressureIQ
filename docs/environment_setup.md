# PressureIQ — Environment Setup Guide

**Project:** PressureIQ  
**Supported Platforms:** Windows (PowerShell / CMD), Linux (Bash), macOS (Zsh / Bash)  
**Python Requirement:** Python 3.11 or later  

---

## 1. Prerequisites

Ensure Python 3.11+ and Git are installed on your system.

To check your Python version:
```bash
python --version   # Windows / Linux / macOS
# or
python3 --version  # Linux / macOS
```

---

## 2. Virtual Environment Setup

### Windows (PowerShell)

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd PressureIQ
   ```

2. Create the virtual environment:
   ```powershell
   python -m venv .venv
   ```

3. Activate the environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   > **Note regarding PowerShell Execution Policies:**  
   > If script execution is restricted on your Windows machine, run:
   > ```powershell
   > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   > ```
   > Or invoke Python directly from `.venv` without activation:
   > ```powershell
   > .\.venv\Scripts\python.exe <script.py>
   > ```

4. Upgrade pip using the module invocation:
   ```powershell
   python -m pip install --upgrade pip
   ```

---

### Linux / macOS (Terminal)

1. Open a terminal and navigate to the project root:
   ```bash
   cd PressureIQ
   ```

2. Create the virtual environment:
   ```bash
   python3 -m venv .venv
   ```

3. Activate the environment:
   ```bash
   source .venv/bin/activate
   ```

4. Upgrade pip:
   ```bash
   python3 -m pip install --upgrade pip
   ```

---

## 3. Dependency Installation

Install all required packages from `requirements.txt`:

```bash
# Windows
python -m pip install -r requirements.txt

# Linux / macOS
python3 -m pip install -r requirements.txt
```

---

## 4. Environment Verification

Run the automated dependency and platform verification audit:

```bash
# Windows
python verify_dependencies.py

# Linux / macOS
python3 verify_dependencies.py
```

This script will verify every critical dependency and output their version numbers.

---

## 5. Running Tests

Run the test suite with coverage:

```bash
# Windows
python -m pytest -v --cov=src

# Linux / macOS
python3 -m pytest -v --cov=src
```

---

## 6. Running the Application Entry Point

To verify project configuration and directory architecture:

```bash
# Windows
python run.py

# Linux / macOS
python3 run.py
```

---

## 7. Starting the Streamlit Dashboard

To launch the minimal interactive dashboard:

```bash
# Windows
python -m streamlit run dashboard/app.py

# Linux / macOS
python3 -m streamlit run dashboard/app.py
```

