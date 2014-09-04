# coding=UTF-8
import nose
import mock
from unittest import TestCase
from seplis.indexer.show.tvrage import Tvrage
from seplis import schemas

def mock_tvrage(url):
    if 'last_updates.php' in url:
        return mock.Mock(
            content='''<updates at="1409709081" found="398" sorting="latest_updates" showing="Last 24H">
                    <show>
                    <id>4628</id>
                    <last>-29</last>
                    <lastepisode>817620</lastepisode>
                    </show>
                    <show>
                    <id>2445</id>
                    <last>-28</last>
                    <lastepisode>3314898</lastepisode>
                    </show>
                    </updates>''',
            status_code=200,
        )
    elif 'showinfo.php' in url:
        if '4628' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                    <Showinfo>
                    <showid>4628</showid>
                    <showname>NCIS</showname>
                    <showlink>http://tvrage.com/NCIS</showlink>
                    <seasons>11</seasons>
                    <started>2003</started>
                    <startdate>Sep/23/2003</startdate>
                    <ended></ended>
                    <origin_country>US</origin_country>
                    <status>Returning Series</status>
                    <classification>Scripted</classification>
                    <genres><genre>Action</genre><genre>Crime</genre><genre>Drama</genre><genre>Military/War</genre></genres>
                    <runtime>60</runtime>
                    <network  country="US">CBS</network>
                    <airtime>20:00</airtime>
                    <airday>Tuesday</airday>
                    <timezone>GMT-5 +DST</timezone>
                    <akas><aka country="PL">Agenci NCIS</aka><aka country="RO">Anchetă militară</aka><aka attr="Alternate title" country="IT">N.C.I.S. - Unità anticrimine</aka><aka country="FR">N.C.I.S.: Enquêtes spéciales</aka><aka attr="Working Title" country="US">Naval CIS</aka><aka country="US">Naval Criminal Investigative Service</aka><aka country="ES">Navy - investigación criminal</aka><aka country="DE">Navy CIS</aka><aka country="US">Navy: NCIS</aka><aka attr="Alternate title" country="GR">NCIS</aka><aka country="CZ">NCIS - Námořní vyšetřovací služba</aka><aka country="SK">NCIS - Námorný vyšetrovací úrad</aka><aka country="NL">NCIS - Naval Criminal Investigative Service</aka><aka attr="Alternate title" country="HU">NCIS - Tengerészeti helyszínelők</aka><aka country="FI">NCIS Rikostutkijat</aka><aka attr="Alternate title" country="EE">NCIS: Kriminalistid</aka><aka attr="Original full title" country="US">NCIS: Naval Criminal Investigative Service</aka><aka attr="Alternate title" country="GR">Omada NCIS</aka><aka attr="Alternate title" country="SI">Preiskovalci na delu: NCIS</aka><aka country="LT">Specialioji jūrų policijos tarnyba</aka><aka attr="Alternate title" country="RU">Морская полиция: Спецотдел</aka></akas>
                    </Showinfo>
                    ''',
                status_code=200,
            )
        elif '2445' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Showinfo>
                <showid>2445</showid>
                <showname>24</showname>
                <showlink>http://tvrage.com/24</showlink>
                <seasons>9</seasons>
                <started>2001</started>
                <startdate>Nov/06/2001</startdate>
                <ended></ended>
                <origin_country>US</origin_country>
                <status>Returning Series</status>
                <classification>Scripted</classification>
                <genres><genre>Action</genre><genre>Adventure</genre><genre>Crime</genre><genre>Drama</genre></genres>
                <runtime>60</runtime>
                <network  country="US">FOX</network>
                <airtime>12:00</airtime>
                <timezone>GMT-5 +DST</timezone>
                <akas><aka country="HU">'24'</aka><aka country="CN">24 (美國電視劇)</aka><aka country="DE">24 - Twenty Four</aka><aka attr="Przez 24 godziny" country="PL">24 godziny</aka><aka country="FR">24 heures chrono</aka><aka country="CZ">24 hodin</aka><aka country="BR">24 Horas</aka><aka attr="working title" country="US">24 Hours</aka><aka country="DK">24 timer</aka><aka country="LT">24 valandos</aka><aka country="RU">24 часа</aka><aka attr="Season 9 Subtitle" country="US">24: Live Another Day</aka></akas>
                </Showinfo>
                ''',
                status_code=200,
            )
        elif '5613' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Showinfo>
                <showid>5613</showid>
                <showname>The Best Sex Ever</showname>
                <showlink>http://tvrage.com/shows/id-5613</showlink>
                <seasons>2</seasons>
                <started>2002</started>
                <startdate>May/2002</startdate>
                <ended>Jun/2003</ended>
                <origin_country>US</origin_country>
                <status>Canceled/Ended</status>
                <runtime>30</runtime>
                <network  country="US">CineMax</network>
                <timezone>GMT-5 +DST</timezone>
                </Showinfo>
                ''', 
                status_code=200,
            )
        elif '20370' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Showinfo>
                <showid>20370</showid>
                <showname>The Doctors (2008)</showname>
                <showlink>http://tvrage.com/The_Doctors_2008</showlink>
                <seasons>6</seasons>
                <started>2008</started>
                <startdate>Sep/08/2008</startdate>
                <ended></ended>
                <origin_country>US</origin_country>
                <status>Returning Series</status>
                <classification>Talk Shows</classification>
                <genres><genre>Medical</genre></genres>
                <runtime>60</runtime>
                <network  country="US">Syndicated</network>
                <airtime>16:00</airtime>
                <airday>Weekdays</airday>
                <timezone>GMT-5 +DST</timezone>
                </Showinfo>
                ''',
                status_code=200,
            )
        elif '3140' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Showinfo>
                <showid>3140</showid>
                <showname>Coronation Street</showname>
                <showlink>http://tvrage.com/Coronation_Street</showlink>
                <seasons>54</seasons>
                <started>1960</started>
                <startdate>Dec/09/1960</startdate>
                <ended></ended>
                <origin_country>UK</origin_country>
                <status>Returning Series</status>
                <classification>Scripted</classification>
                <genres><genre>Drama</genre><genre>Family</genre><genre>Soaps</genre></genres>
                <runtime>30</runtime>
                <network  country="UK">ITV</network>
                <airtime>19:30</airtime>
                <airday>Daily</airday>
                <timezone>GMT+0 +DST</timezone>
                <akas><aka country="UK">Coronation St</aka><aka country="UK">Corrie</aka></akas>
                </Showinfo>
                ''',
                status_code=200,
            )
        elif '5294' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Showinfo>
                <showid>5294</showid>
                <showname>Spider-Man (1994)</showname>
                <showlink>http://tvrage.com/Spider-Man_1994</showlink>
                <seasons>5</seasons>
                <started>1994</started>
                <startdate>Nov/1994</startdate>
                <ended>Jan/1998</ended>
                <origin_country>US</origin_country>
                <status>Canceled/Ended</status>
                <classification>Animation</classification>
                <genres><genre>Animation General</genre><genre>Action</genre><genre>Adventure</genre></genres>
                <runtime>30</runtime>
                <akas><aka>Spider-Man (1994)</aka><aka attr="Promotional Title (1998)">Spider-Man's Web Files</aka><aka>Spider-Man: the Animated Series</aka><aka attr="Alternative Spelling">Spiderman</aka></akas>
                </Showinfo>
                ''',
                status_code=200,
            )
        elif '25923' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Showinfo>
                <showid>25923</showid>
                <showname>Double Wedding</showname>
                <showlink>http://tvrage.com/Double_Wedding</showlink>
                <seasons>1</seasons>
                <started>2010</started>
                <startdate>Jun/20/2010</startdate>
                <ended></ended>
                <origin_country>US</origin_country>
                <status>New Series</status>
                <classification>Mini-Series</classification>
                <genres><genre>Comedy</genre><genre>Family</genre><genre>Lifestyle</genre><genre>Romance/Dating</genre></genres>
                <runtime>120</runtime>
                <network  country="US">Lifetime Movie Network</network>
                <airtime>20:00</airtime>
                <airday>Sunday</airday>
                <timezone>GMT-5 +DST</timezone>
                </Showinfo>
                ''',
                status_code=200,
            )
    elif 'episode_list.php' in url:
        if '4628' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>NCIS</name>
                <totalseasons>11</totalseasons>
                <Episodelist>
                <Season no="1">
                <episode><epnum>1</epnum><seasonnum>01</seasonnum><prodnum>101</prodnum><airdate>2003-09-23</airdate><link>http://www.tvrage.com/NCIS/episodes/123486</link><title>Yankee White</title></episode>
                <episode><epnum>2</epnum><seasonnum>02</seasonnum><prodnum>102</prodnum><airdate>2003-09-30</airdate><link>http://www.tvrage.com/NCIS/episodes/123487</link><title>Hung Out to Dry</title></episode>
                </Season>
                <Season no="2">
                <episode><epnum>24</epnum><seasonnum>01</seasonnum><prodnum>201</prodnum><airdate>2004-09-28</airdate><link>http://www.tvrage.com/NCIS/episodes/123509</link><title>See No Evil</title></episode>
                </Season>
                <Season no="3">
                <episode><epnum>47</epnum><seasonnum>01</seasonnum><prodnum>302</prodnum><airdate>2005-09-20</airdate><link>http://www.tvrage.com/NCIS/episodes/123532</link><title>Kill Ari (Part I)</title></episode>
                </Season>
                </Episodelist>
                </Show>
                ''',
                status_code=200,
            )
        elif '2445' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>24</name>
                <totalseasons>9</totalseasons>
                <Episodelist>
                <Season no="1">
                <episode><epnum>1</epnum><seasonnum>01</seasonnum><prodnum>1AFF79</prodnum><airdate>2001-11-06</airdate><link>http://www.tvrage.com/24/episodes/590</link><title>12:00 A.M.-1:00 A.M.</title></episode>
                <episode><epnum>24</epnum><seasonnum>24</seasonnum><prodnum>1AFF23</prodnum><airdate>2002-05-21</airdate><link>http://www.tvrage.com/24/episodes/613</link><title>11:00 P.M.-12:00 A.M.</title></episode>
                </Season>
                <Season no="2">
                <episode><epnum>32</epnum><seasonnum>08</seasonnum><prodnum>2AFF08</prodnum><airdate>2002-12-17</airdate><link>http://www.tvrage.com/24/episodes/621</link><title>Day 2: 3:00 P.M.-4:00 P.M.</title></episode>
                </Season>
                <Season no="9">
                <episode><epnum>193</epnum><seasonnum>01</seasonnum><prodnum></prodnum><airdate>2014-05-00</airdate><link>http://www.tvrage.com/24/episodes/1065323332</link><title>Season 9, Episode 1</title></episode>
                </Season>
                <Special>
                <episode><season>4</season><airdate>0000-00-00</airdate><link>http://www.tvrage.com/24/episodes/526303</link><title>Season 4 Prequel</title></episode>
                <episode><season>5</season><airdate>0000-00-00</airdate><link>http://www.tvrage.com/24/episodes/514123</link><title>Season 5 Prequel</title></episode>
                <episode><season>6</season><airdate>0000-00-00</airdate><link>http://www.tvrage.com/24/episodes/514122</link><title>Season 6 Prequel</title></episode>
                <episode><season>7</season><airdate>2008-11-23</airdate><link>http://www.tvrage.com/24/episodes/660612</link><title>Redemption</title></episode>
                </Special>
                </Episodelist>
                </Show>
                ''',
                status_code=200,
            )
        elif '5613' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>The Best Sex Ever</name>
                <totalseasons>2</totalseasons>
                <Episodelist>
                <Season no="1">
                <episode><epnum>1</epnum><seasonnum>01</seasonnum><prodnum></prodnum><airdate>2002-05-03</airdate><link>http://www.tvrage.com/shows/id-5613/episodes/174478</link><title>Truth or Dare</title></episode>
                <episode><epnum>12</epnum><seasonnum>12</seasonnum><prodnum></prodnum><airdate>2002-07-19</airdate><link>http://www.tvrage.com/shows/id-5613/episodes/174489</link><title>Warrior Princess</title></episode>
                <episode><epnum>13</epnum><seasonnum>13</seasonnum><prodnum></prodnum><airdate>2002-07-26</airdate><link>http://www.tvrage.com/shows/id-5613/episodes/174490</link><title>Housesitting</title></episode>
                </Season>
                <Season no="2">
                <episode><epnum>25</epnum><seasonnum>12</seasonnum><prodnum></prodnum><airdate>2003-06-20</airdate><link>http://www.tvrage.com/shows/id-5613/episodes/174502</link><title>Naughty by Nature</title></episode>
                <episode><epnum>26</epnum><seasonnum>13</seasonnum><prodnum></prodnum><airdate>2003-06-27</airdate><link>http://www.tvrage.com/shows/id-5613/episodes/174503</link><title>Hot Salsa</title></episode>
                </Season>
                </Episodelist>
                </Show>
                ''', 
                status_code=200,
            )
        elif '20370' in url: 
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>The Doctors (2008)</name>
                <totalseasons>6</totalseasons>
                <Episodelist>

                <Season no="1">
                <episode><epnum>1</epnum><seasonnum>01</seasonnum><prodnum></prodnum><airdate>2008-09-08</airdate><link>http://www.tvrage.com/The_Doctors_2008/episodes/1065315472</link><title>Season 1, Episode 1</title></episode>
                <episode><epnum>100</epnum><seasonnum>100</seasonnum><prodnum></prodnum><airdate>2009-02-06</airdate><link>http://www.tvrage.com/The_Doctors_2008/episodes/1065315473</link><title>Season 1, Episode 100</title></episode>
                </Season>

                <Season no="2">
                <episode><epnum>446</epnum><seasonnum>00</seasonnum><prodnum></prodnum><airdate>2010-05-26</airdate><link>http://www.tvrage.com/The_Doctors_2008/episodes/1065315474</link><title>Episode 446</title></episode>
                </Season>

                <Season no="3">
                <episode><epnum>0</epnum><seasonnum>01</seasonnum><prodnum></prodnum><airdate>2010-09-14</airdate><link>http://www.tvrage.com/The_Doctors_2008/episodes/1065315475</link><title>Season 3, Episode 1</title></episode>
                </Season>
                </Episodelist>
                </Show>
                ''',
                status_code=200,
            )
        elif '3140' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>Coronation Street</name>
                <totalseasons>54</totalseasons>
                <Episodelist>
                <Season no="1">
                <episode><epnum>1</epnum><seasonnum>01</seasonnum><prodnum>P228/1</prodnum><airdate>1960-12-09</airdate><link>http://www.tvrage.com/Coronation_Street/episodes/36249</link><title>Friday 9th December 1960</title></episode>
                <episode><epnum>2</epnum><seasonnum>02</seasonnum><prodnum>P228/2</prodnum><airdate>1960-12-14</airdate><link>http://www.tvrage.com/Coronation_Street/episodes/36250</link><title>Wednesday 14th December 1960</title></episode>
                </Season>
                </Episodelist>
                </Show>
                ''',
                status_code=200,
            )
        elif '5294' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>Spider-Man (1994)</name>
                <totalseasons>5</totalseasons>
                <Episodelist>
                <Season no="1">
                <episode><epnum>1</epnum><seasonnum>01</seasonnum><prodnum>101</prodnum><airdate>1994-11-19</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160695</link><title>Night of the Lizard</title></episode>
                <episode><epnum>2</epnum><seasonnum>02</seasonnum><prodnum>103</prodnum><airdate>1995-02-04</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160696</link><title>The Spider Slayer (1)</title></episode>
                </Season>
                <Season no="5">
                <episode><epnum>53</epnum><seasonnum>01</seasonnum><prodnum>404</prodnum><airdate>1997-09-12</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160747</link><title>The Wedding</title></episode>
                <episode><epnum>64</epnum><seasonnum>12</seasonnum><prodnum>415</prodnum><airdate>1998-01-31</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160758</link><title>Spider Wars (1): I Really, Really Hate Clones</title></episode>
                <episode><epnum>65</epnum><seasonnum>13</seasonnum><prodnum>416</prodnum><airdate>1998-01-31</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160759</link><title>Spider Wars (2): Farewell, Spider-Man</title></episode>
                </Season>
                </Episodelist>
                </Show>
                ''',
                status_code=200,
            )
        elif '25923' in url:
            return mock.Mock(
                content='''<?xml version="1.0" encoding="UTF-8" ?>
                <Show>
                <name>Double Wedding</name>
                <totalseasons>1</totalseasons>
                <Episodelist>
                <Season no="5">
                <episode><epnum>53</epnum><seasonnum>01</seasonnum><prodnum>404</prodnum><airdate>1997-09-12</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160747</link><title>The Wedding</title></episode>
                <episode><epnum>64</epnum><seasonnum>12</seasonnum><prodnum>415</prodnum><airdate>1998-01-31</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160758</link><title>Spider Wars (1): I Really, Really Hate Clones</title></episode>
                <episode><epnum>65</epnum><seasonnum>13</seasonnum><prodnum>416</prodnum><airdate>1998-01-31</airdate><link>http://www.tvrage.com/Spider-Man_1994/episodes/160759</link><title>Spider Wars (2): Farewell, Spider-Man</title></episode>
                </Season>
                </Episodelist>
                </Show>
                ''',
                status_code=200,
            )
    return mock.Mock(
        content=None,
        status_code=404,
    )

class test_tvrage(TestCase):
    
    @mock.patch('requests.get', mock_tvrage)
    def test(self):
        tvrage = Tvrage()
        tvrage_ids = [4628, 2445, 5613, 20370, 3140, 5294, 25923]
        for id_ in tvrage_ids:
            show = tvrage.get_show(id_)
            show['episodes'] = tvrage.get_episodes(id_)
            schemas.validate(schemas.Show_schema, show)
            self.assertTrue(show['episodes'])
            
    @mock.patch('requests.get', mock_tvrage)
    def test_updates(self):
        thetvdb = Tvrage()
        ids = thetvdb.get_updates(
            store_latest_timestamp=False,
        )
        self.assertEqual(len(ids), 2)
        self.assertEqual(ids[0], 4628)
        self.assertEqual(ids[1], 2445)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)