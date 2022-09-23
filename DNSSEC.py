from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QDialog
from DB import *
import cf


class DNSSEC(QDialog):

    def __init__(self, *args, **kwargs):
        super(DNSSEC, self).__init__(*args, **kwargs)
        self.__db = DB()
        self.tmp_data = self.__db.select_tmp_data()
        self.cf = cf.CloudFlareAPI()
        zone = self.cf.get_zone(self.tmp_data["zone_id"])
        uic.loadUi("Templates/dnssec.ui", self)
        self.lineEditID.setText(self.tmp_data["zone_id"])
        self.lineEditID.setVisible(False)
        self.setWindowTitle("DNSSEC - " + zone["name"])
        self.pushButtonEnableDisable.clicked.connect(self.changeStatus)
        self.dnssecFields()

    def dnssecFields(self):
        dnssec_status = self.cf.getDNSSEC(self.tmp_data["zone_id"])
        if dnssec_status["status"] != "disabled":
            self.plainTextEditDSRecord.setPlainText(str(dnssec_status["ds"]))
            self.lineEditDigest.setText(str(dnssec_status["digest"]))
            self.lineEditDigestType.setText(str(dnssec_status["digest_type"]) + " - " + str(dnssec_status["digest_algorithm"]))
            self.lineEditAlgorithm.setText(str(dnssec_status["algorithm"]))
            self.lineEditKeyTag.setText(str(dnssec_status["key_tag"]))
            self.lineEditFlags.setText(str(dnssec_status["flags"]))
            self.lineEditPublicKey.setText(str(dnssec_status["public_key"]))
            self.lineEditKeyType.setText(str(dnssec_status["key_type"]))
            self.pushButtonEnableDisable.setText("Disable")
        else:
            self.plainTextEditDSRecord.clear()
            self.lineEditDigest.clear()
            self.lineEditDigestType.clear()
            self.lineEditAlgorithm.clear()
            self.lineEditAlgorithm.clear()
            self.lineEditKeyTag.clear()
            self.lineEditFlags.clear()
            self.lineEditPublicKey.clear()
            self.lineEditKeyType.clear()
            self.pushButtonEnableDisable.setText("Enable")
        self.groupBox.setTitle(str("DNSSEC - " + dnssec_status["status"]))

    def changeStatus(self):
        dnssec_status = self.cf.getDNSSEC(self.tmp_data["zone_id"])
        if dnssec_status["status"] == "disabled":
            self.cf.enableDNSSEC(self.tmp_data["zone_id"])
        else:
            self.cf.disableDNSSEC(self.tmp_data["zone_id"])
        self.dnssecFields()





