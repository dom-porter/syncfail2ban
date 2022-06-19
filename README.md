# syncfail2ban

## Description
As the name suggests, the app will synchronise fail2ban jails across servers.  It will also update OPNSense aliases which can then be used to block traffic at the firewall level.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Assumptions
You are familiar with fail2ban and already have a working system.

## Setup
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

### 1. Update Configuration
Enter IP and port

Get API Key and API Secret from OPN

Enter f2b jails and sync-jail names

Enter f2b jails and OPN alias names
       

### 2. Create Sync Action

### 3. Create Dummy Log & Filter

### 4. Update Jail Configuration

## License
Apache License Version 2.0

