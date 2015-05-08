function hasValue(arr,value) {
    return (arr.indexOf(value) != -1);
}

function id(id){
	return document.getElementById(id);
}
function replyTo(elem){
	id('refer_id').value = elem.textContent.trim()
	id('replyto_id').textContent = elem.textContent.trim()
}
function handleSelect(evt){
	supported_image_fromats = ['jpg','png','gif']
	var files = evt.target.files;
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
	}
}
function thumbExpand(elem){
	if(elem.src != elem.parentNode.getElementsByClassName("filelink")[0].href){
		elem.src = elem.parentNode.getElementsByClassName("filelink")[0].href
	}else{
		elem.src = "/thumb/"+ elem.parentNode.getElementsByClassName("filelink")[0].href.split("/")[4].split(".")[0]+".jpg"
	}
}

function appendTag(e) {
    if (e.keyCode == 13 || e.charCode == 35) {
		id("tags").value += "#"+id("taginput").value+"#"
		newtag = document.createElement("a")
		newtag.onclick=function(){
			removeTag(this)
		}
		newtag.className = "usertag tag"
		newtag.textContent = '#'+id("taginput").value
		id("usertags").appendChild(newtag)
		id("taginput").value = ""
        var src = e.srcElement || e.target;
        if (src.tagName.toLowerCase() != "textarea") {
            if (e.preventDefault) {
                e.preventDefault();
                e.cancelBubble = true;
            } else {
                e.returnValue = false;
            }
        }
    }
}
function removeTag(elem){
	id("tags").value = id("tags").value.replace(elem.textContent+"#",'')
	elem.remove()
}