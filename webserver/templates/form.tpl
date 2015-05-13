
	<form method="POST" action="/send" id="post_form" class="postform">
		<table class="postformtable">
			<tr>
				<td>
					<input type="hidden" autocomplete="off" name="refer" id="refer_id" value="%%replyto%%">
					<input type="hidden" autocomplete="off" name="posttime" id="post_time" value="0">
					<input type="hidden" autocomplete="off" name="postpowshift" id="post_pow_shift" value="0">
					<input type="hidden" autocomplete="off" name="postlanguagess" id="post_languages" value="ruen">
					<span class="replyto"><span id="postingmode">%%postingmode%%</span> <span id="replyto_id">%%replyto%%</span></span>
				</td>
				<td>
					browser may freeze -> 
					<select autocomplete="off" id="pow_value_select" title="Be careful! browser may freeze!" onchange="calcPOWandSend();">
						<option disabled>Select POW value.</option>
						<option value="5" class="pow_value_option">5</option>
						<option value="8" class="pow_value_option">8</option>
						<option value="10" class="pow_value_option">10</option>
						<option value="12" class="pow_value_option">12</option>
						<option value="13" class="pow_value_option">13</option>
						<option value="14" class="pow_value_option">14</option>
						<option value="15" class="pow_value_option">15</option>
						<option value="16" class="pow_value_option">16</option>
						<option value="17" class="pow_value_option">17</option>
						<option value="18" class="pow_value_option">18</option>
						<option value="19" class="pow_value_option">19</option>
						<option value="20" class="pow_value_option">20</option>
					</select>
					<!--<input class="postformsubmit" type="submit" value="New post">-->
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<input type="text" name="name" class="postformname" id="post_name" autocomplete="off" placeholder="Name">
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<input type="text" id="post_subject" name="subject" class="postformsubject" autocomplete="off" placeholder="Subject">
				</td>
			</tr>
			<tr>
				<td colspan=2>
					<textarea name="text" id="post_text" class="postformtext" placeholder="Message" autocomplete="off"></textarea>
				</td>
			</tr>
			<tr>
				<td>
					<input id="fileselect"  autocomplete="off"  type="file" multiple onchange="handleSelect(event);">
				</td>
			</tr>
			<tr>
				<td id="filelist">
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
						<div class="boardinfo">bbcode: [b],[s],[i],[u]</div> 
						<div class="boardinfo">Maximum files attached to one post: %%maxfiles%%</div>
				</td>
			</tr>
		</table>
	</form>
 