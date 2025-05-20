function captureScreen(selector) {
  const element = document.querySelector(selector);
  html2canvas(element).then(canvas => {
    const imgData = canvas.toDataURL('image/png');
    fetch('/api/screenshots/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({imageData: imgData})
    })
    .then(response => response.json())
    .then(data => {
      if(data.success) {
        alert('Capture d\'écran sauvegardée!');
      }
    });
  });
}
