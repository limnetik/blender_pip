# 🐍 Python Module Manager Plus

**Blender Add-on for Python Package Management**  
Manage, install, remove, and export Python packages directly inside Blender. (Chat GPT was used for making the modded add-on)

---

## 📦 Overview
The **Python Module Manager Plus** add-on allows you to manage Python packages inside Blender without needing to use a terminal.  
It provides an interface in **Preferences → Add-ons** to install, remove, list, and export Python modules.  
Additional tools include dependency reports and compatibility checks.

---

## 🔧 Installation
1. Download the script file and save it as `python_module_manager_plus.py`.  
2. In Blender, go to:  
   **Edit → Preferences → Add-ons → Install…**  
3. Select the script and enable the checkbox.  
4. The add-on will now appear in **Preferences → Add-ons** under *Development*.  

---

## 🚀 Features

### 📦 Package Management
- **Install Packages** → Install one or multiple modules (space-separated).  
- **Remove Packages** → Uninstall one or multiple modules.  
- **List Installed Packages** → Show all installed modules with versions.  
- **Clear Output** → Reset the result/console area inside the UI.  

### 📑 Export & Reports
- **Export Package List** → Save all installed packages into:
  - `installed_packages.txt`  
  - `installed_packages.csv`  
- **Export Dependencies** → Run `pip show` and save package details to `package_dependencies.txt`.  
- **Export Dependency Tree** → Use `pipdeptree` to generate a dependency tree (`dependency_tree.txt`).  

### 🔍 Compatibility Tools
- **Check Compatibility** → Verify package dependencies and detect version conflicts (`pip check`).  

### 🔧 Maintenance
- **Ensure pip** → Make sure `pip` is installed in Blender’s Python.  
- **Upgrade pip** → Update `pip` to the latest version.  

---

## 🖼 UI Preview
Accessible under:  
**Edit → Preferences → Add-ons → Development → Python Module Manager Plus**  

- **Module Name(s):** Field to enter one or more package names.  
- **Install as --user:** Toggle for user-level installations.  
- **Filter (for export):** Restrict results when exporting.  
- **Output/Error Panels:** Show logs from pip commands.  

---

## 📂 Export Locations
Files are saved in Blender’s **scripts folder**, typically:  

`<Blender user directory>/scripts/`

- `installed_packages.txt`  
- `installed_packages.csv`  
- `package_dependencies.txt`  
- `dependency_tree.txt`  

---

## ✅ Quick Start
1. Open Blender Preferences → Add-ons → Development → **Python Module Manager Plus**.  
2. Type a package name (e.g. `requests`).  
3. Click **Install Packages**.  
4. Use **List Packages** to confirm installation.  
5. (Optional) Export lists or check compatibility.  

---

## 📌 Notes
- Runs inside Blender’s bundled Python.  
- Some packages with compiled binaries may require a matching build for Blender’s Python.  
- Dependency graph visualization requires `pipdeptree` (installed automatically if missing).  




