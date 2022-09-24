from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from DB import *
import cf
from main import Ui
import ipaddress


class EditRecords(QDialog):

    def __init__(self, *args, **kwargs):
        super(EditRecords, self).__init__(*args, **kwargs)
        self.__db = DB()
        self.tmp_data = self.__db.select_tmp_data()
        self.cf = cf.CloudFlareAPI()
        if self.tmp_data["dns_id"] == "new_record":
            self.record = None
            self.record_type = self.tmp_data["dns_type"]
            self.record_id = None
        else:
            self.record = self.cf.get_dns_record(self.tmp_data["zone_id"], self.tmp_data["dns_id"])
            self.record_type = self.record["type"]
            self.record_id = self.record["id"]
        self.template()

    @staticmethod
    def IPBlacklist(IP):
        IPList = [
            "127.0.0.1/32",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
        ]
        for ip in IPList:
            status = ipaddress.ip_address(IP) in ipaddress.ip_network(ip)
            if status:
                return True

    def template(self):
        if self.record_type == "A" or self.record_type == "AAAA" or self.record_type == "CNAME":
            uic.loadUi("Templates/dns_record_a_aaaa_cname.ui", self)
            self.Record_A_AAA_CNAME()
        elif self.record_type == "TXT":
            uic.loadUi("Templates/dns_record_txt.ui", self)
            self.Record_TXT_MX()
        elif self.record_type == "MX":
            uic.loadUi("Templates/dns_record_mx.ui", self)
            self.Record_TXT_MX()
        elif self.record_type == "SRV":
            uic.loadUi("Templates/dns_record_srv.ui", self)
            self.Record_SRV()
        elif self.record_type == "CAA":
            uic.loadUi("Templates/dns_record_caa.ui", self)
            self.Record_CAA()
        else:
            uic.loadUi("Templates/dns_record_a_aaaa_cname.ui", self)
            self.Record_A_AAA_CNAME()
        self.lineEditID.setVisible(False)
        self.setWindowTitle("DNS Record Type: " + self.record_type)
        self.pushButtonSave.clicked.connect(self.saveRecord)

    def Record_A_AAA_CNAME(self):
        if self.record is None:
            record = None
        else:
            record = self.record
        if record is not None:
            self.lineEditID.setText(record["id"])
            self.lineEditDomain.setText(record["name"])
            self.lineEditContent.setText(record["content"])
            if record["proxied"]:
                self.checkBox.setChecked(True)
                self.checkBox.setToolTip("Proxied")
            else:
                self.checkBox.setChecked(False)
                self.checkBox.setToolTip("DNS Only")

        self.lineEditID.setVisible(False)

    def Record_TXT_MX(self):
        if self.record is None:
            record = None
        else:
            record = self.record
        if record is not None:
            self.lineEditID.setText(record["id"])
            self.lineEditDomain.setText(record["name"])
            self.lineEditContent.setText(record["content"])
            if record["type"] == "MX":
                self.lineEditPriority.setText(str(record["priority"]))

    def Record_SRV(self):
        if self.record is None:
            record = None
        else:
            record = self.record
        if record is not None:
            self.lineEditID.setText(record["id"])
            self.lineEditDomain.setText(record["data"]["name"])
            self.lineEditTarget.setText(record["data"]["target"])
            self.lineEditPriority.setText(str(record["data"]["priority"]))
            self.lineEditPort.setText(str(record["data"]["port"]))
            self.lineEditWeight.setText(str(record["data"]["weight"]))
            self.lineEditService.setText(str(record["data"]["service"]))
            if record["data"]["proto"] == "_tcp":
                self.comboBoxProtocol.setCurrentIndex(0)
            elif record["data"]["proto"] == "_udp":
                self.comboBoxProtocol.setCurrentIndex(1)
            elif record["data"]["proto"] == "_tls":
                self.comboBoxProtocol.setCurrentIndex(2)
            else:
                self.comboBoxProtocol.setCurrentIndex(0)

    def Record_CAA(self):
        if self.record is None:
            record = None
        else:
            record = self.record
        if record is not None:
            if record["data"]["tag"] == "issue":
                self.comboBoxTag.setCurrentIndex(0)
            elif record["data"]["tag"] == "issuewild":
                self.comboBoxTag.setCurrentIndex(1)
            elif record["data"]["tag"] == "iodef":
                self.comboBoxTag.setCurrentIndex(2)
            else:
                self.comboBoxTag.setCurrentIndex(0)

            self.lineEditID.setText(record["id"])
            self.lineEditDomain.setText(record["name"])
            self.lineEditCADomainName.setText(record["data"]["value"])

    def saveRecord(self):
        if self.record_type == "A" or self.record_type == "AAAA" or self.record_type == "CNAME":
            if self.record_type == "A":
                if self.IPBlacklist(self.lineEditContent.text()):
                    proxied = False
                else:
                    proxied = self.checkBox.isChecked()
            else:
                proxied = self.checkBox.isChecked()
            data = {
                "type": self.record_type,
                "name": self.lineEditDomain.text(),
                "content": self.lineEditContent.text(),
                "proxied": proxied
            }
        elif self.record_type == "TXT":
            data = {
                "type": self.record_type,
                "name": self.lineEditDomain.text(),
                "content": self.lineEditContent.toPlainText(),
            }
        elif self.record_type == "MX":
            data = {
                "type": self.record_type,
                "name": self.lineEditDomain.text(),
                "content": self.lineEditContent.text(),
                "priority": int(self.lineEditPriority.text())
            }
        elif self.record_type == "SRV":
            if self.comboBoxProtocol.currentIndex() == 0:
                proto = "_tcp"
            elif self.comboBoxProtocol.currentIndex() == 1:
                proto = "_udp"
            elif self.comboBoxProtocol.currentIndex() == 2:
                proto = "_tls"
            else:
                proto = "_tcp"
            data = {
                "type": self.record_type,
                "name": self.lineEditService.text() + "." + proto + "." + self.lineEditDomain.text(),
                "data": {
                    "name": self.lineEditDomain.text(),
                    "target": self.lineEditTarget.text(),
                    "priority": int(self.lineEditPriority.text()),
                    "port": int(self.lineEditPort.text()),
                    "proto": proto,
                    "service": self.lineEditService.text(),
                    "weight": int(self.lineEditWeight.text())
                }
            }
        elif self.record_type == "CAA":
            if self.comboBoxTag.currentText() == "Only Allow Specific Hostname":
                tag = "issue"
            elif self.comboBoxTag.currentText() == "Only Allow Wildcards":
                tag = "issuewild"
            elif self.comboBoxTag.currentText() == "Send Violation Reports to URL (http:, https: or mailto:)":
                tag = "iodef"
            else:
                tag = "issue"
            data = {
                "type": self.record_type,
                "name": self.lineEditDomain.text(),
                "data": {
                    "tag": tag,
                    "value": self.lineEditCADomainName.text(),
                    "flags": 0
                }
            }
        else:
            data = {
                "type": self.record_type,
                "name": self.lineEditDomain.text(),
                "content": self.lineEditContent.text(),
                "proxied": self.checkBox.isChecked()
            }
        if self.tmp_data["dns_id"] == "new_record":
            response = self.cf.add_dns_record(self.tmp_data["zone_id"], data)
        else:
            response = self.cf.update_dns_record(self.tmp_data["zone_id"], self.record_id, data=data)
        if len(response) > 0:
            self.close()
        else:
            Ui().messageBox('Something went wrong!', 'Warning', 'Warning')
