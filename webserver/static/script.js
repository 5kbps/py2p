
function hasValue(arr,value) {
	return (arr.indexOf(value) != -1);
}

function id(eid){
	return document.getElementById(eid);
}
function vid(eid){
	r = id(eid).value
	return r
}
function byc(className){
	return document.getElementsByClassName(className)
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
			newtag = document.createElement("a")
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
	id("tags").value = id("tags").value.replace(elem.textContent+"#",'')
	elem.remove()
}

function stringifyPost(){
	string = ""
	posttime = Date.now()
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
	for(var i = 0; i < byc('posttag').length; i++){
		string += byc('posttag')[i].textContent.substr(1)
	}
	//TODO
	string += "ruen"
	return string
}
function calcPOW(value,maxTime){
	timestamp = Date.now()
	post_content = stringifyPost()
	if(value > 50){
		value = 50
	}
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
		if(!pow_shift%1000){
			if(Date.now()-timestamp>maxTime){
				break
			}
		}
	}
	if(pow_shift){
		id("post_pow_shift").value = pow_shift
		console.log("pid="+hex2base36( pid1 )+"("+pid1+")"+":"+pow_shift)
	}
}
function calcPOWandSend(){
	id("fileselect").value=""
	calcPOW(vid('pow_value_select')*1,10)
	id('post_form').submit()
}

function handleSelect(evt){
	supported_image_fromats = ['jpg','png','gif']
	var files = evt.target.files;

	var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice
	var chunkSize = 2097152					   // read in chunks of 2MB
	for (var i = 0, f; f = files[i]; i++) {
		var reader = new FileReader();
		reader.num = i+1
		reader.fname =  files[i].name
		reader.onload = (function(theFile) {
			return function(e) {
				i = this.num
				n = this.fname
				ext = n.split('.')[n.split('.').length-1]
				s = e.target.result
				if(id('fileentry_'+i) == null){
					
					fileentry = document.createElement('div')
					fileentry.id = 'fileentry_'+i
					id('filelist').appendChild(fileentry)

					filesource = document.createElement('input')
					filesource.id = 'filesource_'+i
					filesource.name = 'source_'+i
					filesource.type = 'hidden'
					fileentry.appendChild(filesource)

					filename = document.createElement('input')
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
						filethumb = document.createElement('img')
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
		spark.f_i = i
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
				filehash = document.createElement('input')
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
		var position = getPosition(elem);
		var p = document.createElement('div');
		p.style['top'] = (position.y) -scrollY +25+ 'px';
		p.style['left'] = (position.x) - scrollX +8+'px';
		p.className = 'popup menu';
		elem.appendChild(p);
		elem.onmouseleave = function(){
			removePopupMenu(this)
		}
		for(r in repliesList){
			reply = repliesList[r]
			pe = document.createElement('div')
			pe.innerHTML = cutPostId(reply,15)
			pe.id = "reply_"+reply
			pe.className = "item replyitem"
			pe.onmouseover = function(){
				if(this.getElementsByClassName("postpreview").length==0)
				addPostPreview(this, this.id.split("_")[1])
			}
			pe.onmouseleave = function(){
				removePostPreview(this)
			}
			p.appendChild(pe)
		}
	}
}
function addPostPreview(elem,postid){
	var reqUrl = '/rawpost/'+postid
	xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", reqUrl, true );
	xmlHttp.send( null );
    xmlHttp.onreadystatechange = function(){
		if (this.readyState == 4 && this.status == 200) {
			var position = getPosition(elem);
			postdiv = document.createElement("div")
			postdiv.className = "postpreview"
			postdiv.innerHTML = this.responseText
			postdiv.style['position'] = "absolute"
			postdiv.style['right'] = position.w+3+scrollX+"px"
			postdiv.style['top'] = "0px"
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