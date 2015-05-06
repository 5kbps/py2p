function byID(id){
	return document.getElementById(id)
}
function replyTo(elem){
	byID("refer_id").value = elem.textContent.trim()
	byID("replyto_id").textContent = elem.textContent.trim()
}