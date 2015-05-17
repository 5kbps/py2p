#!/usr/bin/env python
# -*- coding: utf-8 -*-

#[GLOBAL SETTINGS]
logSettings = set([1,2,3,4,5])
'''
1 - human-readable messages
2 - functions called
3 - what functions do
4 - warnings
5 - errors and reasons
'''

#[CRYPTOGRAPHY]
keyLength = 1024 #bits
keyExchangeMessageDetector = '\'' # don't change

#[DIRS]
postsDir = "posts/"
postsFileDir = "webserver/file/"
attachmentsDir = "attachments/"
deletedPostsDir = "moved/"
webServerDir = "webserver/"
webServerPostsDir = "webserver/posts/"
webServerThreadsDir = "webserver/threads/"
webServerImageThumbDir = "webserver/thumb/"
webServerTemplatestDir = "webserver/templates/"
serversListFile = "meta/servers"
defaultServersListFile = "meta/servers-default"
protectedPostsFile = "meta/protected-posts"

#[POSTS]
maxPostsCount = 10 #0 to disable TODO
enablePostDeleting = True #TODO
postDeletingMode = "move" #TODO
maxPostSize = 10485760		# do not change!
maxRequestSize = 67108864	# do not change!
powInfluence = 1000 #The more this value is the more
# extra time to live gets the post with bigger POW
# when webServerPostDeletingMode = "normal" every
# hash calculated when post was created gives additional 
# time (in seconds) equal to this value
# when webServerPostDeletingMode = "progressive" 
# Посты удаляются не по одному, а целыми деревьями
# Ответы на главный пост дерева отдают ему свой POWBonus
# И уничтожаются вместе с ним, когда достигается лимит
# TODO: translate

#[POSTING SETTINGS]
newPostDefaultPOW = 1;
newPostDefaultName = "Anonymous"
newPostDefaultSubject = ""
newPostDefaultTags = ["tag","test","py2p"]
newPostDefaultFiles = ["test.gif","test.jpg"]
newPostDefaultLanguages = "ru,en"

#[CLIENT SETTINGS]
clientRequestsInterval = 20			# Интервал между запросами
clientMaxIterationCount = 10 			# Максимальное количество сеансов обмена постами с сервером в каждом цикле
clientRejectedConnectionsLimit = 3	# Количество отклоненных подряд запросов
clientBehaviorAfterReachingRejectedConnectionsLimit = "remove" 		# 
clientRejectedConnectionsSmartModeLimit = 100
"""
proceed = connect 
smart_mode = Подключаться, если число циклов опроса серверов делится на количество 
пропущенных соединений (оптимальный вариант) TODO TRANSLATE
remove = delete from host list
"""

#[SERVER SETTINGS]
serverPort = 5441
serverMaxPOWTimeShift = 10

#[WEBSERVER SETTINGS]
webServerPort = 5440 # server listent on this port
webServerPostingEnabled = True # Разрешить постить через веб-морду, а не с помощью скрипта
webServerEnableThumbnails = True # Генерировать превью
webServerThumbnailSize = 200,200
webServerThumbnailQuality = 90
webServerPostsOnPage = 50

webServerPostingPOW = 10

webServerTreeViewRecursionLevel = 3 # Глубина рекурсии
webServerTreeViewCutOn = 4 # 


webServerPageListSplitNum = 25
webServerPostFileNameMaxLength = 12
webServerPostLongFileNameSeparator = "[...]."
webServerAdditionalTags = ["py2p","кириллица","⠝"]
webServerAdditionalLanguages = "ru,en"
webServerPostingMaxFileCount = 4
webServerPostingMaxFileSize = 5242880
webServerloggingEnabled = False #TODO
webServerPostDeletingMode = "progressive"
webServerSupportedImageFormats = ['jpg','gif','png','jpeg']
webServerPostingFileFormats = webServerSupportedImageFormats + ['tar','gz','rar']

defaultAdminName = "##Admin##"
defaultAdminSign = "<span style=\"color:red\">Admin</span>"
