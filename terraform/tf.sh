#!/usr/bin/env bash
YC_TOKEN=$(yc --profile=dd iam create-token) \
terraform "${@}"
