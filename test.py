from pathlib import Path

print("Home:", Path.home())
print("Config dir:", Path.home() / ".config" / "mdct")
print("Exists:", (Path.home() / ".config" / "mdct").exists())
