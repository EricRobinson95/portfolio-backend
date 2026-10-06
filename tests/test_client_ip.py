import pytest

from app.core.client_ip import ClientIPResolver


def scope(peer="10.0.1.5", forwarded=b"203.0.113.9"):
    return {"client": (peer, 50000), "headers": [(b"x-forwarded-for", forwarded)]}


@pytest.mark.parametrize("peer", ["198.51.100.8", "127.0.0.1", "10.0.2.5"])
def test_untrusted_peer_cannot_spoof_client_ip(peer):
    resolver = ClientIPResolver(("10.0.1.0/24",))
    assert resolver.resolve(scope(peer)) == (peer, "peer")


def test_forwarded_headers_are_untrusted_by_default():
    assert ClientIPResolver().resolve(scope()) == ("10.0.1.5", "peer")


@pytest.mark.parametrize("forwarded,expected", [
    (b"203.0.113.9", "203.0.113.9"),
    (b"198.51.100.99, 203.0.113.9", "203.0.113.9"),
    (b"not-an-ip, 203.0.113.9", "203.0.113.9"),
    (b"203.0.113.9:45678", "203.0.113.9"),
    (b"2001:db8::9", "2001:db8::9"),
    (b"[2001:db8::9]:45678", "2001:db8::9"),
])
def test_alb_appended_address_overrides_visitor_supplied_prefix(forwarded, expected):
    assert ClientIPResolver(("10.0.1.0/24",)).resolve(scope(forwarded=forwarded)) == (
        expected, "alb",
    )


@pytest.mark.parametrize("forwarded", [
    b"", b"203.0.113.9,", b"garbage", b"203.0.113.9:0", b"203.0.113.9:65536",
    b"[2001:db8::9]:bad", b"[203.0.113.9]:80", b"fe80::1%eth0", b"\xff",
    b"x" * 4097,
])
def test_invalid_proxy_data_is_omitted(forwarded):
    assert ClientIPResolver(("10.0.1.0/24",)).resolve(scope(forwarded=forwarded)) == (None, None)


def test_duplicate_or_missing_header_is_omitted_for_trusted_peer():
    request = scope()
    request["headers"] *= 2
    resolver = ClientIPResolver(("10.0.1.0/24",))
    assert resolver.resolve(request) == (None, None)
    request["headers"] = []
    assert resolver.resolve(request) == (None, None)


@pytest.mark.parametrize("client", [None, ("testclient", 50000)])
def test_missing_or_non_ip_peer_is_omitted(client):
    assert ClientIPResolver().resolve({"client": client}) == (None, None)


def test_ipv6_proxy_network():
    assert ClientIPResolver(("2001:db8:1::/64",)).resolve(
        scope(peer="2001:db8:1::5")
    ) == ("203.0.113.9", "alb")


@pytest.mark.parametrize("cidr", ["*", "0.0.0.0/0", "::/0"])
def test_invalid_network_configuration_fails(cidr):
    with pytest.raises(ValueError):
        ClientIPResolver((cidr,))


@pytest.mark.parametrize("edge", [
    b"172.70.80.213", b"172.69.214.198:45678", b"2606:4700::1",
    b"[2606:4700::1]:45678",
])
@pytest.mark.parametrize("visitor", [b"198.51.100.25", b"2001:db8::25"])
def test_cloudflare_visitor_requires_both_verified_hops(edge, visitor):
    request = scope(forwarded=b"fake-visitor, " + edge)
    request["headers"].append((b"cf-connecting-ip", visitor))
    assert ClientIPResolver(("10.0.1.0/24",)).resolve(request) == (
        visitor.decode(), "cloudflare",
    )


@pytest.mark.parametrize("peer", ["198.51.100.8", "172.70.80.213"])
def test_direct_peer_cannot_forge_entire_cloudflare_chain(peer):
    request = scope(peer=peer, forwarded=b"172.70.80.213")
    request["headers"].append((b"cf-connecting-ip", b"192.0.2.123"))
    assert ClientIPResolver(("10.0.1.0/24",)).resolve(request) == (peer, "peer")


def test_direct_alb_client_cannot_forge_cloudflare_header_or_prefix():
    request = scope(forwarded=b"172.70.80.213, 198.51.100.8")
    request["headers"].append((b"cf-connecting-ip", b"192.0.2.123"))
    assert ClientIPResolver(("10.0.1.0/24",)).resolve(request) == ("198.51.100.8", "alb")


@pytest.mark.parametrize("visitor", [
    b"", b"garbage", b"192.0.2.1, 192.0.2.2", b"192.0.2.1:443",
    b"[2001:db8::1]:443", b"fe80::1%eth0", b"\xff", b"x" * 46,
])
def test_invalid_cloudflare_visitor_is_omitted(visitor):
    request = scope(forwarded=b"172.70.80.213")
    request["headers"].append((b"cf-connecting-ip", visitor))
    assert ClientIPResolver(("10.0.1.0/24",)).resolve(request) == (None, None)


def test_cloudflare_missing_or_duplicate_visitor_header_is_omitted():
    request = scope(forwarded=b"172.70.80.213")
    resolver = ClientIPResolver(("10.0.1.0/24",))
    assert resolver.resolve(request) == (None, None)
    request["headers"].extend([(b"cf-connecting-ip", b"192.0.2.123")] * 2)
    assert resolver.resolve(request) == (None, None)


def test_cloudflare_source_does_not_enable_trust_by_default():
    request = scope(forwarded=b"172.70.80.213")
    request["headers"].append((b"cf-connecting-ip", b"192.0.2.123"))
    assert ClientIPResolver().resolve(request) == ("10.0.1.5", "peer")
