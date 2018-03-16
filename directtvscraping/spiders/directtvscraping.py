from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request
import scrapy
import re
import json
import csv
import os
import time
import traceback
import requests
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from pyvirtualdisplay import Display
from selenium import webdriver
import socket

CWD = os.path.dirname(os.path.abspath(__file__))
# driver_path = os.path.join(CWD, 'bin', 'chromedriver')
# driver_log_path = os.path.join(CWD, 'bin', 'driver.log')

keys = []

try:
    with open(os.path.abspath('DirecTV_input.csv'), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            keys.append(row[2])

except Exception as e:
    print('parse_csv Function => Got Error: {}'.format(e))

    with open('/home/ubuntu/Stefan-Scrapy-DiscoveryMarkets/DiscoveryMarketsScraping/DirectTV/directtvscraping'
              '/inputdata/DirecTV_input.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            keys.append(row[2])


class SiteProductItem(scrapy.Item):
    container_num = scrapy.Field()


class DirecTV (scrapy.Spider):

    name = "scrapingdata"
    allowed_domains = ['www.att.com']

    start_urls = [
        'https://www.shipmentlink.com/servlet/TDB1_CargoTracking.do']

    def start_requests(self):
        for start_url in self.start_urls:

            if 'www.shipmentlink.com' in start_url:
                for key in keys_EMC:
                    form_data = {'CNTR': key, 'TYPE': 'CNTR', 'blFields': '1', 'cnFields': '1', 'is-quick': 'Y'}
                    yield Request(url=start_url,
                                  headers={
                                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                            'Chrome/64.0.3282.186 Safari/537.36',
                                            'Content-Type': 'application/x-www-form-urlencoded'
                                           },
                                  callback=self.parse_product,
                                  method='POST',
                                  body=urlencode(form_data),
                                  dont_filter=True)

    def parse_product(self, response):

        prod_item = SiteProductItem()

        prod_item['container_num'] = self._parse_ContainerNumber(response)

        if any(value for value in prod_item.values()):
            return prod_item

    @staticmethod
    def _parse_ContainerNumber(response):
        try:
            ContainerNumber = response.xpath('//table[@width="95%"][3]/tr[3]/td[1]//text()').extract()
            if ContainerNumber:
                ContainerNumber = str(ContainerNumber[0])
            if not ContainerNumber and response.xpath('//td[@class="bor_L_none"]/a/font/u//text()'):
                ContainerNumber = str(response.xpath('//td[@class="bor_L_none"]/a/font/u//text()')[0].extract())
            if not ContainerNumber and response.xpath('//span[@class="tracking_container_id"]//text()'):
                ContainerNumber = str(response.xpath('//span[@class="tracking_container_id"]//text()')[0].extract())
            if not ContainerNumber and response.xpath('//tr[@class="field_odd"]//text()').extract():
                ContainerNumber = str(response.xpath('//tr[@class="field_odd"]//text()').extract()[3])
            return ContainerNumber if ContainerNumber else None
        except Exception as e:
            print('No Data')
