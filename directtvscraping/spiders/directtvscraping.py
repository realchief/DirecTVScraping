from scrapy import Request
import scrapy
from scrapy.log import WARNING
import json
import csv
import os
import traceback

zip_codes = []
Channels = []
Genere = []
Ott = []
Popular = []
Tags = []
ShortName = []
Alternative_Name = []
Top_Shows = []
Channel_Description = []
Conversion_Names = []

try:
    with open(os.path.abspath('DirecTV_input.csv'), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            zip_codes.append(row[2])

except Exception as e:
    print('parse_csv Function => Got Error: {}'.format(e))

    with open('/home/ubuntu/Stefan-Scrapy-DiscoveryMarkets/DiscoveryMarketsScraping/DirectTV/directtvscraping'
              '/inputdata/DirecTV_input.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            zip_codes.append(row[2])

try:
    with open(os.path.abspath('DirecTV_input.csv'), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            Channels.append(row[0])
            Genere.append(row[1])
            Ott.append(row[2])
            Popular.append(row[3])
            Tags.append(row[4])
            ShortName.append(row[5])
            Alternative_Name.append(row[6])
            Top_Shows.append(row[7])
            Channel_Description.append(row[8])
            Conversion_Names.append(row[9])

except Exception as e:
    print('parse_csv Function => Got Error: {}'.format(e))

    with open('/home/ubuntu/Stefan-Scrapy-DiscoveryMarkets/DiscoveryMarketsScraping/DirectTV'
              '/directtvscraping/inputdata/Channels.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            Channels.append(row[0])
            Genere.append(row[1])
            Ott.append(row[2])
            Popular.append(row[3])
            Tags.append(row[4])
            ShortName.append(row[5])
            Alternative_Name.append(row[6])
            Top_Shows.append(row[7])
            Channel_Description.append(row[8])
            Conversion_Names.append(row[9])


class SiteProductItem(scrapy.Item):
    Channel = scrapy.Field()
    package_name = scrapy.Field()
    zip_code = scrapy.Field()
    Genre = scrapy.Field()
    OTT = scrapy.Field()
    Popular = scrapy.Field()
    Tags = scrapy.Field()
    ShortName = scrapy.Field()
    AlternateNames = scrapy.Field()
    TopShows = scrapy.Field()
    ChannelDescription = scrapy.Field()
    ConversionNames = scrapy.Field()


class ATTProductsSpider (scrapy.Spider):
    name = "att_products"
    allowed_domains = ['att.com']

    start_urls = [
        'https://www.att.com/channellineup/tv/tvchannellineup.html?tvType=directv&cta_button=AddToCart&pricing_terms'
        '=true&lang=en']

    PROD_URL = "https://www.att.com/apis/channellineup/getChannelData?_=1521230061137"

    def start_requests(self):
        for zipCode in zip_codes[1:]:
            yield Request(
                url=self.PROD_URL,
                callback=self.parse_product,
                method="POST",
                body=json.dumps({"county": "SINGLE_COUNTY", "isLatino": "false", "tvType": "dtv", "zipCode": zipCode}),
                dont_filter=True,
                meta={'zip_code': zipCode},
                headers={
                    "content-type": "application/json",
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/64.0.3282.186 Safari/537.36",

                }
            )

    def parse_product(self, response):
        final_channels = []
        product = SiteProductItem()
        zip_code = response.meta['zip_code']
        channel_data = []
        package_data = []
        channel_list = []
        package_list = []
        try:
            data = json.loads(response.body).get('channelLineupDetails')
            channel_data = data.get('channelGroups')
            package_data = data.get('packages')
        except:
            self.log(
                "Failed parsing json at {} - {}".format(response.url, traceback.format_exc())
                , WARNING)

        for channel in channel_data:
            channel_list.append(channel.get('sortName'))
        for package in package_data:
            package_list.append(package.get('packageName'))

        for channel in channel_list:
            for i, c in enumerate(Channels):
                if channel.lower() == c.lower():
                    final_channels.append(c)

        for channel in final_channels:
            for i, c in enumerate(Channels):
                if channel.lower() == c.lower():
                    product['Channel'] = c
                    product['package_name'] = package_list
                    product['zip_code'] = zip_code
                    product['Genre'] = Genere[i]
                    product['OTT'] = Ott[i]
                    product['Popular'] = Popular[i]
                    product['Tags'] = Tags[i]
                    product['ShortName'] = ShortName[i]
                    product['AlternateNames'] = Alternative_Name[i]
                    product['TopShows'] = Top_Shows[i]
                    product['ChannelDescription'] = Channel_Description[i]
                    product['ConversionNames'] = Conversion_Names[i]

                    yield product