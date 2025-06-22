# Lab Config Generator

This tool generates router configuration files based on a topology JSON file and a Jinja2 template.

## Features

- Supports multiple routers and interfaces
- Automatically assigns interface IP addresses and descriptions
- Generates configs using a customizable Jinja2 template

## Usage

### 1. Prepare Your Topology

Edit or create your topology file in `config/topology.json`. Example:
```json
{
  "routers": {
    "R1": {
      "interfaces": {
        "Eth0/0": { "peer": "R2" },
        "Eth0/1": { "peer": "R3" }
      }
    },
    "R2": {
      "interfaces": {
        "Eth0/0": { "peer": "R1" }
      }
    },
    "R3": {
      "interfaces": {
        "Eth0/0": { "peer": "R1" }
      }
    }
  }
}
```

### 2. Prepare Your Template

Edit the Jinja2 template in `templates/router_template.j2` to match your desired config style.

### 3. Generate Configs

Run the generator from the project root:

```bash
python3 main.py
```

#### Optional Arguments

- `--topology`: Path to the topology JSON file (default: `config/topology.json`)
- `--template`: Path to the Jinja2 template (default: `templates/router_template.j2`)
- `--output`: Output directory for generated configs (default: `outputs`)

Example:

```bash
python3 main.py --topology config/bgp.json --template templates/router_template.j2 --output outputs
```

### 4. Output

Generated configuration files will be placed in the specified output directory (default: `outputs/`).

Example: R1_config

```
hostname R1
no ip domain lookup
!
interface Loopback0
  ip address 10.255.0.1 255.255.255.255
  description Lo0::R1
interface Eth0/0
  ip address 10.0.12.1 255.255.255.0
  description Eth0/0>>R1::R2<<Eth0/0
  no shutdown
!
router bgp 65001
neighbor 10.0.12.2 remote-as 65002
  address-family ipv4
    neighbor 10.0.12.2 activate
  exit-address-family
```

## Requirements

- Python 3.7+
- [Jinja2](https://pypi.org/project/Jinja2/)

Install dependencies with:

```bash
pip install Jinja2
```

## Project Structure

```
lab_config_generator/
├── config/
│   └── topology.json
├── lab_config_generator/
│   └── generator.py
├── templates/
│   └── router_template.j2
├── outputs/
│   └── R1_config.txt
├── main.py
```

## License

MIT License
