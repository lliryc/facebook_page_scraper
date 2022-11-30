#!/usr/bin/env python3

from seleniumwire import webdriver
# to add capabilities for chrome and firefox, import their Options with different aliases
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# import webdriver for downloading respective driver for the browser
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from fake_useragent import UserAgent
import logging
from tbselenium.tbdriver import TorBrowserDriver
import os

logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)


class Initializer:

    def __init__(self, browser_name, proxy=None, headless=True, profile=None, path=None):
        self.browser_name = browser_name
        self.proxy = proxy
        self.headless = headless
        self.profile = profile
        self.path = path

    def set_properties(self, browser_option):
        """adds capabilities to the driver"""
        if self.headless:
            browser_option.add_argument(
                '--headless')  # runs browser in headless mode
        if self.profile and self.browser_name.lower() == "chrome":
            logger.setLevel(logging.INFO)
            logger.info("Loading Profile from {}".format(self.profile))
            browser_option.add_argument(
                "user-data-dir={}".format(self.profile))
        if self.profile and self.browser_name.lower() == "firefox":
            logger.setLevel(logging.INFO)
            logger.info("Loading Profile from {}".format(self.profile))
            browser_option.add_argument("-profile")
            browser_option.add_argument(self.profile)
        browser_option.add_argument('--no-sandbox')
        browser_option.add_argument("--disable-dev-shm-usage")
        browser_option.add_argument('--ignore-certificate-errors')
        browser_option.add_argument('--disable-gpu')
        browser_option.add_argument('--log-level=3')
        browser_option.add_argument('--disable-notifications')
        browser_option.add_argument('--disable-popup-blocking')
        return browser_option

    def set_driver_for_browser(self, browser_name):
        """expects browser name and returns a driver instance"""
        logger.setLevel(logging.INFO)
        # if browser is suppose to be chrome
        if browser_name.lower() == "chrome":
            browser_option = ChromeOptions()
            # automatically installs chromedriver and initialize it and returns the instance
            if self.proxy is not None:
                options = {
                    'https': 'https://{}'.format(self.proxy.replace(" ", "")),
                    'http': 'http://{}'.format(self.proxy.replace(" ", "")),
                    'no_proxy': 'localhost, 127.0.0.1'
                }
                logger.info("Using: {}".format(self.proxy))
                return webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                        options=self.set_properties(browser_option), seleniumwire_options=options)

            return webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.set_properties(browser_option))
        elif browser_name.lower() == "firefox":
            useragent = UserAgent()
            browser_option = FirefoxOptions()
            browser_option.set_preference("general.useragent.override",useragent.firefox)
            if self.proxy is not None:
                options = {
                    'https': 'https://{}'.format(self.proxy.replace(" ", "")),
                    'http': 'http://{}'.format(self.proxy.replace(" ", "")),
                    'no_proxy': 'localhost, 127.0.0.1'
                }
                return webdriver.Firefox(executable_path=GeckoDriverManager(path=self.path).install(),
                                         options=self.set_properties(browser_option)
                                         ,seleniumwire_options=options
                                         )

            # automatically installs geckodriver and initialize it and returns the instance
            return webdriver.Firefox(executable_path=GeckoDriverManager(path=self.path).install(), options=self.set_properties(browser_option))
        elif browser_name.lower() == "tor":
            browser_option = FirefoxOptions()
            tor_browser_path = os.getenv('TOR_BROWSER_PATH')
            if tor_browser_path is None:
                raise Exception("TOR_BROWSER_PATH should be set")
            driver = TorBrowserDriver(tor_browser_path, executable_path=GeckoDriverManager(path=self.path).install(), options=self.set_properties(browser_option))
            return driver
        else:
            # if browser_name is not chrome neither firefox than raise an exception
            raise Exception("Browser not supported!")

    def init(self):
        """returns driver instance"""
        driver = self.set_driver_for_browser(self.browser_name)
        #res = driver.get('https://icanhazip.com/')
        return driver
