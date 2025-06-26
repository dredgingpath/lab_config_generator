from ipaddress import IPv4Network, ip_interface
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import json

def load_topology(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)['routers']

def get_default_subnet(r1, r2):
    nums = sorted([int(r1[1:]), int(r2[1:])])
    third_octet = int(f"{nums[0]}{nums[1]}")
    subnet_str = f"10.0.{third_octet}.0/30"
    net = IPv4Network(subnet_str)
    return str(net[1]), str(net[2])

def assign_loopbacks(topology):
    for router in topology:
        router_num = int(router[1:])
        loopback_ip = f"10.255.0.{router_num} 255.255.255.255"
        topology[router]['loopback'] = loopback_ip
    return topology

def assign_interface_ips(topology):
    link_counters = {}
    peer_link_indices = {}
    for router, data in topology.items():
        interfaces = data.get("interfaces", {})
        for iface, details in interfaces.items():
            peer = details.get("peer")
            if not peer:
                continue
            link_key = tuple(sorted([router, peer]))
            if link_key not in link_counters:
                link_counters[link_key] = 0
            link_index = link_counters[link_key]
            peer_intfs = topology[peer]['interfaces']
            peer_links = [p_iface for p_iface, p_details in peer_intfs.items() if p_details.get("peer") == router]
            peer_links.sort()
            if len(peer_links) > link_index:
                peer_iface = peer_links[link_index]
            else:
                peer_iface = None
            if peer_iface:
                # Format: <local_router>> <local_interface>::<peer_interface> << <peer_router>
                data['interfaces'][iface]['description'] = f"{router}>>{iface}::{peer_iface}<<{peer}"
                topology[peer]['interfaces'][peer_iface]['description'] = f"{peer}>>{peer_iface}::{iface}<<{router}"
            nums = sorted([int(router[1:]), int(peer[1:])])
            third_octet = int(f"{nums[0]}{nums[1]}")
            subnet_str = f"10.{link_index}.{third_octet}.0/30"
            net = IPv4Network(subnet_str)
            ip1, ip2 = str(net[1]), str(net[2])
            if 'ip' not in details:
                data['interfaces'][iface]['ip'] = f"{ip1} 255.255.255.0"
                if peer_iface and 'ip' not in peer_intfs[peer_iface]:
                    peer_intfs[peer_iface]['ip'] = f"{ip2} 255.255.255.0"
            link_counters[link_key] += 1
    return topology

def find_neighbors(router_name, topology):
    neighbors = []
    routing = topology[router_name].get("routing", {})
    for n in routing.get("neighbors", []):
        neighbor_name = n.get("neighbor")
        asn = n.get("asn")
        neighbor_intfs = topology[neighbor_name]["interfaces"]
        for iface, details in neighbor_intfs.items():
            if details.get("peer") == router_name:
                ip = details.get("ip", "").split()[0]
                neighbors.append({"ip": ip, "asn": asn})
    return neighbors

def collect_networks(router_config):
    networks = set()
    loopback_ip = router_config.get("loopback")
    if loopback_ip:
        ip, mask = loopback_ip.split()
        if mask == "255.255.255.255":
            cidr = "32"
        else:
            cidr = str(IPv4Network(f"0.0.0.0/{mask}").prefixlen)
        networks.add(f"{ip}/{cidr}")
    for iface_data in router_config.get("interfaces", {}).values():
        if "ip" in iface_data:
            ip, mask = iface_data["ip"].split()
            cidr = str(IPv4Network(f"0.0.0.0/{mask}").prefixlen)
            networks.add(f"{ip}/{cidr}")
    return sorted(networks)

def generate_configs(topology, template_path, output_dir):
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template(template_path.name)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for router, config in topology.items():
        interfaces = config.get("interfaces", {})
        neighbors = find_neighbors(router, topology)
        routing = config.get("routing", {})
        loopback_ip = config.get("loopback")
        networks = collect_networks(config)
        rendered = template.render(
            hostname=router,
            interfaces=interfaces,
            neighbors=neighbors,
            routing=routing,
            loopback=loopback_ip,
            networks=networks
        )
        with open(Path(output_dir) / f"{router}_config.txt", "w") as f:
            f.write(rendered)
        print(f"✅ Generated config for {router}")