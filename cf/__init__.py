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
            return self.cf.zones.settings.security_level.patch(zone_id, data={
            'value': 'under_attack'})  # high, medium, low, under_attack
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
