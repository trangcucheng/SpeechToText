//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //audio context to help us record
var arrRecordButton = [];
var arrStopButton = [];
var cur_id;
var arrBlob = [];
var fileNames = [];
for (let i=0;i<skipsens_id.length;i++ ) {
    var recordButton = document.getElementById("recordButton_" + i);
    var stopButton = document.getElementById("stopButton_" + i);
    arrRecordButton.push(recordButton);
    arrStopButton.push(stopButton);
}
for (let i=0;i<skipsens_id.length;i++ ) {
    arrRecordButton[i].addEventListener("click", function () {
        startRecording(i);
    }, false);
    arrStopButton[i].addEventListener("click", function () {
        stopRecording(i);
    }, false);
}


function startRecording(stt) {
    console.log("recordButton " + stt + " clicked");
    var constraints = {audio: true, video: false};
    arrRecordButton[stt].disabled = true;
    arrStopButton[stt].disabled = false;
    // pauseButton.disabled = false
    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");
        audioContext = new AudioContext();
        /*  assign to gumStream for later use  */
        gumStream = stream;
        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);
        /*
            Create the Recorder object and configure to record mono sound (1 channel)
            Recording 2 channels  will double the file size
        */
        rec = new Recorder(input, {numChannels: 1});
        //start the recording process
        rec.record();
    }).catch(function (err) {
        //enable the record button if getUserMedia() fails
        arrRecordButton[stt].disabled = false;
        arrStopButton[stt].disabled = true;
        // pauseButton.disabled = true
    });
}


function stopRecording(_id) {
    console.log("stopButton clicked");
    //disable the stop button, enable the record too allow for new recordings
    arrStopButton[_id].disabled = true;
    arrRecordButton[_id].disabled = false;
    // pauseButton.disabled = true;
    //reset button just in case the recording is stopped while paused
    // pauseButton.innerHTML = "Pause";
    //tell the recorder to stop the recording
    rec.stop();
    //stop microphone access
    gumStream.getAudioTracks()[0].stop();
    //create the wav blob and pass it on to createDownloadLink
    cur_id = _id;
    rec.exportWAV(createDownloadLink);
}



function createDownloadLink(blob) {
    console.log("current id : "+skipsens_id[cur_id]);
    var filename = username+"_"+user_id+"_" +skipsens_id[cur_id]+".wav";
    fileNames[cur_id] = filename;
    arrBlob[cur_id] = blob;
    let url = URL.createObjectURL(blob);
    let au = document.createElement('audio');
    // var li = document.createElement('li');
    // var link = document.createElement('a');
    //name of .wav file to use during upload and download (without extendion)
    //add controls to the <audio> element
    au.controls = true;
    au.src = url;
    var theDiv = document.getElementById("colWav_"+cur_id);
    theDiv.innerHTML = '';
    theDiv.append(au);
}

function alert_function(message){

}

function upload() {
    if (Array.isArray(arrBlob) && arrBlob.length && arrBlob.length >0) {
        let xhr = new XMLHttpRequest();
        var fd = new FormData();
        // fd.append("audio_data", arrBlob[0], fileNames[0]);
        for (let j=0;j<skipsens_id.length;j++){
            if (arrBlob[j]!=undefined)
                fd.append("audio_data", arrBlob[j], fileNames[j]);
            // alert(fileNames[j]);
            // console.log(fileNames[j]);
        }
        xhr.open("POST", "/save_audios", true);
        xhr.send(fd);
        alert("tải lên thành công");
        window.location = "/upload_skip";
}
    else{
        alert("Chưa đủ file thu âm!");
        window.location= request.url
    }
}