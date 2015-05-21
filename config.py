# -*- coding: utf-8 -*-

# py2p config
# It's highly recommended to backup this file before 
# making any changes.
# Changing variables marked with `[DO NOT CHANGE]` 
# can make py2p unsafe or useless.

#[GLOBAL SETTINGS]
logSettings = set([1,2,3,4,5])
# 1 - human-readable messages
# 2 - functions called
# 3 - what functions do
# 4 - warnings
# 5 - errors and reasons
timeShift = 0
#[CRYPTOGRAPHY]
keyLength = 1024 #bits [DO NOT CHANGE]
keyExchangeMessageDetector = '\'' # [DO NOT CHANGE]

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
maxPostsCount = 10 # todo
enablePostDeleting = True #TODO
postDeletingMode = "progressive"
# when postDeletingMode = "progressive" 
#	Посты удаляются не по одному, а целыми деревьями
# 	Ответы на главный пост дерева отдают ему свой POWBonus
# 	И уничтожаются вместе с ним, когда достигается лимит
# 	TODO: translate
# when postDeletingMode = "agressive"
# 	Посты удаляются по одному (дискуссии могу обрываться)
postDeletingAction = "move" #TODO
# move: todo
# remove: todo
maxPostSize = 10485760		# [DO NOT CHANGE]
maxRequestSize = 67108864	# [DO NOT CHANGE]
minPostPOW = 0
powInfluence = 1000 #The more this value is the more
# extra time to live gets the post with bigger POW

#[POSTING SETTINGS]
newPostDefaultPOW = 1;
newPostDefaultName = "Anonymous"
newPostDefaultSubject = ""
newPostDefaultTags = ["tag","test","py2p"]
newPostDefaultFiles = ["test.gif","test.jpg"]
newPostDefaultLanguages = "ru,en"

#[MODERATION]
bannedTags = ['somethingillegal','thatshouldnot','besaved']
bannedWords= ['blacklistedword','onemoreblacklistedword']
bannedFiles= ['somefilehash']
#[CLIENT SETTINGS]
clientRequestsInterval = 2			# Интервал между запросами
clientMaxIterationCount = 10 			# Максимальное количество сеансов обмена постами с сервером в каждом цикле
clientSocketTimeout = 300
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
webServerSupportedImageFormats = ['jpg','gif','png','jpeg']
webServerPostingFileFormats = webServerSupportedImageFormats + ['tar','gz','rar']

defaultAdminName = "##Admin##"
defaultAdminSign = "<span style=\"color:red\">Admin</span>"
