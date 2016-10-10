if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from webapp.models.models import *

test_user1 = User(username="dun", nickname="gali", password="123456", email="test1@gmail.com") 
test_user1.add(test_user1)
test_user2 = User(username="ting", nickname="kkk", password="123456", email="test2@gmail.com") 
test_user2.add(test_user2)
test_user3 = User(username="wendi", nickname="helloworld", password="123456", email="test3@gmail.com") 
test_user3.add(test_user3)
test_user4 = User(username="sizhe", nickname="trump", password="123456", email="test4@gmail.com") 
test_user4.add(test_user4)
test_user5 = User(username="yingqiong", nickname="hahaha", password="123456", email="test5@gmail.com") 
test_user5.add(test_user5)

