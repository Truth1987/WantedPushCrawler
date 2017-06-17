import traceback
import sys
import time
import random
import json
import getpass
sys.path.append('..\\PTTCrawlerLibrary')
import PTT

# If you want to automatically login define Account.txt
# {"ID":"YourID", "Password":"YourPW"}
try:
    with open('Account.txt') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
except FileNotFoundError:
    print('Welcome to WantedPushCrawler v 1.0.17.0617')
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')

print('Hello Crawler')

Board = 'Wanted'
Retry = True

LastNewestPostIndex = 0
WantList = []

with open('WantList.txt', encoding = 'utf8') as fp:
    for line in fp:
        if len(line) == 0:
            continue
        WantList.append(line.replace('\n', '').replace('\r', ''))

HelloList = []
with open('HelloList.txt', encoding = 'utf8') as fp:
    for line in fp:
        if len(line) == 0:
            continue
        HelloList.append(line.replace('\n', '').replace('\r', ''))
PublicList = []
with open('PublicList.txt', encoding = 'utf8') as fp:
    for line in fp:
        if len(line) == 0:
            continue
        PublicList.append(line.replace('\n', '').replace('\r', ''))

while Retry:
    PTTCrawler = PTT.Crawler(ID, Password, False)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('Login fail')
    else:
        #PTTCrawler.setLogLevel(PTT.LogLevel_DEBUG)
        LastIndex = 0
        LastIndexList = [0]
        
        NoFastPushWait = False
        First = True
        
        PTTCrawler.Log('Start detect new post in ' + Board)
        while Retry:
            try:
            
                ErrorCode, Time = PTTCrawler.getTime()
                if ErrorCode != PTT.Success:
                    PTTCrawler.Log('Get ptt time error!')
                    continue
                #PTTCrawler.Log('PTT time: ' + Time)
                Time = Time[:Time.find(':')]
                
                if 5 <= int(Time) and int(Time) < 11:
                    TimeHello = '早安~喔~'
                elif 12 <= int(Time) and int(Time) < 18:
                    TimeHello = '午安~呦~'
                else:
                    TimeHello = '晚安~囉~'
                    
                if not len(LastIndexList) == 0:
                    LastIndex = LastIndexList.pop()
                ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList(Board, LastIndex)
                if ErrorCode != PTT.Success:
                    PTTCrawler.Log('Get newest list error: ' + str(ErrorCode))
                    time.sleep(1)
                    continue
                
                if not len(LastIndexList) == 0:
                    PTTCrawler.Log('Detected ' + str(len(LastIndexList)) + ' new post')
                    if First:
                        PTTCrawler.Log('Pass the post already exist')
                        PTTCrawler.Log(str(LastIndexList))
                        First = False
                        continue
                    
                    for NewPostIndex in LastIndexList:
                
                        PTTCrawler.Log('Detected ' + str(NewPostIndex))
                        
                        ErrorCode, Post = PTTCrawler.getPostInfoByIndex(Board, NewPostIndex)
                        if ErrorCode == PTT.PostDeleted:
                            PTTCrawler.Log('Post has been deleted')
                            continue
                        if ErrorCode == PTT.WebFormatError:
                            PTTCrawler.Log('Web structure error')
                            continue
                        if ErrorCode != PTT.Success:
                            PTTCrawler.Log('Get post by index fail')
                            continue
                        if Post == None:
                            PTTCrawler.Log('Post is empty')
                            continue
                        
                        if ID in Post.getPostContent() or ID in Post.getTitle():
                            PTTCrawler.Log('User is not allow push')
                            continue
                        
                        PostUser = Post.getPostAuthor()
                        PostUser = PostUser[PostUser.find('(') + 1:PostUser.find(')')]
                        
                        if '5566' in Post.getPostAuthor():
                            PushContent = '5566 pass'
                        elif '抽菸' in Post.getPostContent():
                            PushContent = '抽菸 pass'
                        elif '問安' in Post.getTitle():
                            PushContent = random.choice(HelloList).replace('{User}', PostUser).replace('{TimeHello}', TimeHello)
                        elif '徵求' in Post.getTitle():
                            PushContent = random.choice(WantList).replace('{User}', PostUser).replace('{TimeHello}', TimeHello)
                        elif '公告' in Post.getTitle():
                            PushContent = random.choice(PublicList).replace('{User}', PostUser).replace('{TimeHello}', TimeHello)
                        else:
                            PushContent = PostUser + ' ' + TimeHello
                        
                        PTTCrawler.Log('Push: ' + PushContent)
                        ErrorCode = PTTCrawler.pushByIndex(Board, PTTCrawler.PushType_Push, PushContent, NewPostIndex)
                        
                        if ErrorCode == PTT.Success:
                            PTTCrawler.Log('Push success')
                        else:
                            PTTCrawler.Log('Push fail')
                            time.sleep(1)
            except KeyboardInterrupt:
                '''
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                '''
                PTTCrawler.Log('Interrupted by user')
                PTTCrawler.logout()
                sys.exit()
            except EOFError:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                Retry = True
                break
            except ConnectionAbortedError:
                Retry = True
                break
            except Exception:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                Retry = True
                break