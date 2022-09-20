import CloudFlare
import DB

db = DB.DB()


class CloudFlareAPI:
    def __init__(self):
        api = db.select_api()
        self.cf = CloudFlare.CloudFlare(email=api['email'], key=api['api_key'])

    def add_zone(self, zone_name):
        return self.cf.zones.post(data={'name': zone_name})

    def get_zones(self, zone_name=None):
        return self.cf.zones.get(params={'per_page': 999, 'name': zone_name, 'match': 'any'})

    def get_zone(self, zone_id):
        return self.cf.zones.get(zone_id)

    def delete_zone(self, zone_id):
        return self.cf.zones.delete(zone_id)

    def get_dns_records(self, zone_id, record_type=None, search=None, match=None):
        return self.cf.zones.dns_records.get(zone_id, params={'per_page': 999, 'type': record_type, 'name': search,
                                                              'content': search, 'match': match})

    def get_unproxied_dns_records(self, zone_id):
        return self.cf.zones.dns_records.get(zone_id, params={'per_page': 999, 'proxied': False})

    def get_dns_record(self, zone_id, dns_id):
        return self.cf.zones.dns_records.get(zone_id, dns_id)

    def add_dns_record(self, zone_id, data):
        return self.cf.zones.dns_records.post(zone_id, data=data)

    def update_dns_record(self, zone_id, dns_id, data):
        return self.cf.zones.dns_records.put(zone_id, dns_id, data=data)

    def delete_dns_record(self, zone_id, dns_id):
        return self.cf.zones.dns_records.delete(zone_id, dns_id)

    def purge_cache(self, zone_id):
        return self.cf.zones.purge_cache.delete(zone_id, data={'purge_everything': True})

    def development_mode(self, zone_id, status):
        return self.cf.zones.settings.development_mode.patch(zone_id, data={'value': status})  # on or off

    def under_attack(self, zone_id):
        return self.cf.zones.settings.security_level.patch(zone_id, data={
            'value': 'under_attack'})  # high, medium, low, under_attack
