import argparse
from pathlib import Path
import shutil
from lab_config_generator.generator import (
    load_topology, assign_interface_ips, assign_loopbacks, generate_configs
)

def clean_output_dir(output_dir):
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()):
        confirm = input(f"Output directory '{output_dir}' is not empty. Remove all files? [y/N]: ")
        if confirm.lower() == 'y':
            for item in output_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"✅ Cleaned output directory '{output_dir}'.")
        else:
            print("❌ Aborted by user.")
            exit(1)

def force_clean_output_dir(output_dir):
    output_path = Path(output_dir)
    if output_path.exists():
        for item in output_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"✅ Cleaned output directory '{output_dir}'.")

def main():
    parser = argparse.ArgumentParser(description="Generate router configs from topology JSON.")
    parser.add_argument("--topology", default="config/topology.json", help="Path to topology JSON")
    parser.add_argument("--template", default="templates/router_template.j2", help="Path to Jinja2 template")
    parser.add_argument("--output", default="outputs", help="Directory to store generated configs")
    parser.add_argument("--clean-output", action="store_true", help="Always clean output directory before generating configs")
    args = parser.parse_args()

    if args.clean_output:
        force_clean_output_dir(args.output)
    else:
        clean_output_dir(args.output)

    topology = load_topology(args.topology)
    topology = assign_interface_ips(topology)
    topology = assign_loopbacks(topology)
    generate_configs(
        topology=topology,
        template_path=Path(args.template),
        output_dir=args.output
    )

if __name__ == "__main__":
    main()