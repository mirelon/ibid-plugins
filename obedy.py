# -*- coding: utf-8 -*-
import re
import os.path
import HTMLParser
import datetime
import time
from ibid.plugins import Processor, match
from ibid.utils import cacheable_download
from ibid.config import Option, IntOption

features = {'obedy': {
    'description': u'Pozrie co je na obed.',
    'categories': ('lookup', 'web',),
}}

cachetime = 60*60

class Obedy(Processor):
    usage = u"""obedy : zakladny set obedovych menu
    ferdinand : menu U Ferdinanda
    flagship : menu vo Flagshipe
    lanai : menu v Lanai
    club : menu v Club-e
    napoli : menu v Bella Napoli
    obyvacka : menu v restauracii Obyvacka
    bmp : menu v Bratislavskom Mestianskom Pivovare"""

    restaurants = ['ferdinand','flagship','lanai','club','napoli','obyvacka','bmp']

    feature = ('obedy',)

    obedurl = {}
    obedurl['ferdinand'] = "http://www.papanica.sk/sk/denne.php?id=4445&kraj=1"
    obedurl['flagship'] = "http://www.bratislavskarestauracia.sk/sk/denne-menu"
    obedurl['lanai'] = "http://www.lanai-cafe.sk/menu/"
    obedurl['club'] = "https://www.zomato.com/sk/bratislava/club-restaurant-star%C3%A9-mesto-bratislava-i"
    obedurl['napoli'] = "https://www.zomato.com/sk/bratislava/bella-napoli-star%C3%A9-mesto-bratislava-i"
    obedurl['obyvacka'] = "https://www.zomato.com/sk/bratislava/ob%C3%BDva%C4%8Dka-cafe-restaurant-star%C3%A9-mesto-bratislava-i/menu#daily"
    obedurl['bmp'] = "http://dunajska.mestianskypivovar.sk/pivovar-dunajska-ponuka-dna-denne-menu-bratislava-dobry-obed"

    cachetime = IntOption("cachetime", "Time to cache Obedy", cachetime)
    obedfile = {}
    last_checked = {}
    for restaurant in restaurants:
        obedfile[restaurant] =  None
        last_checked[restaurant] = 0

    def _update_list(self,restaurant):
        if restaurant in self.restaurants:
            if not self.obedfile[restaurant] or time.time() - self.last_checked[restaurant] > self.cachetime:
                self.obedfile[restaurant] = cacheable_download(self.obedurl[restaurant], "obedy/"+restaurant+".html")
                self.last_checked[restaurant] = time.time()
        else:
            self._update_list('ferdinand')
            self._update_list('bmp')
            self._update_list('flagship')

    def obed_bmp(self):
        self._update_list('bmp')
        obedar = "[ Bratislavsky Mestiansky Pivovar ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['bmp']))
        f = file(self.obedfile['bmp'], "rU")
        src = f.read()
        f.close()
        obedy = re.findall('<td class="foodDescrip">(.*)<\/td>', src)
        if obedy:
            for obed in obedy:
                if not obed in obedar: obedar += obed.replace('|',':')+"\n"
        obedar = obedar.decode("utf8")
        return obedar
     
    def obed_flagship(self):
        self._update_list('flagship')
        html_parser = HTMLParser.HTMLParser()
        obedar = "[ Flagship ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['flagship']))
        f = file(self.obedfile['flagship'], "rU")
        src = f.read()
        f.close()
        week = ['Pondelok / Monday','Utorok / Tuesday','Streda / Wednesday','Štvrtok / Thursday','Piatok / Friday']
        day = datetime.datetime.today().weekday()
        try:
            vsetky = re.findall('<h3>'+week[day]+'</h3>(.*)<h3>', src, re.MULTILINE|re.DOTALL)
        except:
            return obedar+"\nZiadne menu na dnes."
        obedy = re.findall('<div class="col-md-5"><span>(.*)</span></div>', vsetky[0], re.MULTILINE)
        if obedy:
            for obed in obedy[:5]:
                if not obed in obedar: obedar += re.sub('<[^<]+?>','',obed).replace("\t",' : ').lstrip(' ')+"\n"
        obedar = obedar.replace("panenka","*PANENKA*")
        obedar = obedar.decode("utf8")
        return html_parser.unescape(obedar)

    def obed_lanai(self):
        self._update_list('lanai')
        html_parser = HTMLParser.HTMLParser()
        obedar = "[ Lanai ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['lanai']))
        f = file(self.obedfile['lanai'], "rU")
        src = f.read()
        f.close()
        week = ['PONDELOK','UTOROK','STREDA','ŠTVRTOK','PIATOK']
        day = datetime.datetime.today().weekday()
        day_date = datetime.datetime.today().strftime("%d.%m.%Y")
        try:
            vsetky = re.findall('<p><strong><em>'+week[day]+'.*'+day_date+'</em></strong></p>(.*)<p>&nbsp;</p>', src, re.MULTILINE|re.DOTALL)
        except:
            return obedar+"\nZiadne menu na dnes."
        obedy = re.findall('<p><strong>.*:</strong>(.*)</p>', vsetky[0], re.MULTILINE)
        if obedy:
            for obed in obedy[:5]:
                if not obed in obedar: obedar += re.sub('<[^<]+?>','',obed).replace("\t",' : ').lstrip(' ')+"\n"
        obedar = obedar.replace("panenka","*PANENKA*")
        obedar = obedar.decode("utf8")
        return html_parser.unescape(obedar)
     
        
    def obed_club(self):
        self._update_list('club')
        html_parser = HTMLParser.HTMLParser()
        obedar = "[ Club ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['club']))
        f = file(self.obedfile['club'], "rU")
        src = f.read()
        f.close()
        obedy = re.findall('<div class="tmi-name">\n.*([0-9]\..*)', src, re.MULTILINE)
        if obedy:
            for obed in obedy:
                if not obed in obedar: obedar += re.sub('<[^<]+?>','',obed).replace("\t",' : ').lstrip(' ')+"\n"
        obedar = obedar.replace("panenka","*PANENKA*")
        obedar = obedar.decode("utf8")
        return html_parser.unescape(obedar)

    def obed_napoli(self):
        self._update_list('napoli')
        html_parser = HTMLParser.HTMLParser()
        obedar = "[ Bella Napoli ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['napoli']))
        f = file(self.obedfile['napoli'], "rU")
        src = f.read()
        f.close()
        obedy = re.findall('<div class="tmi-name">\n.*([0-9]\..*)', src, re.MULTILINE)
        if obedy:
            for obed in obedy:
                if not obed in obedar: obedar += re.sub('<[^<]+?>','',obed).replace("\t",' : ').lstrip(' ')+"\n"
        obedar = obedar.replace("panenka","*PANENKA*")
        obedar = obedar.decode("utf8")
        return html_parser.unescape(obedar)
     
    def obed_obyvacka(self):
        self._update_list('obyvacka')
        html_parser = HTMLParser.HTMLParser()
        obedar = "[ Obyvacka ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['obyvacka']))
        f = file(self.obedfile['obyvacka'], "rU")
        src = f.read()
        f.close()
        obedy = re.findall('<div class="tmi-name">\n.*/', src, re.MULTILINE)
        if obedy:
            for obed in obedy[:5]:
                if 'polievku,' not in obed:
                        if not obed in obedar: obedar += re.sub('<[^<]+?>','',obed).replace("\t",' : ').lstrip().rstrip()+"\n"
        obedar = obedar.replace("panenka","*PANENKA*")
        obedar = obedar.decode("utf8")
        return html_parser.unescape(obedar)
     
    def obed_ferdinand(self):
        self._update_list('ferdinand')
        html_parser = HTMLParser.HTMLParser()
        obedar = "[ U ferdinanda ] (Cached: %s)\n" % time.ctime(os.path.getmtime(self.obedfile['ferdinand']))
        f = file(self.obedfile['ferdinand'], "rU")
        src = f.read()
        f.close()
        obedy = re.findall('<h3 class="text">([0-9].*)</h3></td>', src, re.MULTILINE)
        if obedy:
            for obed in obedy[:4]:
                if not obed in obedar: obedar += re.sub('<[^<]+?>','',obed).replace("\t",' : ').lstrip(' ')+"\n"
        obedar = obedar.replace("panenka","*PANENKA*")
        try:
            obedar = obedar.decode("utf8")
        except:
            obedar = obedar.decode("windows-1250")
        return html_parser.unescape(obedar)
 
    @match(r'^obed$')
    def obed(self, event):
        for line in self.obed_bmp().splitlines():
            event.addresponse(line.strip())
        event.addresponse('-')
        for line in self.obed_flagship().splitlines():
            event.addresponse(line.strip())
        event.addresponse('-')
        for line in self.obed_ferdinand().splitlines():
            event.addresponse(line.strip())

    @match(r'^bmp$')
    def bmp(self, event):
        for line in self.obed_bmp().splitlines():
            event.addresponse(line.strip())

    @match(r'^flagship$')
    def flagship(self, event):
        for line in self.obed_flagship().splitlines():
            event.addresponse(line.strip())

    @match(r'^lanai$')
    def lanai(self, event):
        for line in self.obed_lanai().splitlines():
            event.addresponse(line.strip())

    @match(r'^club$')
    def club(self, event):
        for line in self.obed_club().splitlines():
            event.addresponse(line.strip())

    @match(r'^napoli$')
    def napoli(self, event):
        for line in self.obed_napoli().splitlines():
            event.addresponse(line.strip())

    @match(r'^obyvacka$')
    def obyvacka(self, event):
        for line in self.obed_obyvacka().splitlines():
            event.addresponse(line.strip())

    @match(r'^ferdinand$')
    def ferdinand(self, event):
        for line in self.obed_ferdinand().splitlines():
            event.addresponse(line.rstrip())

