import datetime
import os

now = datetime.datetime.now()
timestamp = now.strftime("%Y%m%d-%H%M")
old_path = "Tasks.md"
new_path = f"archives/{timestamp}-Tasks-done.md"

if os.path.exists(old_path):
    os.rename(old_path, new_path)
    print(f"Successfully renamed '{old_path}' to '{new_path}'")
else:
    print(f"Error: '{old_path}' not found.")