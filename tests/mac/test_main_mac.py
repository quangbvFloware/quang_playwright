from framework.mac.pages.main_window import MainWindow

def test_main_mac(mac):
    mw = MainWindow(mac)
    mw.click_login()
