var fileSelectCounter = 1
var powWorkersActive = false
var powThreadsCount = 2
var powWorkers = []
var manageBoard = false
var popupEffectScroll = scrollY
var popupEffectResetValue = 0.08
function _(text){
	return text
}
//some sugar

doc = document
bd = doc.body
hd = doc.head

function hasValue(arr,value) {
	return (arr.indexOf(value) != -1);
}

function id(eid){
	return doc.getElementById(eid);
}

function createElement(tagName){
	return doc.createElement(tagName)
}
function addEvent(elem, action,func){
	elem.addEventListener(action,func)
}
function vid(eid){
	r = id(eid).value
	return r
}
function byc(className){
	return doc.getElementsByClassName(className)
}
//math
function hex2base36(hexint){
	return parseInt(hexint, 16).toString(36);
}

function replyTo(elem){
	id('refer_id').value = elem.textContent.trim()
	id('postingmode').textContent = "Reply to:"
	id('replyto_id').textContent = elem.textContent.trim()
}
function removeEmptyItems(list){
	r = []
	for(i in list){
		if(list[i] || list[i] === 0){
			r.push(list[i])
		}
	}
	return r
}
function inList(item,list){
	for(i in list){
		if(list[i]==item){
			return true
		}
	}
	return false
}
function thumbExpand(elem){
	if(elem.src != elem.parentNode.getElementsByClassName("filelink")[0].href){
		elem.src = elem.parentNode.getElementsByClassName("filelink")[0].href
	}else{
		elem.src = "/thumb/"+ elem.parentNode.getElementsByClassName("filelink")[0].href.split("/")[4].split(".")[0]+".jpg"
	}
}

function appendTag(e) {
	cancelBubble = false
	if(e.charCode == 47 || e.charCode == 32){
		cancelBubble = true
	}
	if( e.keyCode == 13 || e.charCode == 35){
		list = removeEmptyItems( id("tags").value.split("#"))
		if(id("taginput").value.trim() !="" && !inList(id("taginput").value.trim(),list) ){
			id("tags").value += "#"+id("taginput").value.trim()+"#"
			newtag = createElement("a")
			newtag.onclick=function(){
				removeTag(this)
			}
			newtag.className = "usertag tag posttag"
			newtag.textContent = '#'+id("taginput").value
			id("usertags").appendChild(newtag)
			id("taginput").value = ""
		}
		cancelBubble = true
	}

	var src = e.srcElement || e.target;
	if (src.tagName.toLowerCase() != "textarea" && cancelBubble == true) {
		if (e.preventDefault) {
			e.preventDefault();
			e.cancelBubble = true;
		} else {
			e.returnValue = false;
		}
	}

}
function removeTag(elem){
	if(powWorkersActive==false){
		id("tags").value = id("tags").value.replace(elem.textContent+"#",'')
		elem.remove()
	}
}

function stringifyPost(timestamp){
	string = ""
	posttime = timestamp
	referid	 = vid('refer_id')
	postname = vid('post_name')
	postsubj = vid('post_subject')
	posttext = vid('post_text')
	id('post_time').value = posttime
	string  = referid+postname+postsubj+posttext+posttime
	i = 1
	while(id('filesource_'+i) != null){
		filehash = id('filehash_'+i).value
		filename = id('filename_'+i).value
		string += filehash
		string += filename
		i++
	}
	for(var j = 0; j < byc('posttag').length; j++){
		string += byc('posttag')[j].textContent.substr(1)
	}
	//TODO
	string += "ruen"
	return string
}
function calcPOW(value,toSubmit){
	timestamp = Date.now()*10
	post_content = stringifyPost(timestamp)
	if(value > 25){
		value = 25
	}
	if (!!window.Worker){
		for(var i = 0; i < powThreadsCount; i++){
			powWorkers[i] = new Worker('/static/cpuboiler.js');
			function startWork(worker){
				powWorkers[i].postMessage({'cmd': 'start', 'timestamp': timestamp,'post_content':post_content,'value':value});
			}
			startWork(powWorkers[i])
			powWorkers[i].addEventListener('message', function(e) {
				id("post_pow_shift").value = e.data*1
				if(toSubmit){
					prepareForm()
					id('post_form').submit()
				}
			}, false);
		}
  	}else{
		pow_shift = 0
		while( true ){
			pow_shift++
			pid1 = md5(post_content+pow_shift)
			pid2 = md5(pow_shift+post_content)
			tid1 = parseInt(pid1, 16).toString(2)
			tid2 = parseInt(pid2, 16).toString(2)
			if(tid1.substr(0,value)==tid2.substr(0,value)){
				break
			}
		}
		if(pow_shift){
			id("post_pow_shift").value = pow_shift
			console.log("pid="+hex2base36( pid1 )+"("+pid1+")"+":"+pow_shift)
		}
		if(toSubmit){
			prepareForm()
			id('post_form').submit()
		}
	}
}

function terminateWorkers(){
	for(i in powWorkers){
		 powWorkers[i].terminate()
	}
}
function calcPOWandSend(){
	if(powWorkersActive==false){
		powWorkersActive = true
		id('popostformsubmit').value="Working..."
		calcPOW(vid('pow_value_select')*1,true)
		disableForm()
	}else{
		powWorkersActive = false
		id('popostformsubmit').value="Send post"
		terminateWorkers()
		enableForm()
	}
}

function prepareForm(){
	enableForm()
	for(var i = 1; i <= boardConfig.webServerPostingMaxFileCount;i++){
		id('fileselect_'+i).value = ''
	}

}
function enableForm(){

	id('pow_value_select').disabled = false
	id('post_name').disabled = false
	id('post_subject').disabled = false
	id('post_text').disabled = false
	for(var i = 1; i <= boardConfig.webServerPostingMaxFileCount;i++){
		id('fileselect_'+i).disabled = false
	}
	id('taginput').disabled = false
}
function disableForm(){
	id('pow_value_select').disabled = true
	id('post_name').disabled = true
	id('post_subject').disabled = true
	id('post_text').disabled = true
	for(var i = 1; i <= boardConfig.webServerPostingMaxFileCount;i++){
	id('fileselect_'+i).disabled = true
	}
	id('taginput').disabled = true

}
function handleSelect(elem,evt){
	supported_image_fromats = ['jpg','png','gif']
	var f = evt.target.files[0];
	//i = elem.id.split("_")[1]*1
	i = fileSelectCounter
	fileSelectCounter++
	var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice
	var chunkSize = 2097152	   // read in chunks of 2MB
	var reader = new FileReader();
	reader.num = i
	reader.fname =  f.name
	reader.onload = (function(theFile) {
		return function(e) {
			i = this.num
			n = this.fname
			ext = n.split('.')[n.split('.').length-1]
			s = e.target.result
			if(id('fileentry_'+i) == null){
				
				fileentry = createElement('div')
				fileentry.id = 'fileentry_'+i
				id('filelist').appendChild(fileentry)

				filesource = createElement('input')
				filesource.id = 'filesource_'+i
				filesource.name = 'source_'+i
				filesource.type = 'hidden'
				fileentry.appendChild(filesource)

				filename = createElement('input')
				filename.id = 'filename_'+i
				filename.name = 'filename_'+i
				filename.type = 'hidden'
				fileentry.appendChild(filename)
			}else{
				fileentry = id( 'fileentry_'+i )
				filesource= id( 'filesource_'+i )
				filename =  id( 'filename_'+i )
			}
			filename.value = n
			filesource.value = s
			if( hasValue(supported_image_fromats, ext) ){
				if(id('filethumb_'+i) == null){
					filethumb = createElement('img')
					filethumb.id= 'filethumb_'+i
					filethumb.title = n
					filethumb.className = 'filethumb'
					fileentry.appendChild(filethumb)
				}else{
					filethumb = id('filethumb'+i)
				}
				filethumb.src= s
			}
		};
	})(f);
	reader.readAsDataURL(f);

	var chunks = Math.ceil(f.size / chunkSize)
	var currentChunk = 0
	var spark = new SparkMD5.ArrayBuffer()
	frOnload = function(e) {
		console.log("read chunk nr", currentChunk + 1, "of", chunks);
		spark.append(e.target.result);				 // append array buffer
		currentChunk++;

		if (currentChunk < chunks) {
			loadNext();
		}
		else {
		   console.log("finished loading");
		   hashval = spark.end()
		   console.info("computed hash", hashval,i); // compute hash
			fileentry = id('fileentry_'+i)
			filehash = createElement('input')
			filehash.name = 'filehash_'+i
			filehash.id = 'filehash_'+i
			filehash.type = 'hidden'
			filehash.value = hashval
			fileentry.appendChild(filehash)
		}
	},
	frOnerror = function () {
		console.warn("oops, something went wrong.");
	};

	function loadNext() {
		var fileReader = new FileReader();
		fileReader.onload = frOnload;
		fileReader.onerror = frOnerror;
		var start = currentChunk * chunkSize,
			end = ((start + chunkSize) >= f.size) ? f.size : start + chunkSize;
		fileReader.readAsArrayBuffer(blobSlice.call(f, start, end));
	};
	loadNext();
}

function getPosition(element) {
	var r = element.getBoundingClientRect();
	position = new Object()
	position.x = r.left + window.pageXOffset
	position.y = r.top + window.pageYOffset
	position.h = window.getComputedStyle(element)['height'].split('px')[0]*1;
	position.w = window.getComputedStyle(element)['width'].split('px')[0]*1;
	return position	
}

function removePopupMenu(elem){
	if(elem.getElementsByClassName('popup').length)
		elem.getElementsByClassName('popup')[0].remove()
}
function cutPostId(postid,cutAt){
	cutAt = cutAt || 10
	return postid.substr(0,cutAt)
}
function showReplies(elem){
	repliesList = removeEmptyItems(elem.getElementsByClassName("post_replies_list")[0].value.split(","))
	if(repliesList.length){
		popupEffectReset()
		var position = getPosition(elem);
		var p = createElement('div');
		p.style['top'] = (position.y) -scrollY +25+ 'px';
		p.style['left'] = (position.x) - scrollX +8+'px';
		p.className = 'popup menu';
		elem.appendChild(p);
		elem.onmouseleave = function(){
			removePopupMenu(this)
		}
		for(r in repliesList){
			reply = repliesList[r]
			pe = createElement('div')
			pe.innerHTML = cutPostId(reply,15)
			pe.id = "reply_"+reply
			pe.className = "item replyitem"
			pe.onmouseover = function(){
				if(this.getElementsByClassName("postpreview").length==0)
				addPostPreview(this,this.id.split("_")[1])
			}
			pe.onmouseleave = function(){
				removePostPreview(this)
			}
			p.appendChild(pe)
		}
	}
}
function addPostPreview(elem,postid,xshift,yshift){
	xshift = xshift?xshift:3
	yshift = yshift?yshift:0
	var reqUrl = '/rawpost/'+postid
	xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", reqUrl, true );
	xmlHttp.send( null );
    xmlHttp.onreadystatechange = function(){
		if (this.readyState == 4 && this.status == 200) {
			popupEffectReset()
			var position = getPosition(elem);
			postdiv = createElement("div")
			postdiv.className = "postpreview"
			postdiv.innerHTML = this.responseText
			postdiv.style['right'] = position.w+xshift+scrollX+"px"
			postdiv.style['top'] = yshift+"px"
			postdiv.onmouseover = function(){
				cancelBubble = true
				return false
			}
			elem.appendChild(postdiv);
		}
	}
}

function removePostPreview(elem){
	if(elem.getElementsByClassName("postpreview").length)
		elem.getElementsByClassName("postpreview")[0].remove()
}

function removePostOptions(elem){
	if(id("delete_"+elem.id.split("_")[1]))
		id("delete_"+elem.id.split("_")[1]).remove()
}
function postMouseOver(elem){
	if(manageBoard && elem.parentNode.className.indexOf("postpreview")==-1){
		var postid = elem.id.split("_")[1]
		var position = getPosition(elem);
		if(!id("delete_"+postid)){
			popupEffectReset()

			var p=createElement("div")
			p.className = "popup menu postoption"
			p.id="delete_"+postid
			p.style['top'] = (position.y) -scrollY +25+ 'px';
			p.style['left'] = (position.x) - scrollX +8+'px';
			p.textContent = _("delete")
			elem.appendChild(p);
			elem.onmouseleave = function(){
				removePostOptions(elem)
			}
			p.onclick = function(){
				addToDeletingList(this)
			}
		}
	}
}
//board manage
function toggleBoardManage(){
	if(!manageBoard){
		manageBoard = true
		id("manageboard").style['display'] = "block"
	}else{
		manageBoard = false
		id("manageboard").style['display'] = "none"
	}
}
function isInDeletingList(postid){
	return (vid("manageboard_todelete").indexOf(postid)!=-1)
}
function addToDeletingList(elem){
	if(manageBoard){
		postid = elem.id.split("_")[1]
		if(!isInDeletingList(postid)){
			id("manageboard_todelete").value+=postid+","
			var p = createElement("div")
			p.className = "todelete_item"
			p.id="todelete_"+postid
			p.textContent = postid
			p.onmouseover = function(){
				if(this.getElementsByClassName("postpreview").length==0)
				addPostPreview(this,postid,10,80)
			}
			p.onmouseleave = function(){
				removePostPreview(this)
			}
			p.onclick = function(){
				removeFromDeletingList(this)
			}

			id("manageboard_todelete_div").appendChild(p)
			id("manageboard_todelete_div").style['display'] = 'block'
		}
	}
}
function removeFromDeletingList(elem){
	if(manageBoard){
		postid = elem.id.split("_")[1]
		if(isInDeletingList(postid)){
			id("manageboard_todelete").value = vid("manageboard_todelete").replace(postid+",","")
		}
		elem.remove()
		if(vid("manageboard_todelete")==""){
			id('manageboard_todelete_div').style['display'] = 'none';
		}
	}
}
function removeAllPopups(){
	r = []
	for(i in document.getElementsByClassName("popup")){
		r.push(document.getElementsByClassName("popup")[i]) 
	}
	for(i in document.getElementsByClassName("postpreview")){
		r.push(document.getElementsByClassName("postpreview")[i]) 
	}
	for(i in r){
		if(typeof r[i].remove == "function")
			r[i].remove()
	}
}
function popupEffectReset(){
	popupEffectScroll = scrollY
	id("popup_effect").innerHTML = ".popup,.postpreview { opacity: 1; }"

}
function popupEffect(){
	k = 10/Math.abs(popupEffectScroll - scrollY)
	if(k < popupEffectResetValue){
		removeAllPopups()
		popupEffectReset()
	}
	id("popup_effect").innerHTML = ".popup,.postpreview { opacity: "+k+"; }"
}
function addGUIEvents(){
	addEvent(window,"scroll",function(){
		//removeAllPopups()
		popupEffect()
	})	
}
window.onload = addGUIEvents