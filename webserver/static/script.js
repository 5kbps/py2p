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
function replyTo(elem){
	id('refer_id').value = elem.textContent.trim()
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
	string += vid('refer_id')
	string += vid('post_name')
	string += vid('post_subject')
	string += vid('post_text')
	string += Date.now()
	i = 1
	while(id('filesource_'+i) != null){
		filehash = id('filehash_'+i).value
		filehash = id('filename_'+i).value
		string += filehash
		string += filename
		i++
	}
	for(var i = 0; i < byc('posttag').length; i++){
		string += byc('posttag'])[i].textContent
	}
	string += "ruen"
	return string
}
function calcPOW(value,maxTime){
	
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