from cf import CloudFlareAPI, db


class UnderAttack(CloudFlareAPI):

    def enableUA(self, zone_id):
        try:
            records = self.get_unproxied_dns_records(zone_id)
            security_level = self.getSecurityLevel(zone_id)
            for record in records:
                if record["type"] == "A" or record["type"] == "AAAA" or record["type"] == "CNAME":
                    if record['proxied']:
                        proxied = "true"
                    else:
                        proxied = "false"
                    db.insert_under_attack(record["zone_id"], record['id'], record["type"], record['name'],
                                           record['content'], proxied, security_level['value'])
                    self.update_dns_record(zone_id, record['id'], {'name': record['name'], 'content': record['content'],
                                                                   'type': record['type'], 'proxied': True})
            self.cf.zones.settings.security_level.patch(zone_id, data={'value': 'under_attack'})
            return True
        except Exception as e:
            print(e)
            return False

    def disableUA(self, zone_id):
        try:
            records = db.select_under_attack(zone_id)
            security_level = "medium"
            for record in records:
                if record['dns_proxied'] == "true":
                    proxied = True
                else:
                    proxied = False
                self.update_dns_record(zone_id, record['dns_id'],
                                       {'name': record['dns_name'], 'content': record['dns_content'],
                                        'type': record['dns_type'], 'proxied': proxied})
                security_level = record['security_level']
            self.cf.zones.settings.security_level.patch(zone_id, data={'value': security_level})
            db.remove_under_attack(zone_id)
            return True
        except Exception as e:
            print(e)
            return False

    def getSecurityLevel(self, zone_id):
        return self.cf.zones.settings.security_level.get(zone_id)
