<center>
	<form method="POST" action="/send" class="postform">
		<table>
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
				<td colspan=2>
					<input id="imageselect1" type="file" name="file">
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<span id="refer"></span>
					<input id="hrefer" type="hidden" autocomplete="off" value="" name="refer">
				</td>
			</tr>
		</table>
	</form>
 
</center>