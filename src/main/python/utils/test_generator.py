if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from webapp.models.models import *
from geoalchemy2 import WKTElement

test_user1 = User(username="dun", nickname="gali", password="123456", email="test1@gmail.com") 
test_user2 = User(username="ting", nickname="kkk", password="123456", email="test2@gmail.com") 
test_user3 = User(username="wendi", nickname="helloworld", password="123456", email="test3@gmail.com") 
test_user4 = User(username="sizhe", nickname="trump", password="123456", email="test4@gmail.com") 
test_user5 = User(username="yingqiong", nickname="hahaha", password="123456", email="test5@gmail.com") 

#Point(longitude, latitude)
pin1 = Pin(title="I have made this test pin 1", short_title="test pin1", owner=test_user1, geo=WKTElement('Point(-84.415984 33.780569)',srid=4326))
pin2 = Pin(title="I have made this test pin 2", short_title="test pin2", owner=test_user1, geo=WKTElement('Point(-84.413181 33.781836)',srid=4326))
pin3 = Pin(title="I have made this test pin 3", short_title="test pin3", owner=test_user2, geo=WKTElement('Point(-84.411529 33.782750)',srid=4326))
pin4 = Pin(title="I have made this test pin 4", short_title="test pin4", owner=test_user3, geo=WKTElement('Point(-84.407847 33.781701)',srid=4326))
pin5 = Pin(title="I have made this test pin 5", short_title="test pin5", owner=test_user4, geo=WKTElement('Point(-84.410684 33.779872)',srid=4326))
pin6 = Pin(title="I have made this test pin 6", short_title="test pin6", owner=test_user5, geo=WKTElement('Point(-84.410325 33.779400)',srid=4326))

pin1.add(pin1)
pin2.add(pin2)
pin3.add(pin3)
pin4.add(pin4)
pin5.add(pin5)
pin6.add(pin6)
