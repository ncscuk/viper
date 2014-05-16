# This file is part of Viper - https://github.com/botherder/viper
# See the file 'LICENSE' for copying permission.

import os
import re
import getopt
from socket import inet_pton, AF_INET6, error as socket_error

from viper.common.out import *
from viper.common.abstracts import Module
from viper.core.session import __sessions__

DOMAIN_REGEX = re.compile('([a-z0-9][a-z0-9\-]{0,61}[a-z0-9]\.)+[a-z0-9][a-z0-9\-]*[a-z0-9]', re.IGNORECASE)
IPV4_REGEX = re.compile('[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]')
IPV6_REGEX = re.compile('((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}'
                        '|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9'
                        'A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25['
                        '0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3'
                        '})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|['
                        '1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,'
                        '4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:'
                        '))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-'
                        '5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]'
                        '{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d'
                        '\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7}'
                        ')|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d'
                        '\d|[1-9]?\d)){3}))|:)))(%.+)?', re.IGNORECASE | re.S)
TLD = ['AC', 'ACADEMY', 'ACTOR', 'AD', 'AE', 'AERO', 'AF', 'AG', 'AGENCY', 'AI', 'AL', 'AM', 'AN', 'AO', 'AQ', 'AR',
    'ARPA', 'AS', 'ASIA', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BAR', 'BARGAINS', 'BB', 'BD', 'BE', 'BERLIN', 'BEST',
    'BF', 'BG', 'BH', 'BI', 'BID', 'BIKE', 'BIZ', 'BJ', 'BLUE', 'BM', 'BN', 'BO', 'BOUTIQUE', 'BR', 'BS', 'BT',
    'BUILD', 'BUILDERS', 'BUZZ', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CAB', 'CAMERA', 'CAMP', 'CARDS', 'CAREERS', 'CAT',
    'CATERING', 'CC', 'CD', 'CENTER', 'CEO', 'CF', 'CG', 'CH', 'CHEAP', 'CHRISTMAS', 'CI', 'CK', 'CL', 'CLEANING',
    'CLOTHING', 'CLUB', 'CM', 'CN', 'CO', 'CODES', 'COFFEE', 'COM', 'COMMUNITY', 'COMPANY', 'COMPUTER', 'CONDOS',
    'CONSTRUCTION', 'CONTRACTORS', 'COOL', 'COOP', 'CR', 'CRUISES', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DANCE',
    'DATING', 'DE', 'DEMOCRAT', 'DIAMONDS', 'DIRECTORY', 'DJ', 'DK', 'DM', 'DNP', 'DO', 'DOMAINS', 'DZ', 'EC',
    'EDU', 'EDUCATION', 'EE', 'EG', 'EMAIL', 'ENTERPRISES', 'EQUIPMENT', 'ER', 'ES', 'ESTATE', 'ET', 'EU', 'EVENTS',
    'EXPERT', 'EXPOSED', 'FARM', 'FI', 'FISH', 'FJ', 'FK', 'FLIGHTS', 'FLORIST', 'FM', 'FO', 'FOUNDATION', 'FR',
    'FUTBOL', 'GA', 'GALLERY', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GIFT', 'GL', 'GLASS', 'GM', 'GN', 'GOV',
    'GP', 'GQ', 'GR', 'GRAPHICS', 'GS', 'GT', 'GU', 'GUITARS', 'GURU', 'GW', 'GY', 'HK', 'HM', 'HN', 'HOLDINGS',
    'HOLIDAY', 'HOUSE', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IMMOBILIEN', 'IN', 'INDUSTRIES', 'INFO', 'INK',
    'INSTITUTE', 'INT', 'INTERNATIONAL', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 'JO', 'JOBS', 'JP', 'KAUFEN',
    'KE', 'KG', 'KH', 'KI', 'KIM', 'KITCHEN', 'KIWI', 'KM', 'KN', 'KOELN', 'KP', 'KR', 'KRED', 'KW', 'KY', 'KZ',
    'LA', 'LAND', 'LB', 'LC', 'LI', 'LIGHTING', 'LIMO', 'LINK', 'LK', 'LR', 'LS', 'LT', 'LU', 'LUXURY', 'LV', 'LY',
    'MA', 'MAISON', 'MANAGEMENT', 'MANGO', 'MARKETING', 'MC', 'MD', 'ME', 'MENU', 'MG', 'MH', 'MIL', 'MK', 'ML',
    'MM', 'MN', 'MO', 'MOBI', 'MODA', 'MONASH', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MUSEUM', 'MV', 'MW', 'MX',
    'MY', 'MZ', 'NA', 'NAGOYA', 'NAME', 'NC', 'NE', 'NET', 'NEUSTAR', 'NF', 'NG', 'NI', 'NINJA', 'NL', 'NO', 'NP',
    'NR', 'NU', 'NZ', 'OKINAWA', 'OM', 'ONION', 'ONL', 'ORG', 'PA', 'PARTNERS', 'PARTS', 'PE', 'PF', 'PG', 'PH',
    'PHOTO', 'PHOTOGRAPHY', 'PHOTOS', 'PICS', 'PINK', 'PK', 'PL', 'PLUMBING', 'PM', 'PN', 'POST', 'PR', 'PRO',
    'PRODUCTIONS', 'PROPERTIES', 'PS', 'PT', 'PUB', 'PW', 'PY', 'QA', 'QPON', 'RE', 'RECIPES', 'RED', 'RENTALS',
    'REPAIR', 'REPORT', 'REVIEWS', 'RICH', 'RO', 'RS', 'RU', 'RUHR', 'RW', 'SA', 'SB', 'SC', 'SD', 'SE', 'SEXY',
    'SG', 'SH', 'SHIKSHA', 'SHOES', 'SI', 'SINGLES', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SOCIAL', 'SOLAR',
    'SOLUTIONS', 'SR', 'ST', 'SU', 'SUPPLIES', 'SUPPLY', 'SUPPORT', 'SV', 'SX', 'SY', 'SYSTEMS', 'SZ', 'TATTOO',
    'TC', 'TD', 'TECHNOLOGY', 'TEL', 'TF', 'TG', 'TH', 'TIENDA', 'TIPS', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO',
    'TODAY', 'TOKYO', 'TOOLS', 'TP', 'TR', 'TRAINING', 'TRAVEL', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UK', 'UNO',
    'US', 'UY', 'UZ', 'VA', 'VACATIONS', 'VC', 'VE', 'VENTURES', 'VG', 'VI', 'VIAJES', 'VILLAS', 'VISION', 'VN',
    'VOTE', 'VOTING', 'VOTO', 'VOYAGE', 'VU', 'WANG', 'WATCH', 'WED', 'WF', 'WIEN', 'WIKI', 'WORKS', 'WS',
    'XN--3BST00M', 'XN--3DS443G', 'XN--3E0B707E', 'XN--45BRJ9C', 'XN--55QW42G', 'XN--55QX5D', 'XN--6FRZ82G',
    'XN--6QQ986B3XL', 'XN--80AO21A', 'XN--80ASEHDB', 'XN--80ASWG', 'XN--90A3AC', 'XN--C1AVG', 'XN--CG4BKI',
    'XN--CLCHC0EA0B2G2A9GCD', 'XN--D1ACJ3B', 'XN--FIQ228C5HS', 'XN--FIQ64B', 'XN--FIQS8S', 'XN--FIQZ9S',
    'XN--FPCRJ9C3D', 'XN--FZC2C9E2C', 'XN--GECRJ9C', 'XN--H2BRJ9C', 'XN--I1B6B1A6A2E', 'XN--IO0A7I', 'XN--J1AMH',
    'XN--J6W193G', 'XN--KPRW13D', 'XN--KPRY57D', 'XN--L1ACC', 'XN--LGBBAT1AD8J', 'XN--MGB9AWBF', 'XN--MGBA3A4F16A',
    'XN--MGBAAM7A8H', 'XN--MGBAB2BD', 'XN--MGBAYH7GPA', 'XN--MGBBH1A71E', 'XN--MGBC0A9AZCG', 'XN--MGBERP4A5D4AR',
    'XN--MGBX4CD0AB', 'XN--NGBC5AZD', 'XN--NQV7F', 'XN--NQV7FS00EMA', 'XN--O3CW4H', 'XN--OGBPF8FL', 'XN--P1AI',
    'XN--PGBS0DH', 'XN--Q9JYB4C', 'XN--RHQV96G', 'XN--S9BRJ9C', 'XN--UNUP4Y', 'XN--WGBH1C', 'XN--WGBL6A',
    'XN--XKC2AL3HYE2A', 'XN--XKC2DL3A5EE0H', 'XN--YFRO4I67O', 'XN--YGBI2AMMX', 'XN--ZFR164B', 'XXX', 'XYZ', 'YE',
    'YT', 'ZA', 'ZM', 'ZONE', 'ZW']

class Strings(Module):
    cmd = 'strings'
    description = 'Extract strings from file'
    authors = ['nex', 'Brian Wallace']

    def extract_hosts(self, strings):
        for entry in strings:
            if DOMAIN_REGEX.search(entry):
                if entry[entry.rfind('.') + 1:].upper() in TLD:
                    print_item(entry)
            elif IPV4_REGEX.search(entry):
                print_item(entry)
            elif IPV6_REGEX.search(entry):
                try:
                    inet_pton(AF_INET6, entry)
                except socket_error:
                    continue
                else:
                    print_item(entry)

    def run(self):
        def usage():
            print("usage: xtreme [-haH]")

        def help():
            usage()
            print("")
            print("Options:")
            print("\t--help (-h)\tShow this help message")
            print("\t--all (-a)\tPrint all strings")
            print("\t--hosts (-H)\tExtract IP addresses and domains from strings")
            print("")

        try:
            opts, argv = getopt.getopt(self.args[0:], 'haH', ['help', 'all', 'hosts'])
        except getopt.GetoptError as e:
            print(e)
            return

        arg_all = False
        arg_hosts = False

        for opt, value in opts:
            if opt in ('-h', '--help'):
                help()
                return
            elif opt in ('-a', '--all'):
                arg_all = True
            elif opt in ('-H', '--hosts'):
                arg_hosts = True

        if not arg_all and not arg_hosts:
            usage()
            return

        if not __sessions__.is_set():
            print_error("No session opened")
            return

        if os.path.exists(__sessions__.current.file.path):
            regexp = '[\x30-\x39\x41-\x5a\x61-\x7a\-\.:]{4,}'
            strings = re.findall(regexp, __sessions__.current.file.data)

        if arg_all:
            for entry in strings:
                print(entry)
        elif arg_hosts:
            self.extract_hosts(strings)
