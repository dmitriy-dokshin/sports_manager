variable "DB_ADMIN_PASSWORD" {
  type      = string
  sensitive = true
}

resource "yandex_mdb_mysql_cluster" "sm-mysql" {
  deletion_protection = false
  environment         = "PRODUCTION"
  mysql_config = {
    "sql_mode" = "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"
  }
  name       = "sm-mysql"
  network_id = yandex_vpc_network.default.id
  version    = "8.0"

  access {
    data_lens = false
    web_sql   = false
  }

  backup_window_start {
    hours   = 22
    minutes = 0
  }

  database {
    name = "sports_manager"
  }

  host {
    assign_public_ip = true
    subnet_id        = ycp_vpc_subnet.default["ru-central1-c"].id
    zone             = "ru-central1-c"
  }

  maintenance_window {
    type = "ANYTIME"
  }

  resources {
    disk_size          = 10
    disk_type_id       = "network-hdd"
    resource_preset_id = "b2.medium"
  }

  timeouts {}

  user {
    global_permissions = []
    name               = "sm-admin"
    password           = var.DB_ADMIN_PASSWORD

    permission {
      database_name = "sports_manager"
      roles = [
        "ALL",
      ]
    }
  }
}