bl_info = {
    "name": "Python Module Manager plus",
    "author": "ambi, modded by Limnetik",
    "version": (0, 5, 0),
    "blender": (4, 5, 1),
    "location": "Preferences > Add-ons",
    "description": "Manage Python modules inside Blender with PIP",
    "category": "Development",
}

import bpy
import sys
import subprocess
import site
from pathlib import Path
from datetime import datetime

app_path = site.getusersitepackages()
if app_path not in sys.path:
    sys.path.append(app_path)

MODULES_FOLDER = Path(bpy.utils.user_resource("SCRIPTS")) / "modules"
python_bin = sys.executable if bpy.app.version >= (2, 91, 0) else bpy.app.binary_path_python

TEXT_OUTPUT = []
ERROR_OUTPUT = []

def run_pip_command(self, *cmds, cols=False, run_module="pip"):
    global TEXT_OUTPUT, ERROR_OUTPUT

    cmds = [c for c in cmds if c]
    command = [python_bin, "-m", run_module, *cmds]

    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if output.stderr and "WARNING" not in output.stderr[:20]:
        self.report({"ERROR"}, "Error occurred. See console.")
        ERROR_OUTPUT = save_text(output.stderr)
    else:
        ERROR_OUTPUT = []

    TEXT_OUTPUT = save_text(output.stdout, cols=cols) if output.stdout else []

def save_text(text, cols=False):
    lines = []
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split() if cols else [" ".join(line.split())]
        lines.append(parts)
    return lines

# ---------------- OPERATORS ----------------

class PMM_OT_PIPInstall(bpy.types.Operator):
    bl_idname = "pmm.pip_install"
    bl_label = "Install packages"
    def execute(self, context):
        user_flag = "--user" if context.scene.pip_user_flag else None
        run_pip_command(self, "install", *context.scene.pip_module_name.split(), user_flag)
        return {"FINISHED"}

class PMM_OT_PIPRemove(bpy.types.Operator):
    bl_idname = "pmm.pip_remove"
    bl_label = "Remove packages"
    def execute(self, context):
        run_pip_command(self, "uninstall", *context.scene.pip_module_name.split(), "-y")
        return {"FINISHED"}

class PMM_OT_ClearText(bpy.types.Operator):
    bl_idname = "pmm.clear_output"
    bl_label = "Clear Output"
    def execute(self, context):
        global TEXT_OUTPUT, ERROR_OUTPUT
        TEXT_OUTPUT, ERROR_OUTPUT = [], []
        return {"FINISHED"}

class PMM_OT_PIPList(bpy.types.Operator):
    bl_idname = "pmm.pip_list"
    bl_label = "List Installed Packages"
    def execute(self, context):
        run_pip_command(self, "list", cols=True)
        return {"FINISHED"}

class PMM_OT_EnsurePIP(bpy.types.Operator):
    bl_idname = "pmm.ensure_pip"
    bl_label = "Ensure pip is available"
    def execute(self, context):
        run_pip_command(self, "--default-pip", run_module="ensurepip")
        return {"FINISHED"}

class PMM_OT_UpgradePIP(bpy.types.Operator):
    bl_idname = "pmm.upgrade_pip"
    bl_label = "Upgrade pip"
    def execute(self, context):
        run_pip_command(self, "install", "--upgrade", "pip")
        return {"FINISHED"}

class PMM_OT_CheckCompatibility(bpy.types.Operator):
    bl_idname = "pmm.check_compatibility"
    bl_label = "Check Package Dependencies"
    def execute(self, context):
        run_pip_command(self, "check")
        if TEXT_OUTPUT:
            self.report({"WARNING"}, "Some dependency issues found. Check console or output.")
        else:
            self.report({"INFO"}, "All packages compatible.")
        return {"FINISHED"}

class PMM_OT_ExportList(bpy.types.Operator):
    bl_idname = "pmm.export_list"
    bl_label = "Export Packages List"
    def execute(self, context):
        run_pip_command(self, "list", cols=True)
        export_dir = Path(bpy.utils.user_resource("SCRIPTS"))
        txt_path = export_dir / "installed_packages.txt"
        csv_path = export_dir / "installed_packages.csv"
        filter_str = context.scene.pip_filter_string.strip().lower()

        try:
            with open(txt_path, "w", encoding="utf-8") as txtfile, \
                 open(csv_path, "w", encoding="utf-8") as csvfile:

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                txtfile.write(f"Installed Python Packages - {timestamp}\n" + "-"*50 + "\n")
                csvfile.write("Package,Version\n")

                for line in TEXT_OUTPUT:
                    if line[0].lower() == "package":
                        continue
                    name, version = line[0], line[1]
                    if filter_str and filter_str not in name.lower():
                        continue
                    txtfile.write(f"{name} {version}\n")
                    csvfile.write(f"{name},{version}\n")

            self.report({"INFO"}, f"Exported to TXT and CSV in {export_dir}")
        except Exception as e:
            self.report({"ERROR"}, f"Export failed: {e}")
        return {"FINISHED"}

class PMM_OT_ExportDependencies(bpy.types.Operator):
    bl_idname = "pmm.export_dependencies"
    bl_label = "Export Dependencies (pip show)"
    def execute(self, context):
        run_pip_command(self, "list", cols=True)
        export_path = Path(bpy.utils.user_resource("SCRIPTS")) / "package_dependencies.txt"
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("Dependencies by package\n")
                f.write("="*40 + "\n")
                for line in TEXT_OUTPUT:
                    if line[0].lower() == "package":
                        continue
                    module_name = line[0]
                    result = subprocess.run(
                        [python_bin, "-m", "pip", "show", module_name],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                    )
                    f.write(f"\n{module_name}\n" + "-"*len(module_name) + "\n")
                    f.write(result.stdout or "[No info]\n")
            self.report({"INFO"}, f"Exported dependencies to {export_path.name}")
        except Exception as e:
            self.report({"ERROR"}, f"Failed: {e}")
        return {"FINISHED"}

class PMM_OT_ExportDependencyTree(bpy.types.Operator):
    bl_idname = "pmm.export_dependency_tree"
    bl_label = "Export Dependency Tree (pipdeptree)"
    def execute(self, context):
        export_path = Path(bpy.utils.user_resource("SCRIPTS")) / "dependency_tree.txt"
        try:
            result = subprocess.run(
                [python_bin, "-m", "pipdeptree"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(result.stdout or "[No output]\n")
            self.report({"INFO"}, f"Exported dependency tree to {export_path.name}")
        except Exception as e:
            self.report({"ERROR"}, f"pipdeptree not available or error occurred: {e}")
        return {"FINISHED"}

# ------------- PREFERENCES UI ----------------

class PMM_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "pip_user_flag", text="Install as --user")
        layout.prop(context.scene, "pip_module_name", text="Module name(s)")
        layout.prop(context.scene, "pip_filter_string", text="Filter (for export)")

        layout.separator()
        layout.label(text="Basic operations:")
        row = layout.row()
        row.operator("pmm.pip_install", text="Install")
        row.operator("pmm.pip_remove", text="Remove")

        row = layout.row()
        row.operator("pmm.pip_list", text="List")
        row.operator("pmm.clear_output", text="Clear Output")

        layout.separator()
        layout.label(text="Export tools:")
        row = layout.row()
        row.operator("pmm.export_list", text="Export List")
        row.operator("pmm.export_dependencies", text="Export Dependencies")

        row = layout.row()
        row.operator("pmm.export_dependency_tree", text="Export Tree")
        row.operator("pmm.check_compatibility", text="Check Compatibility")

        layout.separator()
        layout.label(text="Maintenance:")
        row = layout.row()
        row.operator("pmm.upgrade_pip", text="Upgrade pip")
        row.operator("pmm.ensure_pip", text="Ensure pip")

        if TEXT_OUTPUT:
            layout.label(text="Output:")
            box = layout.box()
            for line in TEXT_OUTPUT:
                box.label(text=" | ".join(line))

        if ERROR_OUTPUT:
            layout.label(text="Errors:")
            box = layout.box()
            for line in ERROR_OUTPUT:
                box.label(text=" ".join(line))

# -------------- REGISTER ----------------

classes = (
    PMM_AddonPreferences,
    PMM_OT_PIPInstall,
    PMM_OT_PIPRemove,
    PMM_OT_ClearText,
    PMM_OT_PIPList,
    PMM_OT_EnsurePIP,
    PMM_OT_UpgradePIP,
    PMM_OT_ExportList,
    PMM_OT_ExportDependencies,
    PMM_OT_ExportDependencyTree,
    PMM_OT_CheckCompatibility,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.pip_user_flag = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.pip_module_name = bpy.props.StringProperty(default="")
    bpy.types.Scene.pip_filter_string = bpy.props.StringProperty(default="")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.pip_user_flag
    del bpy.types.Scene.pip_module_name
    del bpy.types.Scene.pip_filter_string

if __name__ == "__main__":
    register()
