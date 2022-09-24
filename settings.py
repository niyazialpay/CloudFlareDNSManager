from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from DB import *
import cf
import threading
import time
from main import Ui


class Settings(QDialog):

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.__db = DB()
        self.getSettingsThread = threading.Thread(target=self.getAllSettings)
        self.tmp_data = self.__db.select_tmp_data()
        self.cf = cf.CloudFlareAPI()
        zone = self.cf.get_zone(self.tmp_data["zone_id"])
        uic.loadUi("Templates/settings.ui", self)
        self.lineEditID.setText(self.tmp_data["zone_id"])
        self.lineEditID.setVisible(False)
        self.setWindowTitle("Settings - " + zone["name"])

        self.getSettings_run()
        threading.Thread(target=self.progress).start()

        self.pushButtonSaveSecurity.clicked.connect(self.saveSecuritySettings)
        self.pushButtonSaveCache.clicked.connect(self.saveCacheSettings)
        self.pushButtonSaveNetwork.clicked.connect(self.saveNetworkSettings)

    def progress(self):
        while self.getSettingsThread.is_alive():
            if int(self.progressBar.value()) < 100:
                time.sleep(1)
                self.progressBar.setValue(int(self.progressBar.value()) + 5)

    def getAllSettings(self):
        zone = self.cf.get_zone(self.tmp_data["zone_id"])
        # security settings
        ssl_settings = self.cf.getSSLSettings(self.tmp_data["zone_id"])
        hsts_settings = self.cf.getHSTSsettigs(self.tmp_data["zone_id"])
        security_level = self.cf.getSecurityLevel(self.tmp_data["zone_id"])
        always_use_https = self.cf.getAlwaysUseHTTPSsettings(self.tmp_data["zone_id"])
        https_rewrites = self.cf.getAutomaticHTTPSsettings(self.tmp_data["zone_id"])
        tls13 = self.cf.getTLS13settings(self.tmp_data["zone_id"])
        # security settings

        # cache settings
        cache_level = self.cf.getCacheLevelSettings(self.tmp_data["zone_id"])
        browser_cache_ttl = self.cf.getBrowserCacheTTLSettings(self.tmp_data["zone_id"])
        always_online = self.cf.getAlwaysOnlineSettings(self.tmp_data["zone_id"])
        # cache settings

        # network settings
        min_tls_version = self.cf.getMinimumTLSsettings(self.tmp_data["zone_id"])
        onion_routing = self.cf.getOninonRoutingSettings(self.tmp_data["zone_id"])
        http3 = self.cf.getHttp3Settings(self.tmp_data["zone_id"])
        websockets = self.cf.getWebSocketsSettings(self.tmp_data["zone_id"])
        ip_geolocation = self.cf.getIPGeolocationSettings(self.tmp_data["zone_id"])
        # network settings

        if ssl_settings["value"] == "off":
            self.comboBoxSSL.setCurrentIndex(0)
        elif ssl_settings["value"] == "flexible":
            self.comboBoxSSL.setCurrentIndex(1)
        elif ssl_settings["value"] == "full":
            self.comboBoxSSL.setCurrentIndex(2)
        elif ssl_settings["value"] == "strict":
            self.comboBoxSSL.setCurrentIndex(3)
        else:
            self.comboBoxSSL.setCurrentIndex(0)

        if hsts_settings["value"] == "off":
            self.checkBoxHSTS.setChecked(False)
        else:
            self.checkBoxHSTS.setChecked(True)

        if security_level["value"] == "off":
            self.comboBoxSecurityLevel.setCurrentIndex(0)
        elif security_level["value"] == "essentially_off":
            self.comboBoxSecurityLevel.setCurrentIndex(1)
        elif security_level["value"] == "low":
            self.comboBoxSecurityLevel.setCurrentIndex(2)
        elif security_level["value"] == "medium":
            self.comboBoxSecurityLevel.setCurrentIndex(3)
        elif security_level["value"] == "high":
            self.comboBoxSecurityLevel.setCurrentIndex(4)
        elif security_level["value"] == "under_attack":
            self.comboBoxSecurityLevel.setCurrentIndex(5)
        else:
            self.comboBoxSecurityLevel.setCurrentIndex(0)

        if always_use_https["value"] == "off":
            self.checkBoxAlwaysUseHTTPS.setChecked(False)
        else:
            self.checkBoxAlwaysUseHTTPS.setChecked(True)

        if https_rewrites["value"] == "off":
            self.checkBoxAutomaticHTTPSRewrites.setChecked(False)
        else:
            self.checkBoxAutomaticHTTPSRewrites.setChecked(True)

        if tls13["value"] == "off":
            self.checkBoxTLS13.setChecked(False)
        else:
            self.checkBoxTLS13.setChecked(True)

        if cache_level["value"] == "basic":
            self.comboBoxCacheLevel.setCurrentIndex(0)
        elif cache_level["value"] == "aggressive":
            self.comboBoxCacheLevel.setCurrentIndex(1)
        elif cache_level["value"] == "simplified":
            self.comboBoxCacheLevel.setCurrentIndex(2)
        else:
            self.comboBoxCacheLevel.setCurrentIndex(0)

        if browser_cache_ttl["value"] == 300:
            self.comboBoxTTL.setCurrentIndex(0)
        elif browser_cache_ttl["value"] == 900:
            self.comboBoxTTL.setCurrentIndex(1)
        elif browser_cache_ttl["value"] == 1800:
            self.comboBoxTTL.setCurrentIndex(2)
        elif browser_cache_ttl["value"] == 2700:
            self.comboBoxTTL.setCurrentIndex(3)
        elif browser_cache_ttl["value"] == 3600:
            self.comboBoxTTL.setCurrentIndex(4)
        elif browser_cache_ttl["value"] == 7200:
            self.comboBoxTTL.setCurrentIndex(5)
        elif browser_cache_ttl["value"] == 10800:
            self.comboBoxTTL.setCurrentIndex(6)
        elif browser_cache_ttl["value"] == 14400:
            self.comboBoxTTL.setCurrentIndex(7)
        elif browser_cache_ttl["value"] == 28800:
            self.comboBoxTTL.setCurrentIndex(8)
        elif browser_cache_ttl["value"] == 57600:
            self.comboBoxTTL.setCurrentIndex(9)
        elif browser_cache_ttl["value"] == 86400:
            self.comboBoxTTL.setCurrentIndex(10)
        elif browser_cache_ttl["value"] == 604800:
            self.comboBoxTTL.setCurrentIndex(11)
        elif browser_cache_ttl["value"] == 2592000:
            self.comboBoxTTL.setCurrentIndex(12)
        elif browser_cache_ttl["value"] == 31536000:
            self.comboBoxTTL.setCurrentIndex(13)
        else:
            self.comboBoxTTL.setCurrentIndex(0)

        if always_online["value"] == "off":
            self.checkBoxAlwaysOnline.setChecked(False)
        else:
            self.checkBoxAlwaysOnline.setChecked(True)

        if zone["development_mode"] > 0:
            self.checkBoxDevelopmentMode.setChecked(True)
        else:
            self.checkBoxDevelopmentMode.setChecked(False)

        if min_tls_version["value"] == "1.0":
            self.comboBoxMinTLS.setCurrentIndex(0)
        elif min_tls_version["value"] == "1.1":
            self.comboBoxMinTLS.setCurrentIndex(1)
        elif min_tls_version["value"] == "1.2":
            self.comboBoxMinTLS.setCurrentIndex(2)
        elif min_tls_version["value"] == "1.3":
            self.comboBoxMinTLS.setCurrentIndex(3)
        else:
            self.comboBoxMinTLS.setCurrentIndex(0)

        if onion_routing["value"] == "off":
            self.checkBoxOnionRouting.setChecked(False)
        else:
            self.checkBoxOnionRouting.setChecked(True)

        if http3["value"] == "off":
            self.checkBoxHTTP3.setChecked(False)
        else:
            self.checkBoxHTTP3.setChecked(True)

        if websockets["value"] == "off":
            self.checkBoxWebSockets.setChecked(False)
        else:
            self.checkBoxWebSockets.setChecked(True)

        if ip_geolocation["value"] == "on":
            self.checkBoxIPGeolocation.setChecked(True)
        else:
            self.checkBoxIPGeolocation.setChecked(False)

        self.frame.setVisible(False)

    def getSettings_run(self):
        self.getSettingsThread.start()

    def saveSecuritySettings(self):
        if self.checkBoxAlwaysUseHTTPS.isChecked():
            always_use_https = "on"
        else:
            always_use_https = "off"

        if self.checkBoxAutomaticHTTPSRewrites.isChecked():
            https_rewrites = "on"
        else:
            https_rewrites = "off"

        if self.checkBoxTLS13.isChecked():
            tls13 = "on"
        else:
            tls13 = "off"

        security_level = str(self.comboBoxSecurityLevel.currentText()).lower().replace(" ", "_")
        ssl_level = str(self.comboBoxSSL.currentText()).lower().replace(" ", "_")

        self.cf.editAlwaysUseHTTPSsettings(self.tmp_data["zone_id"], always_use_https)
        self.cf.editHSTSsettings(self.tmp_data["zone_id"], self.checkBoxHSTS.isChecked())
        self.cf.editAutomaticHTTPSsettings(self.tmp_data["zone_id"], https_rewrites)
        self.cf.editTLS13settings(self.tmp_data["zone_id"], tls13)
        self.cf.EditSecurityLevelSettings(self.tmp_data["zone_id"], {"value": security_level})
        self.cf.editSSLSettingns(self.tmp_data["zone_id"], ssl_level)
        self.messageBox()

    def saveCacheSettings(self):
        cache_level = str(self.comboBoxCacheLevel.currentText()).lower().replace(" ", "_")
        browser_cache_ttl_list = str(self.comboBoxTTL.currentText()).lower().split(" ")

        browser_cache = int(browser_cache_ttl_list[0])
        browser_cache_time = browser_cache_ttl_list[1]
        if browser_cache_time == "minutes":
            browser_cache_ttl = browser_cache * 60
        elif browser_cache_time == "hours" or browser_cache_time == "hour":
            browser_cache_ttl = browser_cache * 60 * 60
        elif browser_cache_time == "days":
            browser_cache_ttl = browser_cache * 60 * 60 * 24
        elif browser_cache_time == "weeks":
            browser_cache_ttl = browser_cache * 60 * 60 * 24 * 7
        elif browser_cache_time == "month":
            browser_cache_ttl = browser_cache * 60 * 60 * 24 * 30
        elif browser_cache_time == "year":
            browser_cache_ttl = browser_cache * 60 * 60 * 24 * 365
        else:
            browser_cache_ttl = browser_cache * 60

        if self.checkBoxAlwaysOnline.isChecked():
            always_online = "on"
        else:
            always_online = "off"

        if self.checkBoxDevelopmentMode.isChecked():
            development_mode = "on"
        else:
            development_mode = "off"

        self.cf.editCacheLevelSettings(self.tmp_data["zone_id"], cache_level)
        self.cf.editBrowserCacheTTLSettings(self.tmp_data["zone_id"], browser_cache_ttl)
        self.cf.editAlwaysOnlineSettings(self.tmp_data["zone_id"], always_online)
        self.cf.development_mode(self.tmp_data["zone_id"], development_mode)
        self.messageBox()

    def saveNetworkSettings(self):
        min_tls_version = str(self.comboBoxMinTLS.currentText())

        if self.checkBoxOnionRouting.isChecked():
            onion_routing = "on"
        else:
            onion_routing = "off"

        if self.checkBoxHTTP3.isChecked():
            http3 = "on"
        else:
            http3 = "off"

        if self.checkBoxWebSockets.isChecked():
            websockets = "on"
        else:
            websockets = "off"

        if self.checkBoxIPGeolocation.isChecked():
            ip_geolocation = "on"
        else:
            ip_geolocation = "off"

        self.cf.editMinimumTLSsettings(self.tmp_data["zone_id"], min_tls_version)
        self.cf.editOninonRoutingSettings(self.tmp_data["zone_id"], onion_routing)
        self.cf.editHTTP3settings(self.tmp_data["zone_id"], http3)
        self.cf.editWebSocketsSettings(self.tmp_data["zone_id"], websockets)
        self.cf.editIPGeolocationSettings(self.tmp_data["zone_id"], ip_geolocation)
        self.messageBox()

    @staticmethod
    def messageBox():
        Ui().messageBox("Settings saved successfully", "Success", "Information")
