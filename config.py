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

#[POSTING SETTINGS]
newPostDefaultPOW = 1;
newPostDefaultName = "Anonymous"
newPostDefaultSubject = ""
newPostDefaultTags = "tag,test,py2p"
newPostDefaultFiles = "test.gif,test.jpg"
newPostDefaultLanguages = "en,ru"

#[CLIENT SETTINGS]
# TODO TRANSLATE
clientRequestsInterval = 1 				# Интервал между запросами к разным серверам
clientMaxIterationCount = 10 			# Максимальное количество сеансов обмена постами с сервером в каждом цикле
clientMaxPostSize = 5242880 			# Максимальный размер поста
clientMaxPostsAtOnce = 100 				# Максимальное количество постов, передаваемых за раз
clientRequiredPOW = 0 					# POW, требуемый для запроса поста поста
clientMaxRequestPOW = 3 				# Максимальный POW, который клиент будет вычислять для запроса постов
clientMaxPOWTimeShift = 10 				# срок жизни POW для запроса поста.
										# Если прописанное в запросе время отличается от текущего на большее число, POW считается недействительным
clientRequestLengthLimit = 52428800 	# Максимальный размер запроса
clientAcceptFiles = True 				# Принимает посты с файлами
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
serverMaxPostsAtOnce = 100
serverMaxPostSize = 5242880
serverMaxRequestSize = 52428800 # 50 MB
serverMaxRequestPOW = 3
serverRequiredPOW = 0
serverMaxPOWTimeShift = 10
serverAcceptFiles = True


#[WEBSERVER SETTINGS]
webServerPort = 5440
# server listent on this port
webServerPostingEnabled = True
# Разрешить постить через веб-морду, а не с помощью скрипта
webServerPostRecursionLevel = 10
# Глубина рекурсии
webServerPostReflistHidden = True
# Скрывать ссылки на другие посты
webServerPostingSignatureLength = 1
# Длина подписи, которую генерирует сервер при постинге через веб-морду
# Не стоит изменять

webServerEnableThumbnails = True
# Генерировать превью
webServerThumbnailSize = 200,200
webServerThumbnailQuality = 50

loggingEnabled = True
logFileName = "log.txt"
logMaxSize = 52428800 #50 MB