# R53Update command line utility

R53Update is a command line utility for Amazon Route 53 which is one of the AWS (Amazon Web Services). This tools is useful to anyone who wants to operate server with dynamic IP. You can operate not only the server which is hosted on Amazon EC2 but also on-premise servers.


[![GitHub version](https://badge.fury.io/gh/eternalharvest%2Fr53update.svg)]() [![Hex.pm](https://img.shields.io/hexpm/l/plug.svg)]()


## Requirements

* Internet connection  (with global IP)
* pre-configured Amazon Route53 hosted zone
* python2.6+ and pip command

To create Amazon Route 53 hosted zone, please refer to the following url.  
http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html

To install python and pip command,
```bash
sudo apt-get install python{,-pip} build-essentials
```

or
```bash
sudo yum -y groupinstall "Development Tools"
sudo yum -y install python{,-pip}
```


## Install

```bash
sudo -H pip install git+https://github.com/eternalharvest/r53update
```

## Usage

```bash
r53update www example.com
```

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
