#!/bin/bash
podman inspect --format='{{json .State.Health}}' espiguita-db
