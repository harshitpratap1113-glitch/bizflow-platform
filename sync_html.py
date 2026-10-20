import shutil
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(root_dir, "index.html")
dst1 = os.path.join(root_dir, "static", "index.html")
dst2 = os.path.join(root_dir, "backend", "static", "index.html")

shutil.copy2(src, dst1)
if os.path.exists(os.path.dirname(dst2)):
    shutil.copy2(src, dst2)
print(f"[OK] LeedsFlow index.html synchronized to {dst1} and {dst2}")
