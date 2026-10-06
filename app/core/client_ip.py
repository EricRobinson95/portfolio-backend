from ipaddress import ip_address, ip_network

from app.core.cloudflare_ips import CLOUDFLARE_NETWORKS

class ClientIPResolver:
    """Resolve direct, ALB, or Cloudflare through ALB request sources."""

    def __init__(self, trusted_proxy_cidrs: tuple[str, ...] = ()) -> None:
        # Invalid configuration fails during initialization instead of broadening trust.
        self.trusted_networks = tuple(ip_network(cidr) for cidr in trusted_proxy_cidrs)
        if any(network.prefixlen == 0 for network in self.trusted_networks):
            raise ValueError("Trusted proxies must not include every IP address.")

    def resolve(self, scope: dict) -> tuple[str | None, str | None]:
        client = scope.get("client")
        try:
            peer = ip_address(client[0]) if client else None
        except ValueError:
            peer = None
        if peer is None:
            return None, None

        if not any(peer in network for network in self.trusted_networks):
            return str(peer), "peer"

        forwarded = [value for name, value in scope.get("headers", [])
                    if name.lower() == b"x-forwarded-for"]
        # Ambiguous or missing proxy data must not be attributed to a visitor.
        if len(forwarded) != 1 or len(forwarded[0]) > 4096:
            return None, None
        try:
            # ALB append mode adds the address it observed after client values.
            address = forwarded[0].decode("ascii").rsplit(",", 1)[-1].strip()
            if "%" in address:
                return None, None
            if address.startswith("["):
                host, separator, port = address[1:].partition("]:")
                if not separator or not port.isdecimal() or not 1 <= int(port) <= 65535:
                    return None, None
                parsed = ip_address(host)
                if parsed.version != 6:
                    return None, None
            else:
                try:
                    parsed = ip_address(address)
                except ValueError:
                    host, separator, port = address.rpartition(":")
                    if not separator or not port.isdecimal() or not 1 <= int(port) <= 65535:
                        return None, None
                    parsed = ip_address(host)
                    if parsed.version != 4:
                        return None, None
            if any(parsed in network for network in CLOUDFLARE_NETWORKS):
                # Only an ALB-verified Cloudflare source may supply this header.
                connecting = [value for name, value in scope.get("headers", [])
                              if name.lower() == b"cf-connecting-ip"]
                if len(connecting) != 1 or len(connecting[0]) > 45:
                    return None, None
                visitor = connecting[0].decode("ascii").strip()
                if "%" in visitor:
                    return None, None
                return str(ip_address(visitor)), "cloudflare"
            return str(parsed), "alb"
        except ValueError:
            return None, None
