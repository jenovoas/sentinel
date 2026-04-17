#!/bin/bash
echo "--- CONTAINERS ---"
podman ps --all
echo "--- PODS ---"
podman pod ls
