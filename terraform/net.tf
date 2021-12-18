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
  route_table_id = {
    "ru-central1-a" : null
    "ru-central1-b" : null
    "ru-central1-c" : yandex_vpc_route_table.nat-instance-route.id
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
  route_table_id = local.route_table_id[each.key]
  zone_id        = each.key

  extra_params {
    feature_flags = [
      "hardened-public-ip",
      "blackhole",
    ]
  }
}

// https://cloud.yandex.ru/docs/solutions/routing/nat-instance
resource "ycp_vpc_subnet" "public" {
  egress_nat_enable = false
  name              = "public"
  network_id        = yandex_vpc_network.default.id
  v4_cidr_blocks = [
    "10.131.0.0/24",
  ]
  zone_id = "ru-central1-c"

  extra_params {
    feature_flags = [
      "hardened-public-ip",
      "blackhole",
    ]
  }
}

resource "yandex_compute_instance" "nat-instance" {
  hostname = "nat-instance"
  metadata = {
    "ssh-keys"  = <<-EOT
            v01d:ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOPrUPolP0b37rONe4/MxWuiPUk8GbkENXxZWg3gCcn/ dmitriy.dokshin@gmail.com
        EOT
    "user-data" = <<-EOT
            #cloud-config
            datasource:
             Ec2:
              strict_id: false
            ssh_pwauth: no
            users:
            - name: v01d
              sudo: ALL=(ALL) NOPASSWD:ALL
              shell: /bin/bash
              ssh-authorized-keys:
              - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOPrUPolP0b37rONe4/MxWuiPUk8GbkENXxZWg3gCcn/ dmitriy.dokshin@gmail.com
        EOT
  }
  name                      = "nat-instance"
  network_acceleration_type = "standard"
  platform_id               = "standard-v3"
  zone                      = "ru-central1-c"

  boot_disk {
    auto_delete = true
    device_name = "ef38fs6d0k1f9g3186n6"
    disk_id     = "ef38fs6d0k1f9g3186n6"
    mode        = "READ_WRITE"

    initialize_params {
      image_id = "fd8drj7lsj7btotd7et5"
      size     = 13
      type     = "network-hdd"
    }
  }

  network_interface {
    ip_address         = "10.131.0.5"
    ipv4               = true
    ipv6               = false
    nat                = true
    nat_ip_address     = "84.252.132.202"
    security_group_ids = []
    subnet_id          = ycp_vpc_subnet.public.id
  }


  resources {
    core_fraction = 20
    cores         = 2
    gpus          = 0
    memory        = 1
  }

  scheduling_policy {
    preemptible = false
  }

}

resource "yandex_vpc_route_table" "nat-instance-route" {
  name       = "nat-instance-route"
  network_id = yandex_vpc_network.default.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    next_hop_address   = yandex_compute_instance.nat-instance.network_interface[0].ip_address
  }
}