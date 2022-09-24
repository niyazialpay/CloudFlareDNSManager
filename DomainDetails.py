from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from DB import *
import cf


class DomainDetails(QDialog):

    def __init__(self, *args, **kwargs):
        super(DomainDetails, self).__init__(*args, **kwargs)
        self.__db = DB()
        self.tmp_data = self.__db.select_tmp_data()
        self.cf = cf.CloudFlareAPI()
        zone = self.cf.get_zone(self.tmp_data["zone_id"])
        uic.loadUi("Templates/domain_details.ui", self)

        self.lineEditID.setText(self.tmp_data["zone_id"])
        self.lineEditID.setVisible(False)
        self.lineEditDomainName.setText(zone["name"])
        for item in zone["name_servers"]:
            self.textEditNameServers.append(item)
        self.lineEditOriginalDNSHost.setText(zone["original_dnshost"])
        self.lineEditOriginalRegistrar.setText(zone["original_registrar"])
        if zone["development_mode"]>0:
            self.checkBoxDevelopmentMode.setChecked(True)
        else:
            self.checkBoxDevelopmentMode.setChecked(False)
        self.checkBoxDevelopmentMode.stateChanged.connect(self.ChangeDevelopmentModeStatus)
        self.label_status.setText(zone["status"])

    def ChangeDevelopmentModeStatus(self):
        if self.checkBoxDevelopmentMode.isChecked():
            self.cf.development_mode(self.tmp_data["zone_id"], "on")
        else:
            self.cf.development_mode(self.tmp_data["zone_id"], "off")
