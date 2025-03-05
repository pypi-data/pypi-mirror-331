import time
import requests
import json
import base64
import configparser
import zope.interface
from certbot import errors, interfaces
from certbot.plugins import dns_common

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.implementer(interfaces.IPlugin)
class HydraDNSAuthenticator(dns_common.DNSAuthenticator):
    """Hydra DNS Authenticator for Certbot DNS-01 challenge."""
    
    description = "Obtain certificates using the Hydra DNS API."

    @classmethod
    def add_parser_arguments(cls, add):
        """Define command-line arguments for Certbot"""
        add("config-file", help="Path to the Hydra DNS API credentials file")
        add("propagation-seconds", default=320, type=int, help="Time in seconds to wait for DNS propagation")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = "https://www.networks.it.ox.ac.uk/api/ipam"
        self.username = None
        self.password = None
        self.config_file = None

    def more_info(self):
        return "This plugin configures a DNS TXT record to respond to a DNS-01 challenge using the Hydra DNS API."

    def _setup_credentials(self):
        self.config_file = self.conf("config-file")
        if not self.config_file:
            raise errors.PluginError("Configuration file must be specified.")
        
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        try:
            self.username = config.get("dns_hydra", "api-username")
            self.password = config.get("dns_hydra", "api-password")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise errors.PluginError(f"Error reading configuration file: {e}")

    def _get_auth_header(self):
        auth_str = f"{self.username}:{self.password}"
        auth_encoded = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {auth_encoded}", "Content-Type": "application/json"}

    def _perform(self, domain, validation_name, validation):
        """Create a DNS TXT record for validation."""
        self._setup_credentials()
        record_data = {
            "hostname": validation_name,
            "type": "TXT",
            "content": validation,
            "ttl": 300,
            "comment": "Certbot ACME Challenge"
        }
        headers = self._get_auth_header()
        
        response = requests.post(f"{self.api_url}/records", json=record_data, headers=headers)
        if response.status_code != 202:
            raise errors.PluginError(f"Failed to create DNS record: {response.text}")
        
        time.sleep(10)  # Allow time for DNS propagation

    def _cleanup(self, domain, validation_name, validation):
        """Remove the DNS TXT record after validation."""
        self._setup_credentials()
        headers = self._get_auth_header()
        
        response = requests.delete(f"{self.api_url}/records?q={validation_name}", headers=headers)
        if response.status_code not in [200, 202]:
            raise errors.PluginError(f"Failed to delete DNS record: {response.text}")

# Entry point for Certbot
if __name__ == "__main__":
    from certbot.plugins.entry_point import main
    main(HydraDNSAuthenticator)

