const stream = await navigator.mediaDevices.getDisplayMedia({
    audio:
    {
        channels: 2,
        autoGainControl: false,
        echoCancellation: false,
        noiseSuppression: false
    }
}
);

window.mediaRecorder = new MediaRecorder(stream);

window.chunks = [];

window.mediaRecorder.ondataavailable = event => {
    if (event.data.size > 0) {
        window.chunks.push(event.data);
    }
};