import argparse
from pathlib import Path
from lab_config_generator.generator import (
    load_topology, assign_interface_ips, assign_loopbacks, generate_configs
)

def main():
    parser = argparse.ArgumentParser(description="Generate router configs from topology JSON.")
    parser.add_argument("--topology", default="config/topology.json", help="Path to topology JSON")
    parser.add_argument("--template", default="templates/router_template.j2", help="Path to Jinja2 template")
    parser.add_argument("--output", default="outputs", help="Directory to store generated configs")
    args = parser.parse_args()

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