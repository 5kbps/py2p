#!/usr/bin/env python
# -*- coding: utf-8 -*-

#[GLOBAL SETTINGS]
postsDir = "posts/"
postsFileDir = "webserver/file/"
attachmentsDir = "attachments/"
deletedPostsDir = "moved/"
outdatedPostsDir = "old/"
webServerDir = "webserver/"
webServerPostsDir = "webserver/posts/"
webServerThreadsDir = "webserver/threads/"
webServerImageThumbDir = "webserver/thumb/"
webServerTemplatestDir = "webserver/templates/"
serversListFile = "meta/servers"
defaultServersListFile = "meta/servers-default"
protectedPostsFile = "meta/protected-posts"
maxPostsCount = 1000 #0 to disable TODO
enablePostDeleting = True #TODO
postDeletingMode = "move" #TODO

maxPostSize = 5242880		# Максимальный размер поста
maxRequestSize = 524288 	# Максимальный размер запроса
acceptFiles = True 				# Принимает посты с файлами
requestPOW = 0 				# POW, требуемый для запроса поста поста
maxRequestPOW = 30 				# Максимальный POW, который клиент будет вычислять для запроса постов

#[POSTING SETTINGS]
newPostDefaultPOW = 1;
newPostDefaultName = "Anonymous"
newPostDefaultSubject = ""
newPostDefaultTags = ["tag","test","py2p"]
newPostDefaultFiles = ["test.gif","test.jpg"]
newPostDefaultLanguages = "en,ru"

#[CLIENT SETTINGS]
clientRequestsInterval = 1			# Интервал между запросами к разным серверам
clientMaxIterationCount = 100 			# Максимальное количество сеансов обмена постами с сервером в каждом цикле
clientMaxPOWTimeShift = 10 				# срок жизни POW для запроса поста.
										# Если прописанное в запросе время отличается от текущего на большее число секунд, POW считается недействительным
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
webServerAdditionalTags = ["py2p","кириллица","⠝"]
webServerAdditionalLanguages = "ru,en"
webServerPostingMaxFileCount = 2
webServerPostingMaxFileSize = 5242880
loggingEnabled = False #TODO

webServerSupportedImageFormats = ['jpg','gif','png','jpeg']
webServerPostingFileFormats = webServerSupportedImageFormats + ['tar','gz','rar']

defaultAdminName = "##Admin##"
defaultAdminSign = "<span style=\"color:red\">Admin</span>"