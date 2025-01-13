document.addEventListener('DOMContentLoaded', function () {
    
    const codeReader = new ZXing.BrowserQRCodeReader();
    const videoElement = document.getElementById('video');
    let stream;
    let scanning = false; // Flag para saber si estamos escaneando
    let scanInProgress = false; // Flag para evitar escaneos múltiples seguidos

    // Objeto para almacenar los códigos escaneados y cuántas veces se escanearon
    let scannedCodes = {};

    // Función para empezar a escanear un código QR
    function startScanner() {
        // Si ya estamos escaneando, no hacemos nada
        if (scanInProgress) {
            return;
        }

        scanInProgress = true; // Marcar que el escaneo ha comenzado

        const constraints = {
            video: {
                facingMode: "environment",
                width: { ideal: 720 },
                height: { ideal: 400 }
            }
        };

        // Iniciar la cámara y el escaneo
        navigator.mediaDevices.getUserMedia(constraints)
            .then(function (mediaStream) {
                stream = mediaStream;
                videoElement.srcObject = stream;

                // Iniciar el proceso de escaneo del código QR
                codeReader.decodeOnceFromVideoDevice(null, videoElement)
                    .then(function(result) {
                        // Cuando un código QR es escaneado
                        const scannedText = result.text;

                        // Muestra el resultado del escaneo en el modal
                        const resultContainer = document.getElementById('scan-result');
                        const resultText = document.getElementById('scan-result-text');
                        resultText.textContent = scannedText;
                        resultContainer.style.display = 'block';

                        // Añadir el código escaneado a la lista de códigos
                        if (scannedCodes[scannedText]) {
                            scannedCodes[scannedText]++;
                        } else {
                            scannedCodes[scannedText] = 1;
                        }

                        // Actualizar la lista visual de códigos escaneados
                        updateScannedCodesList();

                        // Detener el escáner después de escanear un código
                        stopScanner();
                    })
                    .catch(function(error) {
                        console.error('Error durante el escaneo:', error);
                        stopScanner();
                    });
            })
            .catch(function (error) {
                console.error("Error al acceder a la cámara: ", error);
                scanInProgress = false; // Asegurarse de que no se quede bloqueado si no hay cámara
            });
    }

    // Actualizar la lista visual de códigos escaneados
    function updateScannedCodesList() {
        const scannedList = document.getElementById('scannedCodesTableBody');
        scannedList.innerHTML = ''; // Limpiar la lista

        // Mostrar los códigos escaneados y cuántas veces se escanearon
        for (let code in scannedCodes) {
            const listItem = document.createElement('tr');
            listItem.innerHTML = `<td>${code}</td><td>${scannedCodes[code]} veces</td>`;
            scannedList.appendChild(listItem);
        }

        // Mostrar la tabla de códigos escaneados
        document.getElementById('scannedCodesTable').style.display = 'block';

        // Actualizar el valor del campo oculto para enviar al servidor
        const formInput = document.getElementById('scanned_data');
        formInput.value = JSON.stringify(scannedCodes); // Guardamos los códigos como una cadena JSON
    }

    // Detener el escaneo y la cámara
    function stopScanner() {
        if (scanning) {
            codeReader.reset();
            scanning = false;
        }
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            stream = null;
        }
        scanInProgress = false; // Marcar que el escaneo ha terminado
        // Rehabilitar el botón de escanear
        document.getElementById('scanButton').disabled = false; 
    }

    // Cerrar el modal y detener el escaneo cuando se cierra el modal
    document.querySelector('.btn-close').addEventListener('click', function () {
        stopScanner();
    });

    // Iniciar el escaneo cuando el botón "Escanear" es presionado
    document.getElementById('scanButton').addEventListener('click', function () {
        if (!scanInProgress) {
            // Deshabilitar el botón de escanear hasta que termine el escaneo
            document.getElementById('scanButton').disabled = true;
            startScanner(); // Solo empieza el escaneo si no está en progreso
        }
    });

    // Cuando se cierra el modal, mostrar la lista en la tabla
    document.getElementById('closeModal').addEventListener('click', function() {
        // Si no se han escaneado códigos, no hacemos nada
        if (Object.keys(scannedCodes).length === 0) {
            alert("No se han escaneado códigos.");
            return;
        }

        // Se muestra la tabla con los códigos escaneados y sus cantidades
        updateScannedCodesList();
    });

    // Enviar los datos al servidor cuando se haga clic en "Subir los datos"
    document.getElementById('submitCodesButton').addEventListener('click', function () {
        document.getElementById('scanForm').submit(); // Enviar el formulario con los datos
    });
});
