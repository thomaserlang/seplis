# coding=UTF-8
import nose
import mock
import xmltodict
from unittest import TestCase
from seplis.indexer.show.thetvdb import Thetvdb
from seplis import schemas
from seplis.api import constants

def mock_thetvdb_show_info(url):
    if 'Updates.php' in url:
        return mock.Mock(
            content='''<Items>
            <Time>1409485893</Time>
            <Series>72108</Series>
            <Series>123</Series>
            <Episode>74097</Episode>
            </Items>
            ''',
            status_code=200,
        )
    elif 'episodes/' in url:
        return mock.Mock(
            content='''<Data>
            <Episode>
              <id>74097</id>
              <Combined_episodenumber>1</Combined_episodenumber>
              <Combined_season>1</Combined_season>
              <DVD_chapter></DVD_chapter>
              <DVD_discid></DVD_discid>
              <DVD_episodenumber></DVD_episodenumber>
              <DVD_season></DVD_season>
              <Director></Director>
              <EpImgFlag>2</EpImgFlag>
              <EpisodeName>Navy NCIS: The Beginning (1)</EpisodeName>
              <EpisodeNumber>1</EpisodeNumber>
              <FirstAired>2003-04-22</FirstAired>
              <GuestStars></GuestStars>
              <IMDB_ID></IMDB_ID>
              <Language>en</Language>
              <Overview>The pilot that aired a few weeks after the show's premiere, and called &quot;Navy NCIS: The Beginning&quot;. It was originally aired as a JAG episode known as S08E20 &quot;Ice Queen (1)&quot;</Overview>
              <ProductionCode></ProductionCode>
              <Rating>8.0</Rating>
              <RatingCount>8</RatingCount>
              <SeasonNumber>1</SeasonNumber>
              <Writer>|Donald P. Bellisario|Don McGill|</Writer>
              <absolute_number></absolute_number>
              <airsafter_season></airsafter_season>
              <airsbefore_episode>1</airsbefore_episode>
              <airsbefore_season>1</airsbefore_season>
              <filename>episodes/72108/74097.jpg</filename>
              <lastupdated>1376029848</lastupdated>
              <seasonid>19575</seasonid>
              <seriesid>987</seriesid>
              <thumb_added></thumb_added>
              <thumb_height>225</thumb_height>
              <thumb_width>400</thumb_width>
              <tms_export>1</tms_export>
              <tms_review_blurry>0</tms_review_blurry>
              <tms_review_by></tms_review_by>
              <tms_review_dark>0</tms_review_dark>
              <tms_review_date></tms_review_date>
              <tms_review_logo>0</tms_review_logo>
              <tms_review_other>0</tms_review_other>
              <tms_review_unsure>0</tms_review_unsure>
            </Episode>
            </Data>''',
            status_code=200,
        )
    elif '72108' in url or '987' in url:
        return mock.Mock(
            content='''<?xml version="1.0" encoding="UTF-8" ?>
            <Data><Series>
              <id>72108</id>
              <Actors>|Mark Harmon|Michael Weatherly|Cote de Pablo|Lauren Holly|Sean Murray|Sasha Alexander|Pauley Perrette|David McCallum|Brian Dietzen|Rocky Carroll|</Actors>
              <Airs_DayOfWeek>Tuesday</Airs_DayOfWeek>
              <Airs_Time>8:00 PM</Airs_Time>
              <ContentRating>TV-14</ContentRating>
              <FirstAired>2003-09-23</FirstAired>
              <Genre>|Action|Adventure|Drama|</Genre>
              <IMDB_ID>tt0364845</IMDB_ID>
              <Language>en</Language>
              <Network>CBS</Network>
              <NetworkID></NetworkID>
              <Overview>Explore the inner workings of the government agency that investigates all crimes involving Navy and Marine Corps personnel, regardless of rank or position.  Leading this team is NCIS Special Agent Leroy Jethro Gibbs, a skilled investigator and interrogator who is smart, tough and willing to bend the rules to get the job done.</Overview>
              <Rating>9.1</Rating>
              <RatingCount>293</RatingCount>
              <Runtime>60</Runtime>
              <SeriesID>16772</SeriesID>
              <SeriesName>NCIS</SeriesName>
              <Status>Continuing</Status>
              <added></added>
              <addedBy></addedBy>
              <banner>graphical/72108-g12.jpg</banner>
              <fanart>fanart/original/72108-1.jpg</fanart>
              <lastupdated>1379846552</lastupdated>
              <poster>posters/72108-5.jpg</poster>
              <tms_wanted>1</tms_wanted>
              <zap2it_id>EP00681911</zap2it_id>
            </Series>
            <Episode>
              <id>4636146</id>
              <Combined_episodenumber>0</Combined_episodenumber>
              <Combined_season>1</Combined_season>
              <DVD_chapter></DVD_chapter>
              <DVD_discid></DVD_discid>
              <DVD_episodenumber></DVD_episodenumber>
              <DVD_season></DVD_season>
              <Director></Director>
              <EpImgFlag></EpImgFlag>
              <EpisodeName>æøå</EpisodeName>
              <EpisodeNumber>1</EpisodeNumber>
              <FirstAired></FirstAired>
              <GuestStars></GuestStars>
              <IMDB_ID></IMDB_ID>
              <Language>en</Language>
              <Overview></Overview>
              <ProductionCode></ProductionCode>
              <Rating></Rating>
              <RatingCount>0</RatingCount>
              <SeasonNumber>0</SeasonNumber>
              <Writer></Writer>
              <absolute_number></absolute_number>
              <airsafter_season></airsafter_season>
              <airsbefore_episode></airsbefore_episode>
              <airsbefore_season></airsbefore_season>
              <filename></filename>
              <lastupdated>1376789683</lastupdated>
              <seasonid>19575</seasonid>
              <seriesid>72108</seriesid>
              <thumb_added></thumb_added>
              <thumb_height></thumb_height>
              <thumb_width></thumb_width>
              <tms_export>0</tms_export>
              <tms_review_blurry>0</tms_review_blurry>
              <tms_review_by></tms_review_by>
              <tms_review_dark>0</tms_review_dark>
              <tms_review_date></tms_review_date>
              <tms_review_logo>0</tms_review_logo>
              <tms_review_other>0</tms_review_other>
              <tms_review_unsure>0</tms_review_unsure>
            </Episode>
            <Episode>
              <id>74097</id>
              <Combined_episodenumber>1</Combined_episodenumber>
              <Combined_season>1</Combined_season>
              <DVD_chapter></DVD_chapter>
              <DVD_discid></DVD_discid>
              <DVD_episodenumber></DVD_episodenumber>
              <DVD_season></DVD_season>
              <Director></Director>
              <EpImgFlag>2</EpImgFlag>
              <EpisodeName>Navy NCIS: The Beginning (1)</EpisodeName>
              <EpisodeNumber>1</EpisodeNumber>
              <FirstAired>2003-04-22</FirstAired>
              <GuestStars></GuestStars>
              <IMDB_ID></IMDB_ID>
              <Language>en</Language>
              <Overview>The pilot that aired a few weeks after the show's premiere, and called &quot;Navy NCIS: The Beginning&quot;. It was originally aired as a JAG episode known as S08E20 &quot;Ice Queen (1)&quot;</Overview>
              <ProductionCode></ProductionCode>
              <Rating>8.0</Rating>
              <RatingCount>8</RatingCount>
              <SeasonNumber>1</SeasonNumber>
              <Writer>|Donald P. Bellisario|Don McGill|</Writer>
              <absolute_number></absolute_number>
              <airsafter_season></airsafter_season>
              <airsbefore_episode>1</airsbefore_episode>
              <airsbefore_season>1</airsbefore_season>
              <filename>episodes/72108/74097.jpg</filename>
              <lastupdated>1376029848</lastupdated>
              <seasonid>19575</seasonid>
              <seriesid>72108</seriesid>
              <thumb_added></thumb_added>
              <thumb_height>225</thumb_height>
              <thumb_width>400</thumb_width>
              <tms_export>1</tms_export>
              <tms_review_blurry>0</tms_review_blurry>
              <tms_review_by></tms_review_by>
              <tms_review_dark>0</tms_review_dark>
              <tms_review_date></tms_review_date>
              <tms_review_logo>0</tms_review_logo>
              <tms_review_other>0</tms_review_other>
              <tms_review_unsure>0</tms_review_unsure>
            </Episode>
            </Data>
                ''',
            status_code=200,
        )
    elif '123' in url:# test with one episode
        return mock.Mock(
            content='''<?xml version="1.0" encoding="UTF-8" ?>
            <Data><Series>
              <id>72108</id>
              <Actors>|Mark Harmon|Michael Weatherly|Cote de Pablo|Lauren Holly|Sean Murray|Sasha Alexander|Pauley Perrette|David McCallum|Brian Dietzen|Rocky Carroll|</Actors>
              <Airs_DayOfWeek>Tuesday</Airs_DayOfWeek>
              <Airs_Time>8:00 PM</Airs_Time>
              <ContentRating>TV-14</ContentRating>
              <FirstAired>2003-09-23</FirstAired>
              <Genre>|Action|Adventure|Drama|</Genre>
              <IMDB_ID>tt0364845</IMDB_ID>
              <Language>en</Language>
              <Network>CBS</Network>
              <NetworkID></NetworkID>
              <Overview>Explore the inner workings of the government agency that investigates all crimes involving Navy and Marine Corps personnel, regardless of rank or position.  Leading this team is NCIS Special Agent Leroy Jethro Gibbs, a skilled investigator and interrogator who is smart, tough and willing to bend the rules to get the job done.</Overview>
              <Rating>9.1</Rating>
              <RatingCount>293</RatingCount>
              <Runtime>60</Runtime>
              <SeriesID>16772</SeriesID>
              <SeriesName>NCIS</SeriesName>
              <Status>Continuing</Status>
              <added></added>
              <addedBy></addedBy>
              <banner>graphical/72108-g12.jpg</banner>
              <fanart>fanart/original/72108-1.jpg</fanart>
              <lastupdated>1379846552</lastupdated>
              <poster>posters/72108-5.jpg</poster>
              <tms_wanted>1</tms_wanted>
              <zap2it_id>EP00681911</zap2it_id>
            </Series>
            <Episode>
              <id>4636146</id>
              <Combined_episodenumber>0</Combined_episodenumber>
              <Combined_season>0</Combined_season>
              <DVD_chapter></DVD_chapter>
              <DVD_discid></DVD_discid>
              <DVD_episodenumber></DVD_episodenumber>
              <DVD_season></DVD_season>
              <Director></Director>
              <EpImgFlag></EpImgFlag>
              <EpisodeName></EpisodeName>
              <EpisodeNumber>0</EpisodeNumber>
              <FirstAired></FirstAired>
              <GuestStars></GuestStars>
              <IMDB_ID></IMDB_ID>
              <Language>en</Language>
              <Overview></Overview>
              <ProductionCode></ProductionCode>
              <Rating></Rating>
              <RatingCount>0</RatingCount>
              <SeasonNumber>1</SeasonNumber>
              <Writer></Writer>
              <absolute_number></absolute_number>
              <airsafter_season></airsafter_season>
              <airsbefore_episode></airsbefore_episode>
              <airsbefore_season></airsbefore_season>
              <filename></filename>
              <lastupdated>1376789683</lastupdated>
              <seasonid>19575</seasonid>
              <seriesid>72108</seriesid>
              <thumb_added></thumb_added>
              <thumb_height></thumb_height>
              <thumb_width></thumb_width>
              <tms_export>0</tms_export>
              <tms_review_blurry>0</tms_review_blurry>
              <tms_review_by></tms_review_by>
              <tms_review_dark>0</tms_review_dark>
              <tms_review_date></tms_review_date>
              <tms_review_logo>0</tms_review_logo>
              <tms_review_other>0</tms_review_other>
              <tms_review_unsure>0</tms_review_unsure>
            </Episode>
            </Data>
                ''',
            status_code=200,
        )

def mock_thetvdb_images(url, stream=None):
    if 'banners.xml' in url:
        return mock.Mock(
            content='''<?xml version="1.0" encoding="UTF-8" ?>
            <Banners>
               <Banner>
                  <id>14820</id>
                  <BannerPath>text/80348.jpg</BannerPath>
                  <BannerType>series</BannerType>
                  <BannerType2>text</BannerType2>
                  <Language>en</Language>
                  <Season></Season>
               </Banner>
               <Banner>
                  <id>877696</id> 
                  <BannerPath>posters/80348-16.jpg</BannerPath> 
                  <BannerType>poster</BannerType> 
                  <BannerType2>680x1000</BannerType2> 
                  <Language>en</Language> 
                  <Rating>8.8000</Rating> 
                  <RatingCount>5</RatingCount>
               </Banner>
               <Banner>
                  <id>877696</id> 
                  <BannerPath>posters/80348-16.jpg</BannerPath> 
                  <BannerType>poster</BannerType> 
                  <BannerType2>680x1000</BannerType2> 
                  <Language>en</Language> 
                  <Rating></Rating> 
                  <RatingCount></RatingCount>
               </Banner>
            </Banners>
            ''',
            status_code=200,
        )
    elif '80348-16.jpg' in url:
        return mock.Mock(
            raw=b'this is an image!',
            status_code=200,
        )

class test_thetvdb(TestCase):
    
    @mock.patch('requests.get', mock_thetvdb_show_info)
    def test(self):
        thetvdb = Thetvdb('apikey')
        ids = [72108, 123]
        for id_ in ids:
            show = thetvdb.get_show(id_)
            show['episodes'] = thetvdb.get_episodes(id_)
            schemas.validate(schemas.Show_schema, show)
            if id_ == 72108:
                self.assertEqual(show['genres'], [
                    'Action',
                    'Adventure',
                    'Drama',
                ])
                self.assertEqual(show['externals']['imdb'], 'tt0364845')

    @mock.patch('requests.get', mock_thetvdb_show_info)
    def test_updates(self):
        thetvdb = Thetvdb('apikey')
        ids = thetvdb.get_updates()
        self.assertEqual(len(ids), 3)
        self.assertEqual(ids[0], 72108)
        self.assertEqual(ids[1], 123)
        self.assertEqual(ids[2], 987)


    @mock.patch('requests.get', mock_thetvdb_images)
    def test_images(self):
        thetvdb = Thetvdb('apikey')
        images = thetvdb.get_images(123)
        self.assertEqual(len(images), 2)
        self.assertEqual(
            images[0]['source_url'], 
            'http://thetvdb.com/banners/posters/80348-16.jpg'
        )
        self.assertEqual(images[0]['source_title'], 'TheTVDB')
        self.assertEqual(images[0]['external_name'], 'thetvdb')
        self.assertEqual(images[0]['external_id'], '877696')
        self.assertEqual(images[0]['type'], constants.IMAGE_TYPE_POSTER)
        schemas.validate(schemas.Image, images[0])
            

if __name__ == '__main__':
    nose.run(defaultTest=__name__)