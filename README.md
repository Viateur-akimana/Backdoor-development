# Backdoor Development

This repository contains the development of a backdoor tool written in Python disguised as a Snake game.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Backdoor Development project aims to create a secure and efficient backdoor tool for penetration testing purposes. This tool is designed for ethical hacking and cybersecurity professionals to test the security of their systems. It is disguised as a Snake game to facilitate its deployment.

## Features

- Remote access to target machines
- Persistence mechanisms
- Disguised as a Snake game
- Cleanup application to remove persistence

## Installation

To install the backdoor tool, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/Viateur-akimana/Backdoor-development.git
   ```
2. Navigate to the project directory:
   ```sh
   cd Backdoor-development
   ```
3. Install the required dependencies:
   ```sh
   pipenv install
   ```

## Usage

To use the backdoor tool

### Running the Game

1. Run the game:
   ```sh
   python game.py
   ```
2. The game will check for required apps and install them if needed.
3. The game will establish persistence on the target system.
4. The game will open a reverse TCP shell to the specified host and port.

### Cleanup

1. To remove the persistence and terminate the game, run the cleanup script:
   ```sh
   python cleanup.py
   ```

## Contributing

Contributions are welcome! 
