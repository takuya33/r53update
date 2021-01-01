# R53Update command line utility
[![Github release](https://img.shields.io/github/release/tuntunkun/r53update.svg)](https://github.com/tuntunkun/r53update/releases)
[![Python version](https://img.shields.io/badge/python-2.6%2C%202.7%2C%203.3%2C%203.4%2C%203.5%2C%203.6-green.svg)](#)
[![Requirements Status](https://requires.io/github/tuntunkun/r53update/requirements.svg)](https://requires.io/github/tuntunkun/r53update/requirements)
[![Build Status](https://travis-ci.org/tuntunkun/r53update.svg?branch=develop)](https://travis-ci.org/tuntunkun/r53update)
[![Hex.pm](https://img.shields.io/hexpm/l/plug.svg)](https://raw.githubusercontent.com/tuntunkun/r53update/master/LICENSE)

R53Update is a command line utility for Amazon Route 53 which is one of the AWS (Amazon Web Services). This tools is useful to anyone who wants to operate server with dynamic IP. You can operate not only the server which is hosted on Amazon EC2 but also on-premise servers.



## Requirements

* Internet connection  (with global IP)
* pre-configured Amazon Route53 hosted zone
* python2.6+ and pip command

### Amazon Route 53 hosted zone
To create Amazon Route 53 hosted zone, please refer to the following url.  
http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html

### Run on Docker Container
If you already configured aws credentials properly in `~/.aws`, Just type following command.

```
docker run --rm -it -v ~/.aws:/root/.aws ghcr.io/tuntunkun/r53update www example.com
```

### Python & PIP
If you want to install python and pip via binary installer, you can generally do so through the basic package-management tool that comes with your distribution.
If you're on Debian-based distribution, you can use apt-get:
```bash
sudo apt-get install python{,-dev,-pip} build-essentials
```

If you're on a Redhat-based distribution like Fedora, CentOS, etc... try yum:
```bash
sudo yum -y groupinstall "Development Tools"
sudo yum -y install python{,-devel,-pip}
```


## Install

```bash
sudo -H pip install git+https://github.com/tuntunkun/r53update
```

## Usage
If you have already configured AWS profile and Route 53 hosted zone, it is very simple to use.
```bash
r53update www example.com
```

### Configurable Variable

| Variable  | Option     | Default    | Description                                 |
|-----------|------------|------------|---------------------------------------------|
| PROFILE   | --profile  | default    | profile name which is configured by aws-cli |
| METHOD    | --method   | localhost  | detection method of global IP               |
| IFACE     | --iface    | n/a        | name of the network interface               |

### The method of global IP detection
You can specify the method of global IP detection by '--method' option.  
Available method is as follows.

|  Method Name  | Method | Multiple IP   | Description                            |
|---------------|--------|---------------|----------------------------------------|
| opendns.com   | DNS    | not supported |                                        |
| ifconfig.me   | HTTP   | not supported |                                        |
| ipecho.net    | HTTP   | not supported |                                        |
| icanhazip.com | HTTP   | not supported |                                        |
| localhost     | NIC    | supported     | require '--iface' option               |  

## License
(C)2015 Takuya Sawada.

R53Update is licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
 
Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.
