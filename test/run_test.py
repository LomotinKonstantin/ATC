import os
from pathlib import Path

ids = ["SUBJ", "IPV", "RGNTI"]
in_files = []
out_files = []
curr_dir = Path(__file__).parent
in_folder = curr_dir / "in"
out_folder = curr_dir / "out"
out_folder.mkdir(exist_ok=True, parents=True)
INTERPRETER = r"python"
norm = "all"
for i in in_folder.iterdir():
    in_files.append(str(i.absolute()))
    out_files.append(i.name)
for i, in_file in enumerate(in_files):
    for rubr_id in ids:
        parts = out_files[i].split(".")
        parts[0] += "_" + rubr_id
        out_file = (out_folder / ".".join(parts)).absolute()
        print(f"Testing {in_file} for {rubr_id}...")
        os.system(f"{INTERPRETER} ../ATC/ATC.py -l auto -f auto -i {in_file} -o {out_file} -id {rubr_id} -n {norm}")
print("Done")
