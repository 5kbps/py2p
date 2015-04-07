#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Новый пост
newPostDefaultSignatureLength = 5;
newPostDefaultName = "Anonymous"
newPostDefaultSubject = ""
newPostDefaultTags = "tag,test,py2p"
newPostDefaultFiles = "test.gif,test.jpg"
newPostDefaultLanguages = "en,ru"

#[ОБЩИЕ НАСТРОЙКИ]
maxFailedConnections = 10
clientRequestsInterval = 60
clientRequestTimeout = 10
clientMaxIterationCount = 100
# Количество последовательных запросов к серверу, после которых клиент должен отключиться
clientVersion = "0.1.1"
clientIsPublic = False
clientListeningOnHost = ""
clientListeningOnPort = 0
clientRequestLengthLimit = 52428800 # 50 MB
clientAcceptImages = True
clientMaxPostSize = 5242880
clientPublicWebserverHost = ""
clientPublicWebserverPort = 0

clientPrivateKeyLength = 10
clientPublicKeyLength = 10
clientRejectedConnectionsLimit = 30
clientAfterReachingRejectedConnectionsLimit = "smart_mode"
"""
proceed = connect 
smart_mode = Подключаться, если число циклов опроса серверов делится на количество 
пропущенных соединений (оптимальный вариант) TRANSLATE
remove = delete from host list
"""




postsDir = "posts/"
postsFileDir = "posts/files/"
attachmentsDir = "attachments/"

maxMemUsage = 102400 #in KB
shelveFileName = "data.shelve"
enablePostDeleting = True
postDeletingMode = "move"
postDeletingMovePath = "outdated"

#[НАСТРОЙКИ СЕРВЕРА]
serverPort = 5441
serverMaxConnections = 10













#[НАСТРОЙКИ ВЕБСЕРВЕРА]




webServerPort = 5440
# Сервер слушает на этом порту
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

logging = True