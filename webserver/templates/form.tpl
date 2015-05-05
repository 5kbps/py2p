	<form method="POST" action="/send">
		<table>
			<tr>
				<td>
					<input type="text" name="name" autocomplete="off" placeholder="Name">
				</td>
			</tr>
			<tr>
				<td>
					<input type="text" name="subject" autocomplete="off" placeholder="Subject">
				</td>
			</tr>
			<tr>
				<td>
					<textarea name="text" placeholder="Enter your message here" autocomplete="off"></textarea>
				</td>
			</tr>
			<tr>
				<td>
					<input autocomplete="off" id="imageselect" type="file" onchange="handleFileSelect(this)" name="image">
					<input type="hidden" name="imageB64" autocomplete="off" id="imageB64">
				</td>
			</tr>
			<tr>
				<td>
					<span id="refer"></span>
					<input id="hrefer" type="hidden" autocomplete="off" value="" name="refer">
				</td>
			</tr>
		</table>
		<input type="submit">
	</form>
 
