
	<form method="POST" action="/send" class="postform">
		<table class="postformtable">
			<tr>
				<td>
					<input type="hidden" name="refer" id="refer_id" value="%%replyto%%">
					<span class="replyto">Reply to: <span id="replyto_id">%%replyto%%</span></span>
				</td>
				<td>
					<input class="postformsubmit" type="submit">
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<input type="text" name="name" class="postformname" autocomplete="off" placeholder="Name">
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<input type="text" name="subject" class="postformsubject" autocomplete="off" placeholder="Subject">
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<textarea name="text" class="postformtext" placeholder="Message" autocomplete="off"></textarea>
				</td>
			</tr>
			<tr>
				<td id="filelist" colspan=2>
				<input id="fileselect"  autocomplete="off"  type="file" multiple onchange="handleSelect(event);">
				</td>
			</tr>
			<tr>
				<td colspan=2 class="posttags">
					<input name="tags" autocomplete="off" id="tags" type="hidden">
					<span class="posttaglist">
						<span class="additionaltags" title="These tags are required to post on this server.">%%additionaltags%%</span>
						<span class="usertags" id="usertags">
						</span>
						<input id="taginput" placeholder="Enter new tag" onkeypress="appendTag(event)">
				</td>
			</tr>
			<tr>
				<td colspan=2>
						<span class="boardinfo">◦ bbcode: [b],[s],[i],[u]</li> 
				</td>
			</tr>
		</table>
	</form>
 