# HomeLink smart home integration API

This project contains a python API to connect MQTT-enabled smart home platforms to HomeLink smarthome cloud

## Setup

This repo utilizes VS Code [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) so you don't need to alter your global python environment.

## Installing dependencies

Use `pip` to install required dependencies by running `pip install -r requirements.txt` from the project root.

## Updating dependencies

During the course of development, if new packages are added, it's recommended to update [`requirements.txt`](./requirements.txt) by running `pip freeze > requirements.txt`.
