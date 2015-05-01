#!/usr/bin/env python
# -*- coding: utf-8 -*-

#[GLOBAL SETTINGS]
postsDir = "posts/"
postsFileDir = "files/"
attachmentsDir = "attachments/"
deletedPostsDir = "moved/"
outdatedPostsDir = "old/"

maxMemUsage = 102400 #in KB TODO
maxPostsCount = 1000 #0 to disable TODO
enablePostDeleting = True #TODO
postDeletingMode = "move" #TODO

maxPostSize = 5242880 			# Максимальный размер поста
maxRequestSize = 52428800 	# Максимальный размер запроса
acceptFiles = True 				# Принимает посты с файлами
requiredPOW = 0 					# POW, требуемый для запроса поста поста
maxRequestPOW = 3 				# Максимальный POW, который клиент будет вычислять для запроса постов
maxToRequestListLength = 100
maxToSendListLength	   = 100

#[POSTING SETTINGS]
newPostDefaultPOW = 1;
newPostDefaultName = "Anonymous"
newPostDefaultSubject = ""
newPostDefaultTags = "tag,test,py2p"
newPostDefaultFiles = "test.gif,test.jpg"
newPostDefaultLanguages = "en,ru"

#[CLIENT SETTINGS]
clientRequestsInterval = 1 				# Интервал между запросами к разным серверам
clientMaxIterationCount = 10 			# Максимальное количество сеансов обмена постами с сервером в каждом цикле
clientMaxPOWTimeShift = 10 				# срок жизни POW для запроса поста.
										# Если прописанное в запросе время отличается от текущего на большее число секунд, POW считается недействительным
clientRejectedConnectionsLimit = 30 	# Количество отклоненных подряд запросов
clientBehaviorAfterReachingRejectedConnectionsLimit = "smart_mode" 		# 
clientRejectedConnectionsSmartModeLimit = 100
"""
proceed = connect 
smart_mode = Подключаться, если число циклов опроса серверов делится на количество 
пропущенных соединений (оптимальный вариант) TODO TRANSLATE
remove = delete from host list
"""

#[SERVER SETTINGS]
serverPort = 5441
serverMaxRequestPOW = 3
serverRequiredPOW = 0
serverMaxPOWTimeShift = 10

#[WEBSERVER SETTINGS]
webServerPort = 5440 # server listent on this port
webServerPostingEnabled = True # Разрешить постить через веб-морду, а не с помощью скрипта
webServerPostRecursionLevel = 10 # Глубина рекурсии
webServerPostReflistHidden = True # Скрывать ссылки на другие посты
webServerPostingSignatureLength = 1 # Длина подписи, которую генерирует сервер при постинге через веб-морду
webServerEnableThumbnails = True # Генерировать превью
webServerThumbnailSize = 200,200
webServerThumbnailQuality = 50

loggingEnabled = False #TODO
logFileName = "log.txt"
logMaxSize = 52428800 #50 MB