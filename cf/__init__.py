import CloudFlare
import DB

db = DB.DB()


class CloudFlareAPI:
    def __init__(self):
        api = db.select_api()
        if api is not None:
            try:
                if api['email'] is not None and api['api_key'] is not None:
                    try:
                        self.cf = CloudFlare.CloudFlare(email=api['email'], key=api['api_key'])
                    except Exception as e:
                        self.cf = None
                        print(e)
                else:
                    self.cf = None
            except Exception as e:
                self.cf = None
                print(e)
        else:
            self.cf = None

    def add_zone(self, zone_name):
        if self.cf is not None:
            return self.cf.zones.post(data={'name': zone_name})
        else:
            return []

    def get_zones(self, zone_name=None):
        if self.cf is not None:
            return self.cf.zones.get(params={'per_page': 999, 'name': zone_name, 'match': 'any'})
        else:
            return []

    def get_zone(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.get(zone_id)
        else:
            return []

    def delete_zone(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.delete(zone_id)
        else:
            return []

    def get_dns_records(self, zone_id, record_type=None, search=None, match=None):
        if self.cf is not None:
            return self.cf.zones.dns_records.get(zone_id, params={'per_page': 999, 'type': record_type, 'name': search,
                                                                  'content': search, 'match': match})
        else:
            return []

    def get_unproxied_dns_records(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.dns_records.get(zone_id, params={'per_page': 999, 'proxied': False})
        return []

    def get_dns_record(self, zone_id, dns_id):
        if self.cf is not None:
            return self.cf.zones.dns_records.get(zone_id, dns_id)
        else:
            return []

    def add_dns_record(self, zone_id, data):
        if self.cf is not None:
            return self.cf.zones.dns_records.post(zone_id, data=data)
        else:
            return []

    def update_dns_record(self, zone_id, dns_id, data):
        if self.cf is not None:
            return self.cf.zones.dns_records.put(zone_id, dns_id, data=data)
        else:
            return []

    def delete_dns_record(self, zone_id, dns_id):
        if self.cf is not None:
            return self.cf.zones.dns_records.delete(zone_id, dns_id)
        else:
            return []

    def purge_cache(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.purge_cache.delete(zone_id, data={'purge_everything': True})
        else:
            return []

    def development_mode(self, zone_id, status):
        if self.cf is not None:
            return self.cf.zones.settings.development_mode.patch(zone_id, data={'value': status})  # on or off
        else:
            return []

    def under_attack(self, zone_id):
        if self.cf is not None:
            return self.EditSecurityLevelSettings(zone_id, {'value': 'under_attack'})
        else:
            return []

    def getSecurityLevel(self, zone_id):
        return self.cf.zones.settings.security_level.get(zone_id)

    def EditSecurityLevelSettings(self, zon_id, data):
        """
        default value: medium
        valid values: off, essentially_off, low, medium, high, under_attack
        """
        if self.cf is not None:
            return self.cf.zones.settings.security_level.patch(zon_id, data=data)  # high, medium, low, under_attack
        else:
            return []

    def getDNSSEC(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.dnssec.get(zone_id)
        else:
            return []

    def enableDNSSEC(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.dnssec.patch(zone_id, data={"status": "active"})
        else:
            return []

    def disableDNSSEC(self, zone_id):
        if self.cf is not None:
            self.cf.zones.dnssec.patch(zone_id, data={"status": "disabled"})
            return self.cf.zones.dnssec.delete(zone_id)
        else:
            return []

    def getSSLSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.ssl.get(zone_id)
        else:
            return []

    def editSSLSettingns(self, zone_id, data):
        if self.cf is not None:
            """
            {
              "value": "flexible"
            }
            """
            return self.cf.zones.settings.ssl.patch(zone_id, data={"value": data})
        else:
            return []

    def getHSTSsettigs(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.security_header.get(zone_id)
        else:
            return []

    def editHSTSsettings(self, zone_id, data):
        if self.cf is not None:
            return self.cf.zones.settings.security_header.patch(zone_id, data={
                "value": {
                    "strict_transport_security": {
                        "enabled": data,
                        "max_age": 86400,
                        "include_subdomains": True,
                        "nosniff": True
                    }
                }
            })
        else:
            return []

    def getMinimumTLSsettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.min_tls_version.get(zone_id)
        else:
            return []

    def editMinimumTLSsettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: 1.0
            valid values: 1.0, 1.1, 1.2, 1.3
            """
            return self.cf.zones.settings.min_tls_version.patch(zone_id, data={'value': data})
        else:
            return []

    def getTLS13settings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.tls_1_3.get(zone_id)
        else:
            return []

    def editTLS13settings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: off
            valid values: on, off, zrt
            """
            return self.cf.zones.settings.tls_1_3.patch(zone_id, data={'value': data})
        else:
            return []

    def getAlwaysUseHTTPSsettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.always_use_https.get(zone_id)
        else:
            return []

    def editAlwaysUseHTTPSsettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: off
            valid values: on, off
            """
            return self.cf.zones.settings.always_use_https.patch(zone_id, data={'value': data})
        else:
            return []

    def getAutomaticHTTPSsettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.automatic_https_rewrites.get(zone_id)
        else:
            return []

    def editAutomaticHTTPSsettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: on
            valid values: on, off
            """
            return self.cf.zones.settings.automatic_https_rewrites.patch(zone_id, data={'value': data})
        else:
            return []

    def getCacheLevelSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.cache_level.get(zone_id)
        else:
            return []

    def editCacheLevelSettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: aggressive
            valid values: basic, aggressive, simplified
            """
            return self.cf.zones.settings.cache_level.patch(zone_id, data={'value': data})
        else:
            return []

    def getBrowserCacheTTLSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.browser_cache_ttl.get(zone_id)
        else:
            return []

    def editBrowserCacheTTLSettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: 14400
            valid values: 300, 900, 1800, 2700, 3600, 7200, 10800, 14400, 28800, 57600, 86400, 604800, 2592000, 31536000
            """
            return self.cf.zones.settings.browser_cache_ttl.patch(zone_id, data={'value': data})
        else:
            return []

    def getAlwaysOnlineSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.always_online.get(zone_id)
        else:
            return []

    def editAlwaysOnlineSettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: off
            valid values: on, off
            """
            return self.cf.zones.settings.always_online.patch(zone_id, data={'value': data})
        else:
            return []

    def getHttp3Settings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.http3.get(zone_id)
        else:
            return []

    def getHTTP3settings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.http3.get(zone_id)
        else:
            return []

    def editHTTP3settings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: off
            valid values: on, off
            """
            return self.cf.zones.settings.http3.patch(zone_id, data={'value': data})
        else:
            return []

    def getWebSocketsSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.websockets.get(zone_id)
        else:
            return []

    def editWebSocketsSettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: on
            valid values: on, off
            """
            return self.cf.zones.settings.websockets.patch(zone_id, data={'value': data})
        else:
            return []

    def getIPGeolocationSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.ip_geolocation.get(zone_id)
        else:
            return []

    def editIPGeolocationSettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: on
            valid values: on, off
            """
            return self.cf.zones.settings.ip_geolocation.patch(zone_id, data={'value': data})
        else:
            return []

    def getOninonRoutingSettings(self, zone_id):
        if self.cf is not None:
            return self.cf.zones.settings.opportunistic_encryption.get(zone_id)
        else:
            return []

    def editOninonRoutingSettings(self, zone_id, data):
        if self.cf is not None:
            """
            default value: off
            valid values: on, off
            """
            return self.cf.zones.settings.opportunistic_encryption.patch(zone_id, data={'value': data})
        else:
            return []
