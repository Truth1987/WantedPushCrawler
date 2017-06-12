import traceback
import sys
import time
import os.path
sys.path.append('../PTTTelnetCrawlerLibrary')
import PTTTelnetCrawlerLibrary
import PTTTelnetCrawlerLibraryErrorCode
try:
    sys.path.append('../IDPassword')
    import IDPassword

    ID = IDPassword.ID
    Password = IDPassword.Password
    
except ModuleNotFoundError:
    #Define your id password here
    ID = 'Your ID'
    Password = 'Your Password'


print('Hello Crawler')

Board = 'Wanted'
Retry = True

LastNewestPostIndex = 0

while Retry:
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, Password, False)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('Login fail')
    else:
        LastIndex = 0
        LastIndexList = [0]
        
        NoFastPushWait = False
        
        First = True
        
        while True:
            try:
                if not len(LastIndexList) == 0:
                    LastIndex = LastIndexList.pop()
                ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList(Board, LastIndex)
                if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                    PTTCrawler.Log('Get newest list error: ' + str(ErrorCode))
                    time.sleep(1)
                    continue
                if not len(LastIndexList) == 0:
                    PTTCrawler.Log('Detected ' + str(len(LastIndexList)) + ' new post')
                    for NewPostIndex in LastIndexList:
                
                        PTTCrawler.Log('Detected ' + str(NewPostIndex))
                        
                        if First:
                            First = False
                            continue
                        
                        ErrorCode, Time = PTTCrawler.getTime()
                        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                            PTTCrawler.Log('Get ptt time error!')
                            continue
                        Time = Time[:Time.find(':')]
                        
                        if 5 <= int(Time) and int(Time) < 11:
                            PushContent = '早安~'
                        elif 12 <= int(Time) and int(Time) < 18:
                            PushContent = '午安~'
                        else:
                            PushContent = '晚安~'
                        
                        ErrorCode = PTTCrawler.pushByIndex(Board, PTTCrawler.PushType_Push, PushContent, NewPostIndex)
                        
                        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                            PTTCrawler.Log('Push success')
                        else:
                            PTTCrawler.Log('Push fail')
                            time.sleep(1)
            except KeyboardInterrupt:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                PTTCrawler.Log('Interrupted by user')
                PTTCrawler.logout()
                Retry = False
                break
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