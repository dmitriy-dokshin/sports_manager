terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
    ycp = {
      source = "terraform.storage.cloud-preprod.yandex.net/yandex-cloud/ycp"
    }
  }
}

provider "yandex" {
  endpoint  = "api.cloud.yandex.net:443"
  cloud_id  = local.yc.cloud_id
  folder_id = local.yc.folder_id
  zone      = local.yc.zone
}

provider "ycp" {
  cloud_id  = local.yc.cloud_id
  folder_id = local.yc.folder_id
  zone      = local.yc.zone
  prod      = true
}

data "yandex_resourcemanager_folder" "default" {
  folder_id = local.yc.folder_id
}

locals {
  yc = {
    "endpoint" : "api.cloud.yandex.net:443"
    "cloud_id" : "b1g8mflotc5jo0f983ig"
    "folder_id" : "b1gsha420392pl173ehc"
    "zone" : "ru-central1-a"
  }
  zones = [
    "ru-central1-a",
    "ru-central1-b",
    "ru-central1-c"
  ]
}