# Certbot Hydra Plugin

A certbot Hydra plugin for use with the University of Oxford Hydra DNS system.

Enables the use of certbot to create a LetsEncrypt SSL certificate, which in turn can be used to automate SSL certificate renewal.

As the ownership validation mechanism uses DNS, no direct access is required to the website.


## Hydra Tokens

This plugin uses the Hydra API, access by the token based authentication mechanism, described at <https://blogs.it.ox.ac.uk/networks/2024/05/31/hydra-token-authentication/>, with further detail documented at <https://wiki.it.ox.ac.uk/networks/HydraTokens>.

To create a token, navigate to https://www.networks.it.ox.ac.uk/itss/ipam/allocations and then search for the (sub)domain you want to create a token for.

The token should be restricted to only have access to the records it needs to modify.


## Setup

To you use the plugin you should follow the instructions in the links above to generate a set of credentials then populate a config file (for example /etc/letsencrypt/dns-hydra.ini) with data in the following format:


```
[dns_hydra]
api-username = x/y 
api-password = zzzzzzzz

```

This file needs to be suitable secured as it contains credentials which can modify your dns and are also providing proof of ownership of the domain.

## Usage


Once installs, run with command:
```
certbot certonly --authenticator dns-hydra --dns-hydra-config-file /etc/letsencrypt/dns-hydra.ini -d yourdomain.jordan.ox.ac.uk
```

