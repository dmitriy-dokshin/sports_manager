resource "yandex_vpc_network" "default" {
  description = "Auto-created default network"
  name        = "default"
}

locals {
  v4_cidr_blocks = {
    "ru-central1-a" : "10.130.0.0/24"
    "ru-central1-b" : "10.129.0.0/24"
    "ru-central1-c" : "10.128.0.0/24"
  }
}

resource "ycp_vpc_subnet" "default" {
  for_each    = toset(local.zones)
  name        = "default-${each.key}"
  description = "Auto-created default subnet for zone ${each.key}"
  network_id  = yandex_vpc_network.default.id
  v4_cidr_blocks = [
    local.v4_cidr_blocks[each.key]
  ]
  zone_id           = each.key
  egress_nat_enable = true


  extra_params {
    feature_flags = [
      "hardened-public-ip",
      "blackhole",
    ]
  }
}