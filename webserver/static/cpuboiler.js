self.addEventListener('message', function(e) {
	var data = e.data;
	importScripts('/static/md5.min.js');                /* imports just "foo.js" */

	switch (data.cmd) {
		case 'start':
			post_content = data.post_content
			timestamp = data.timestamp
			value = data.value
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
						self.postMessage(pow_shift);
						self.close(); // Terminates the worker.
					}
				}
			}
			self.postMessage(pow_shift);
			break;
		case 'stop':
			self.close(); // Terminates the worker.
			break;
	};
}, false);