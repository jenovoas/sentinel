import re

with open("backend/app/config.py", "r") as f:
    content = f.read()

# Pattern to find the broken secret_key assignment
pattern = r"secret_key: str = Field\(..., min_length=32\)\n    \)"
replacement = "secret_key: str = Field(..., min_length=32)"

new_content = re.sub(pattern, replacement, content)

with open("backend/app/config.py", "w") as f:
    f.write(new_content)
