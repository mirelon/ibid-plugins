# -*- coding: utf-8 -*-
# encoding: utf-8
import urllib
import re
import HTMLParser
import datetime
from termcolor import colored
import time

class Restaurant:
    @property
    def url(self):
        raise NotImplementedError

    def download(self):
        start_time = time.time()
        html = urllib.urlopen(self.url).read()
        print("--- %s seconds ---" % (time.time() - start_time))
        html_parser = HTMLParser.HTMLParser()
        return html_parser.unescape(self.parse(html))

    def parse(self, html):
        raise NotImplementedError

    def weekday(self):
        return datetime.datetime.today().weekday()

class ZomatoRestaurant(Restaurant):
    pass

class Ferdinand(Restaurant):
    url = "http://www.papanica.sk/sk/denne.php?id=4445&kraj=1"
    def decode(self, string):
        try:
            return string.decode("utf8")
        except:
            return string.decode("windows-1250")

    def parse(self, html):
        obedy = re.findall('<h3 class="text">([0-9].*)</h3></td>', html, re.MULTILINE)
        return [self.decode(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()) for obed in obedy[:4]]

class Flagship(Restaurant):
    url = "http://www.bratislavskarestauracia.sk/sk/denne-menu"

    def parse(self, html):
        week = ['Pondelok / Monday','Utorok / Tuesday','Streda / Wednesday','Štvrtok / Thursday','Piatok / Friday']
        vsetky = re.findall('<h3>'+week[self.weekday()]+'</h3>(.*)<h3>', html, re.MULTILINE|re.DOTALL)
        obedy = re.findall('<div class="col-md-5"><span>(.*)</span></div>', vsetky[0], re.MULTILINE)
        return [(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()).decode("utf8") for obed in obedy[:5] if obed]

class Lanai(Restaurant):
    url = "http://www.lanai-cafe.sk/menu/"

    def parse(self, html):
        week = ['PONDELOK','UTOROK','STREDA','ŠTVRTOK','PIATOK']
        day_date = datetime.datetime.today().strftime("%d.%m.%Y")
        vsetky = re.findall('<p><strong><em>'+week[self.weekday()]+'.*'+day_date+'</em></strong></p>(.*)', html, re.MULTILINE|re.DOTALL)
        obedy = re.findall('<p><strong>.*:</strong>(.*)</p>', vsetky[0], re.MULTILINE)
        return [(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()).decode("utf8") for obed in obedy[:5]]

class Club(ZomatoRestaurant):
    url = "https://www.zomato.com/sk/bratislava/club-restaurant-star%C3%A9-mesto-bratislava-i"

    def parse(self, html):
        obedy = re.findall('<div class="tmi-name">\n.*([0-9]\..*)', html, re.MULTILINE)
        return [(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()).decode("utf8") for obed in obedy]

class Napoli(ZomatoRestaurant):
    url = "https://www.zomato.com/sk/bratislava/bella-napoli-star%C3%A9-mesto-bratislava-i"

    def parse(self, html):
        obedy = re.findall('<div class="tmi-name">\n.*([0-9]\..*)', html, re.MULTILINE)
        return [(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()).decode("utf8") for obed in obedy]

class Obyvacka(ZomatoRestaurant):
    url = "https://www.zomato.com/sk/bratislava/ob%C3%BDva%C4%8Dka-cafe-restaurant-star%C3%A9-mesto-bratislava-i/menu#daily"

    def parse(self, html):
        obedy = re.findall('<div class="tmi-name">\n.*/', html, re.MULTILINE)
        return [(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()).decode("utf8") for obed in obedy[:5] if 'polievku,' not in obed]

class Staromestsky(ZomatoRestaurant):
    url = "https://www.zomato.com/sk/bratislava/staromestsk%C3%BD-pub-restaurant-star%C3%A9-mesto-bratislava-i/menu#daily"

    def parse(self, html):
        obedy = re.findall('<div class="tmi-name">\n.*([0-9]\..*)', html, re.MULTILINE)
        return [(re.sub('<[^<]+?>','',obed).replace("\t",' : ').strip()).decode("utf8") for obed in obedy[:5]]

class Bmp(Restaurant):
    url = "http://dunajska.mestianskypivovar.sk/pivovar-dunajska-ponuka-dna-denne-menu-bratislava-dobry-obed"

    def parse(self, html):
        return [obed.decode("utf8") for obed in re.findall('<td class="foodDescrip">(.*)<\/td>', html)]

all_restaurants = [
    Ferdinand(),
    Bmp(),
    Napoli(),
    Obyvacka(),
    Staromestsky(),
    Club(),
    Lanai(),
    Flagship()
]

class Diet:
    def blacklist(self):
        return []

    def mark(self, meal):
        for black in self.blacklist():
            meal = meal.replace(black.decode('utf8'), colored(black.decode('utf8'), 'red'))
        return meal

class GlutenFree(Diet):
    def blacklist(self):
        return Diet.blacklist(self) + [
            'buchty', 'Palacinky', 'knedľa', 'Lasagne',
            'cestoviny', 'pirohy', 'penne', 'Pene', 'Penne', 'tagliatelle', 'gnocchi', 'tarhoňa', 'tarhoňou', 'kolienka',
            'Pizza', 'pizza', 'chleba', 'chlieb', 'chlebík', 'chlebíkom', 'pečivo', 'toast', 'Burger', 'bagetka', 'strúhanke', 'Vyprážaný', 'Vyprážané', 'vyprážaný', 'Piškót', 
            'cestíčku', 'halušky', 'haluškami',
            'perkelt']

class Paleo(GlutenFree):
    def blacklist(self):
        return GlutenFree.blacklist(self) + [
            'zemiaky', 'zemiakmi', 'zemiačiky', 'zemiaková', 'hranolky', 'hranolkami',
            'ryza', 'ryža', 'ryžovým', 'ryžou', 'ryžový', 'Rizoto',
            'lekvárom', 'džemom', 'Čokoládový', 'čokoládový', 'čoko', 'krupicovými']

class Keto(Paleo):
    def blacklist(self):
        return Paleo.blacklist(self) + [
            'jahodami', 'jahodovým', 'čučoriedkovou', 
            'Šošovicová', 'strukovinový', 'sézamovej', 'Fazuľový', 'Hrachová', 'Hrášková', 'hráškom', 'cícerom', 'Luskova', 'kukuricou', 'Fazuľová', 'fazuľkách',
            'kakaová']

for r in all_restaurants:
    print(colored(r.__class__.__name__, 'yellow'))
    for meal in r.download():
        print(Keto().mark(meal))
