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
//				id('filesource_'+num).value=e.target.result
//				alert(e.target.result)
				//num = e.target.id.split('_')[1]
				//alert(num*1+1)
				/*
				if(id('fileentry_'+num)==null){
					fileentry = document.createElement('div');
					fileentry.className = 'fileentry'
					fileentry.id = 'fileentry_'+num
					imageselect = document.createElement('input')
					imageselect.id = 'imageselect_'+num
					imageselect.type = 'file'
					imageselect.name = 'file_'+num
					imagesource = document.createElement('input')
					imagesource.id = 'imagesource_'+num
					imagesource.type = 'hidden'
					imagesource.name = 'source_'+num
					id('filelist').appendChild(fileentry)
					fileentry.appendChild(imageselect)
					fileentry.appendChild(imagesource)
				}*/
			};
		})(f);
		reader.readAsDataURL(f);
	}
}