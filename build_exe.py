# build_exe.py
import PyInstaller.__main__
import re

# Extract version from character_creator.py
with open("character_creator.py", "r", encoding="utf-8") as f:
    content = f.read()
    version_match = re.search(r'VERSION = "([^"]+)"', content)
    if version_match:
        VERSION = version_match.group(1)
    else:
        VERSION = "0.0.0"

# Clean version for filename (replace dots and letters)
safe_version = VERSION.replace(".", "_")
exe_name = f"FE_Fates_Character_Creator_v{safe_version}"

print(f"Building version: {VERSION}")
print(f"Output name: {exe_name}")

PyInstaller.__main__.run([
    'character_creator.py',
    '--onefile',
    # '--windowed',
    f'--name={exe_name}',
    '--add-data=skill_data.json;.',
    '--clean',
    '--noconfirm'
])

print(f"\nBuild complete! Check the 'dist' folder for {exe_name}.exe")