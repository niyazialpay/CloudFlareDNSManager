from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox
from DB import *
import cf
from cf import UnderAttack as ua
import threading

regex = regex_data.regex_data()


class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        # main
        super().__init__()
        self.__db = DB()
        self.__cf = cf.CloudFlareAPI()
        self.under_attack = ua.UnderAttack()
        uic.loadUi('Templates/main.ui', self)
        self.icon = QtGui.QIcon('Templates/img/icon.ico')

        self.delete_icon = QtGui.QIcon('Templates/img/delete.png')
        self.edit_icon = QtGui.QIcon('Templates/img/edit.png')
        self.copy_icon = QtGui.QIcon('Templates/img/copy.png')
        self.details_icon = QtGui.QIcon('Templates/img/details.png')
        self.whois_icon = QtGui.QIcon('Templates/img/whois.png')
        self.dnssec_icon = QtGui.QIcon('Templates/img/dnssec.png')
        self.settings_icon = QtGui.QIcon('Templates/img/settings.png')

        self.menu = QtWidgets.QMenu()

        self.copy_column_action = self.menu.addAction("Copy")
        self.copy_column_action.setIcon(self.copy_icon)

        self.edit_column_action = self.menu.addAction("Edit")
        self.edit_column_action.setIcon(self.edit_icon)

        self.delete_column_action = self.menu.addAction("Delete")
        self.delete_column_action.setIcon(self.delete_icon)

        self.details_menu = QtWidgets.QMenu()

        self.details_column_action = self.details_menu.addAction("Details")
        self.details_column_action.setIcon(self.details_icon)

        self.details_column_whois_action = self.details_menu.addAction("Whois")
        self.details_column_whois_action.setIcon(self.whois_icon)

        self.details_column_dnssec_action = self.details_menu.addAction("DNSSEC")
        self.details_column_dnssec_action.setIcon(self.dnssec_icon)

        self.details_column_settings_action = self.details_menu.addAction("Settings")
        self.details_column_settings_action.setIcon(self.settings_icon)

        self.delete_details_menu_action = self.details_menu.addAction("Delete")
        self.delete_details_menu_action.setIcon(self.delete_icon)

        if self.__cf.cf is None:
            self.tabWidget.setCurrentIndex(4)

    def setupUi(self):
        self.btnReplace.clicked.connect(self.btnReplace_click)

        api = self.__db.select_api()
        if api is not None:
            self.txtKey.setText(api['api_key'])
            self.txtEmail.setText(api['email'])
        self.saveButton.clicked.connect(self.saveSettings)
        self.pushButtonAddDomain.setEnabled(False)
        self.btnClearCache.setEnabled(False)
        self.btnUnderAttack.setEnabled(False)
        self.lineEditSearchRecord.setEnabled(False)
        self.comboBoxRecordType.setEnabled(False)
        self.pushButtonAddRecord.setEnabled(False)

        self.DomainListThread()

        self.tableWidgetDomainList.itemDoubleClicked.connect(self.domainDetails)
        self.tableWidgetDomainList.itemClicked.connect(self.listDNSRecordsThread)

        self.lineEditSearchDomain.returnPressed.connect(self.DomainListThread)

        self.tableWidgetDomainList.setColumnHidden(1, True)

        self.tableWidgetDomainList.customContextMenuRequested.connect(self.customContextDomainDetails)

        self.tableWidgetDnsRecords.customContextMenuRequested.connect(self.customContextRecordChange)
        self.tableWidgetDnsRecords.setColumnHidden(4, True)
        self.tableWidgetDnsRecords.verticalHeader().setVisible(False)

        self.tableWidgetResolver.verticalHeader().setVisible(False)
        self.tableWidgetResolver.setColumnHidden(1, True)

        self.tableWidgetDnsRecords.setColumnWidth(0, 50)
        self.tableWidgetDnsRecords.setColumnWidth(1, 200)
        self.tableWidgetDnsRecords.setColumnWidth(2, 325)
        self.tableWidgetDnsRecords.setColumnWidth(3, 80)

        self.lineEditSearchRecord.returnPressed.connect(self.searchRecord_click)

        self.pushButtonAddDomain.clicked.connect(self.addDomain)

        self.pushButtonAddRecord.clicked.connect(self.addRecord)

        self.btnUnderAttack.setText("Under Attack")
        self.btnUnderAttack.clicked.connect(self.underAttack)

        self.pushButtonQuery.clicked.connect(self.dnsQuery_run)
        self.lineEditDomainQuery.returnPressed.connect(self.dnsQuery_run)
        self.pushButtonWhois.clicked.connect(self.whoisQuery_run)
        self.lineEditDomainWhois.returnPressed.connect(self.whoisQuery_run)

        self.dnsResolverListThread()

        self.pushButtonResolverRemove.clicked.connect(self.dnsResolverDelete)
        self.pushButtonResolverAdd.clicked.connect(self.dnsResolverAdd)

        self.btnClearCache.clicked.connect(self.clearCache)

        self.show()

    def clearCache(self):
        self.__cf.purge_cache(self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text())
        self.messageBox("Cache cleared", "Success", "Information")

    def btnReplace_click(self):
        threading.Thread(target=self.replace_run).start()

    def underAttack(self):
        threading.Thread(target=self.underAttack_run).start()

    def underAttack_run(self):
        zone_id = self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text()
        status = self.under_attack.getSecurityLevel(zone_id)
        if status["value"] != "under_attack":
            self.under_attack.enableUA(zone_id)
            self.btnUnderAttack.setText("Under Attack\n(enabled)")
        else:
            self.under_attack.disableUA(zone_id)
            self.btnUnderAttack.setText("Under Attack\n(disabled)")
        self.listDnsRecords()

    def listDomains(self):
        if self.lineEditSearchDomain.text() != "":
            domain = self.lineEditSearchDomain.text()
        else:
            domain = None
        zones = self.__cf.get_zones(domain)
        self.tableWidgetDomainList.setRowCount(0)
        for row_number, row_data in enumerate(zones):
            self.tableWidgetDomainList.insertRow(row_number)
            self.tableWidgetDomainList.setItem(row_number, 0, QtWidgets.QTableWidgetItem(
                str(row_data['name'])))
            self.tableWidgetDomainList.setItem(row_number, 1, QtWidgets.QTableWidgetItem(
                str(row_data['id'])))
        if len(zones) == 0:
            self.pushButtonAddDomain.setEnabled(True)
            self.pushButtonAddDomain.setFont(QFont('MS Shell Dlg 2', 10, QFont.Weight.Bold))
            self.btnClearCache.setEnabled(False)
            self.btnUnderAttack.setEnabled(False)
            self.lineEditSearchRecord.setEnabled(False)
            self.lineEditSearchRecord.setEnabled(False)
            self.comboBoxRecordType.setEnabled(False)
            self.pushButtonAddRecord.setEnabled(False)
        else:
            self.pushButtonAddDomain.setEnabled(False)
            self.pushButtonAddDomain.setFont(QFont('MS Shell Dlg 2', 7, QFont.Weight.Thin))
            self.lineEditSearchRecord.clear()

    def DomainListThread(self):
        threading.Thread(target=self.listDomains()).start()

    def domainDetails(self, domain_id=None):
        from DomainDetails import DomainDetails
        if domain_id is not None:
            self.__db.insert_tmp_data(domain_id)
        else:
            self.__db.insert_tmp_data(
                self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text())
        w = DomainDetails()
        w.exec()

    def showDNSSEC(self, domain_id=None):
        from DNSSEC import DNSSEC
        if domain_id is not None:
            self.__db.insert_tmp_data(domain_id)
        else:
            self.__db.insert_tmp_data(
                self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text())
        w = DNSSEC()
        w.exec()

    def showSettings(self, domain_id=None):
        from settings import Settings
        if domain_id is not None:
            self.__db.insert_tmp_data(domain_id)
        else:
            self.__db.insert_tmp_data(
                self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text())
        w = Settings()
        w.exec()

    def searchRecord_click(self):
        threading.Thread(target=self.listDnsRecords()).start()

    def listDnsRecords(self):
        if self.lineEditSearchRecord.text() != "":
            search = self.lineEditSearchRecord.text()
            match = "any"
        else:
            search = None
            match = "all"
        self.tableWidgetDnsRecords.setRowCount(0)
        dns_records = self.__cf.get_dns_records(
            self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text(),
            search=search,
            match=match
        )
        new_list = []
        for records in dns_records:
            if records['type'] in [self.comboBoxRecordType.itemText(i) for i in range(self.comboBoxRecordType.count())]:
                new_list.append(records)
        for row_number, row_data in enumerate(new_list):
            self.tableWidgetDnsRecords.insertRow(row_number)
            self.tableWidgetDnsRecords.setItem(row_number, 0, QtWidgets.QTableWidgetItem(str(row_data['type'])))
            self.tableWidgetDnsRecords.setItem(row_number, 1, QtWidgets.QTableWidgetItem(str(row_data['name'])))
            self.tableWidgetDnsRecords.setItem(row_number, 2, QtWidgets.QTableWidgetItem(str(row_data['content'])))

            if row_data['proxied']:
                icon = QtGui.QIcon(QtGui.QPixmap("Templates/img/proxied_on.png").scaled(55, 35))
                item = QtWidgets.QTableWidgetItem(icon, "Proxied")
            else:
                icon = QtGui.QIcon(QtGui.QPixmap("Templates/img/proxied_off.png").scaled(55, 35))
                item = QtWidgets.QTableWidgetItem(icon, "DNS Only")

            self.tableWidgetDnsRecords.setItem(row_number, 3, item)
            self.tableWidgetDnsRecords.setItem(row_number, 4, QtWidgets.QTableWidgetItem(str(row_data['id'])))
        self.btnClearCache.setEnabled(True)
        self.btnUnderAttack.setEnabled(True)
        self.lineEditSearchRecord.setEnabled(True)
        self.lineEditSearchRecord.setEnabled(True)
        self.lineEditSearchRecord.setEnabled(True)
        self.comboBoxRecordType.setEnabled(True)
        self.pushButtonAddRecord.setEnabled(True)
        if self.under_attack.getSecurityLevel(
                self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text())[
            "value"] == "under_attack":
            self.btnUnderAttack.setText("Under Attack\n(on)")
        else:
            self.btnUnderAttack.setText("Under Attack\n(off)")

    def listDNSRecordsThread(self):
        threading.Thread(target=self.listDnsRecords()).start()

    def saveSettings(self):
        txtKey = self.txtKey.text()
        txtEmail = self.txtEmail.text()
        if txtEmail != "" or txtKey != "":
            if self.__db.insert_api(txtKey, txtEmail):
                self.close()
            else:
                Ui().messageBox('Something went wrong!', 'Warning', 'Warning')
        else:
            Ui().messageBox('Please fill in all fields', 'Warning', 'Warning')

    def replace_run(self):
        old_ip_address = regex.string(self.txtOldIP.text())
        new_ip_address = regex.string(self.txtNewIP.text())
        if old_ip_address == "" or new_ip_address == "":
            self.messageBox("Please fill in all fields", "Error", "Critical")
        else:
            try:
                cloud_flare = cf.CloudFlareAPI()
                zones = cloud_flare.get_zones()
                for zone in zones:
                    zone_name = zone['name']
                    zone_id = zone['id']
                    dns_records = cloud_flare.get_dns_records(zone_id, 'A')
                    self.textBrowser.append(f"{zone_name}")
                    self.textBrowser.append(f"{'-' * len(zone_name)}")
                    self.textBrowser.append("Current DNS Records:")
                    for dns in dns_records:
                        self.textBrowser.append(f"{dns['name']} - {dns['content']}")
                        if old_ip_address == dns['content']:
                            self.textBrowser.append(f"{'-' * len(zone_name)}")
                            cloud_flare.update_dns_record(zone_id, dns['id'],
                                                          {'content': new_ip_address, 'name': dns['name'], 'type': 'A'})
                            self.textBrowser.append(f"Updated record {dns['name']} to {new_ip_address}")
                            self.textBrowser.append(f"{'-' * len(zone_name)}")
                            cloud_flare.purge_cache(zone['id'])
                            self.textBrowser.append(f"Cache purged for {zone_name}\r\n")
                    self.textBrowser.verticalScrollBar().setValue(
                        self.textBrowser.verticalScrollBar().maximum() * 2
                    )
                self.messageBox("IP Address has been updated successfully", "Success", "Information")
            except Exception as e:
                self.messageBox("An error occurred while updating the IP Address", "Error", "Critical")
                self.textBrowser.append(f"Error: {e}")

    def messageBox(self, alert_message, alert_title, alert_icon):
        message = QMessageBox()
        if alert_icon == "Critical":
            message_icon = QMessageBox.Icon.Critical
        elif alert_icon == "Warning":
            message_icon = QMessageBox.Icon.Warning

        elif alert_icon == "Information":
            message_icon = QMessageBox.Icon.Information
        else:
            message_icon = QMessageBox.Icon.Critical
        message.setIcon(message_icon)
        message.setText(alert_message)
        message.setWindowTitle(alert_title)
        message.setWindowIcon(self.icon)
        message.exec()

    def customContextRecordChange(self, pos):
        try:
            action = self.menu.exec(self.tableWidgetDnsRecords.viewport().mapToGlobal(pos))
            if action == self.delete_column_action:
                reply = QMessageBox().question(self, 'Delete',
                                               "Are you want to sure to delete this DNS record?\n\n" + self.tableWidgetDnsRecords.item(
                                                   self.tableWidgetDnsRecords.currentRow(),
                                                   0).text() + " " + self.tableWidgetDnsRecords.item(
                                                   self.tableWidgetDnsRecords.currentRow(), 1).text(),
                                               QMessageBox().StandardButton.Yes,
                                               QMessageBox().StandardButton.No)

                if reply == QMessageBox().StandardButton.Yes:
                    self.__cf.delete_dns_record(
                        self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text(),
                        self.tableWidgetDnsRecords.item(self.tableWidgetDnsRecords.currentRow(), 4).text())
                self.listDNSRecordsThread()

            if action == self.edit_column_action:
                self.editRecords()
                self.listDNSRecordsThread()

            if action == self.copy_column_action:
                self.copyDNSRecord()
        except Exception as e:
            print(e)
            self.messageBox('You must select a valid row!', 'Warning', 'Warning')

    def customContextDomainDetails(self, pos):
        try:
            action = self.details_menu.exec(self.tableWidgetDomainList.viewport().mapToGlobal(pos))
            if action == self.delete_details_menu_action:
                reply = QMessageBox().question(self, 'Delete',
                                               "Are you want to sure to delete this domain?\n\n" + self.tableWidgetDomainList.item(
                                                   self.tableWidgetDomainList.currentRow(),
                                                   0).text(),
                                               QMessageBox().StandardButton.Yes,
                                               QMessageBox().StandardButton.No)

                if reply == QMessageBox().StandardButton.Yes:
                    self.deleteDomain(
                        self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text())
                self.DomainListThread()

            if action == self.details_column_whois_action:
                self.lineEditDomainWhois.setText(self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 0).text())
                self.whoisQuery_run()
                self.tabWidget.setCurrentIndex(3)

            if action == self.details_column_action:
                self.domainDetails()

            if action == self.details_column_dnssec_action:
                self.showDNSSEC()

            if action == self.details_column_settings_action:
                self.showSettings()
        except Exception as e:
            print(e)
            self.messageBox('You must select a valid row!', 'Warning', 'Warning')

    def copyDNSRecord(self):
        import clipboard
        clipboard.copy(self.tableWidgetDnsRecords.item(self.tableWidgetDnsRecords.currentRow(),
                                                       1).text() + " " + self.tableWidgetDnsRecords.item(
            self.tableWidgetDnsRecords.currentRow(), 0).text() + " " + self.tableWidgetDnsRecords.item(
            self.tableWidgetDnsRecords.currentRow(), 2).text())
        self.messageBox("DNS Record has been copied to clipboard.", "Information", "Information")

    def editRecords(self):
        self.__addEditRecord()

    def addRecord(self):
        self.__addEditRecord("new_record")

    def __addEditRecord(self, record_type=None):
        from EditRecords import EditRecords
        if record_type is not None:
            dns_id = "new_record"
        else:
            dns_id = self.tableWidgetDnsRecords.item(self.tableWidgetDnsRecords.currentRow(), 4).text()

        self.__db.insert_tmp_data(self.tableWidgetDomainList.item(self.tableWidgetDomainList.currentRow(), 1).text(),
                                  dns_id,
                                  self.comboBoxRecordType.currentText())
        w = EditRecords()
        w.exec()
        self.listDNSRecordsThread()

    def addDomain(self):
        if self.lineEditSearchDomain.text() != "":
            result = self.__cf.add_zone(self.lineEditSearchDomain.text())
            if len(result) > 0:
                self.DomainListThread()
                self.domainDetails(result["id"])
            else:
                self.messageBox("Domain could not be added!", "Error", "Critical")
        else:
            self.messageBox("Please enter a domain name!", "Error", "Critical")

    def deleteDomain(self, zone_id):
        self.__cf.delete_zone(zone_id)
        self.DomainListThread()

    def dnsQuery_run(self):
        threading.Thread(target=self.dnsQuery()).start()

    def dnsResolverList(self):
        dns_resolver_list = self.__db.get_resolver_list()
        self.tableWidgetResolver.setRowCount(0)
        for row_number, row_data in enumerate(dns_resolver_list):
            self.tableWidgetResolver.insertRow(row_number)
            self.tableWidgetResolver.setItem(row_number, 0, QtWidgets.QTableWidgetItem(
                str(row_data['ip'])))
            self.tableWidgetResolver.setItem(row_number, 1, QtWidgets.QTableWidgetItem(
                str(row_data['id'])))

    def dnsResolverListThread(self):
        threading.Thread(target=self.dnsResolverList()).start()

    def dnsResolverAdd(self):
        if self.lineEditResolver.text() != "":
            self.__db.insert_resolver(self.lineEditResolver.text())
            self.dnsResolverListThread()
        else:
            self.messageBox("Please enter a resolver IP address!", "Error", "Critical")

    def dnsResolverDelete(self):
        if self.tableWidgetResolver.currentRow() != -1:
            if len(self.__db.get_resolver_list()) > 1:
                self.__db.remove_resolver(
                    self.tableWidgetResolver.item(self.tableWidgetResolver.currentRow(), 0).text())
                self.dnsResolverListThread()
            else:
                self.messageBox("You must have at least one resolver!", "Error", "Critical")
        else:
            self.messageBox("Please select a resolver!", "Error", "Critical")

    def dnsQuery(self):
        self.textBrowserResult.clear()
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver_list = self.__db.get_resolver_list()
            nameservers = []
            for resolver_item in resolver_list:
                nameservers.append(resolver_item["ip"])
            resolver.nameservers = nameservers
            answers = resolver.resolve(self.lineEditDomainQuery.text(), self.comboBoxRecordType_2.currentText())

            for rdata in answers:
                self.textBrowserResult.append(str(rdata))
        except Exception as e:
            self.textBrowserResult.append(str(e))

    def whoisQuery_run(self):
        threading.Thread(target=self.whoisQuery()).start()

    def whoisQuery(self):
        if self.lineEditDomainWhois.text() != "":
            import whois
            self.textBrowserWhoisResult.clear()
            result = whois.whois(self.lineEditDomainWhois.text())
            for key, value in result.items():
                self.textBrowserWhoisResult.append(key + " : " + str(value))
        else:
            self.messageBox("Please enter a domain name!", "Error", "Critical")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.setupUi()
    sys.exit(app.exec())
