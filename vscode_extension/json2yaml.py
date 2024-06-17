import json
from pathlib import Path
import yaml
from yaml import SafeLoader

cur_dir = Path(__file__).parent
input_file_list = [
    Path("language-configuration.json"),
    Path("syntaxes/ksp.tmGrammar.json"),
    Path("snippets/ksp.snippets.json")
]
output_dir = Path("out")
output_dir.mkdir(parents=True, exist_ok=True)

for input_file in input_file_list:
    base_name = input_file.stem
    output_file = output_dir / f"{base_name}.yml"
    print(f"Converting {input_file.as_posix()} -> {output_file.as_posix()}")
    input_path = cur_dir / input_file
    output_path = cur_dir / output_file
    if input_path.is_file():
        with input_path.open("r") as f:
            data = json.load(f)
        with output_path.open("w") as f:
            yaml.dump(data, f, indent=4)
    else:
        print(f"*** ERROR: {input_file.resolve().as_posix()} not found!")