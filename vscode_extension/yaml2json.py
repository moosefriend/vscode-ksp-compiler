import json
from pathlib import Path
import yaml
from yaml import SafeLoader

cur_dir = Path(__file__).parent
input_file_list = [
    Path("language-configuration.yml"),
    Path("syntaxes/ksp.tmGrammar.yml"),
    Path("snippets/ksp.snippets.yml")
]
output_dir = Path("out")
output_dir.mkdir(parents=True, exist_ok=True)

for input_file in input_file_list:
    base_name = input_file.stem
    output_file = output_dir / f"{base_name}.json"
    print(f"Converting {input_file.as_posix()} -> {output_file.as_posix()}")
    input_path = cur_dir / input_file
    output_path = cur_dir / output_file
    if input_path.is_file():
        with input_path.open("r") as f:
            data = yaml.load(f, Loader=SafeLoader)
        with output_path.open("w") as f:
            json.dump(data, f, indent=4)
    else:
        print(f"*** ERROR: {input_file.resolve().as_posix()} not found!")