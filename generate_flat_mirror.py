"""
Regenerates the complete D:\lc_flattened mirror directory.
Guarantees:
1. 100% flat layout (0 subdirectories).
2. Zero binary / database / dataset files.
3. Every file mapped to folder_subfolder_file.ext format.
"""

import os
import shutil
import glob

SRC = r"D:\lc_practice"
DST = r"D:\lc_flattened"

os.makedirs(DST, exist_ok=True)

# 1. Clean destination
for item in os.listdir(DST):
    item_path = os.path.join(DST, item)
    if os.path.isdir(item_path):
        shutil.rmtree(item_path, ignore_errors=True)
    else:
        os.remove(item_path)

# 2. Copy root python scripts, markdown docs, and text files
for fname in os.listdir(SRC):
    fpath = os.path.join(SRC, fname)
    if os.path.isfile(fpath) and fname.endswith((".py", ".md", ".txt")):
        shutil.copy2(fpath, os.path.join(DST, fname))

# 3. Flatten models/ (plain-text JSON files)
models_dir = os.path.join(SRC, "models")
if os.path.exists(models_dir):
    for fname in os.listdir(models_dir):
        if fname.endswith(".json"):
            shutil.copy2(os.path.join(models_dir, fname), os.path.join(DST, f"models_{fname}"))

# 4. Flatten templates/
template_file = os.path.join(SRC, "templates", "index.html")
if os.path.exists(template_file):
    shutil.copy2(template_file, os.path.join(DST, "templates_index.html"))

# 5. Flatten frontend/
frontend_dir = os.path.join(SRC, "frontend")
if os.path.exists(frontend_dir):
    shutil.copy2(os.path.join(frontend_dir, "package.json"), os.path.join(DST, "frontend_package.json"))
    shutil.copy2(os.path.join(frontend_dir, "vite.config.js"), os.path.join(DST, "frontend_vite_config.js"))
    shutil.copy2(os.path.join(frontend_dir, "index.html"), os.path.join(DST, "frontend_index.html"))
    
    src_dir = os.path.join(frontend_dir, "src")
    if os.path.exists(src_dir):
        shutil.copy2(os.path.join(src_dir, "index.css"), os.path.join(DST, "frontend_src_index.css"))
        shutil.copy2(os.path.join(src_dir, "App.jsx"), os.path.join(DST, "frontend_src_App.jsx"))
        
        comps_dir = os.path.join(src_dir, "components")
        if os.path.exists(comps_dir):
            for cname in os.listdir(comps_dir):
                if cname.endswith((".jsx", ".js")):
                    shutil.copy2(os.path.join(comps_dir, cname), os.path.join(DST, f"frontend_src_components_{cname}"))

# 6. Sanitize: remove any binaries, sqlite databases, or parquet files if accidentally copied
banned_exts = (".db", ".sqlite", ".sqlite3", ".parquet", ".xlsx", ".joblib", ".p", ".pkl", ".bin", ".zip", ".pyc")
for item in os.listdir(DST):
    item_path = os.path.join(DST, item)
    if os.path.isdir(item_path):
        shutil.rmtree(item_path, ignore_errors=True)
    elif item.endswith(banned_exts):
        os.remove(item_path)

print(f"[SUCCESS] Flat mirror generated at {DST} with {len(os.listdir(DST))} plain-text files and 0 subdirectories!")
