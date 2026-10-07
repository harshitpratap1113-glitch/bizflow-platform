import shutil
import os

src = r"C:\Users\intel\Desktop\SaaS_Projects\bizflow-platform\static\index.html"
dst = r"C:\Users\intel\Desktop\SaaS_Projects\bizflow-platform\index.html"

shutil.copy2(src, dst)
print("Copied successfully to " + dst)
