const blob = new Blob(window.chunks, { type: 'audio/wav' });

const url_blob = URL.createObjectURL(blob);

window.chunks = [];

const a = document.createElement('a');
a.href = url_blob;
