<!DOCTYPE HTML>
<html>
	<head>
		<meta charset="utf-8">
		<title>%%title%%</title>
		<link rel="stylesheet" href="/static/style.css">
		<script src="/static/spark-md5.min.js"></script>
		<script src="/static/md5.min.js"></script>
		<script src="/static/script.js"></script>
		<script src="/static/config.js"></script>
		%%head%%
		<style id="popup_effect"></style>
	</head>
	<body>
		<div class="headercontent">
			<div class="navlist">
				<a class="link navitem" href="/all">All %%all_counter%%</a>
				<a class="link navitem" href="/threads">Threads %%thread_counter%%</a>
				<a class="link navitem" href="/trees">Trees %%tree_counter%%</a>
				<a class="link navitem" href="javascript:toggleBoardManage();">Manage</a>
			</div>
		</div>
		<form method="POST" action="/manage" id="manageboard" class="manageboard admin" style="display:none;">
			<input id="manageboard_login" name="username" placeholder="Username"><br>
			<input id="manageboard_password" name="password" placeholder="Password">
			<div class="manageboard_div">
				<div id="manageboard_todelete_div" style="display:none;">
					Posts to delete:
				</div>
			</div>
			<input type="hidden" id="manageboard_todelete" name="manageboard_todelete" autocomplete="off">
			<input type="submit">
		</form>
		<br>
