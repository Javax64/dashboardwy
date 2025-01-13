document.addEventListener('DOMContentLoaded', function () {

    const codeReader = new ZXing.BrowserQRCodeReader();
    const videoElement = document.getElementById('video');
    let stream;
    let scanning = false; // Flag para saber si estamos escaneando
    let scanInProgress = false; // Flag para evitar escaneos múltiples seguidos
    const scanline = document.getElementById('scanline');
    // Función para empezar a escanear un código QR
    function startScanner() {
        // Si ya estamos escaneando, no hacemos nada
        if (scanInProgress) {
            return;
        }

        scanInProgress = true; // Marcar que el escaneo ha comenzado

        const constraints = {
            video: {
                facingMode: "environment", // Preferir la cámara trasera
                
            }
        };
        scanline.style.display = 'block';
        // Iniciar la cámara y el escaneo
        navigator.mediaDevices.getUserMedia(constraints)
            .then(function (mediaStream) {
                stream = mediaStream;
                videoElement.srcObject = stream;

                // Intentar obtener las capacidades de la cámara para aplicar zoom y enfoque
                const track = mediaStream.getVideoTracks()[0];
                const capabilities = track.getCapabilities();

                // Configurar zoom, si es compatible
                if (capabilities.zoom) {
                    const maxZoom = capabilities.zoom.max;
                    const idealZoom = Math.min(maxZoom, 5); // Ajustar el zoom a un valor adecuado
                    track.applyConstraints({ advanced: [{ zoom: idealZoom }] });
                }

                // Configurar enfoque, si es compatible
                if (capabilities.focusMode) {
                    track.applyConstraints({ advanced: [{ focusMode: 'continuous' }] });
                }

                // Iniciar el proceso de escaneo del código QR
                codeReader.decodeOnceFromVideoDevice(null, videoElement)
                    .then(function(result) {
                        // Cuando un código QR es escaneado
                        const scannedText = result.text;
                        const form = document.querySelector('#form_add_prod');
                        // Mostrar el código escaneado en el campo de entrada
                        const inputElement = document.getElementById('codigo_escaneado');
                        inputElement.value = scannedText;  // Asignar el texto escaneado al input

                        // Detener el escáner después de escanear un código
                        stopScanner();

                        // Cerrar el modal después de escanear el QR
                        const modal = document.querySelector('.bd-example-modal-lg');
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        modalInstance.hide(); // Cerrar el modal

                        // Detener el flujo de video (cerrar la cámara)
                        if (stream) {
                            const tracks = stream.getTracks();
                            tracks.forEach(track => track.stop()); // Detener los tracks de video
                            stream = null; // Limpiar la referencia al stream
                        }
                        form.submit();

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

    // Detener el escaneo y la cámara
    function stopScanner() {
        if (scanning) {
            codeReader.reset();
            scanning = false;
        }
        scanInProgress = false; // Marcar que el escaneo ha terminado
        scanline.style.display = 'none';
    }

    // Cerrar el modal y detener el escaneo cuando se cierra el modal
    document.querySelector('.btn-close').addEventListener('click', function () {
        stopScanner();
    });

    // Cuando el modal se muestra, inicia el escaneo automáticamente
    const modalElement = document.querySelector('.bd-example-modal-lg');
    modalElement.addEventListener('shown.bs.modal', function () {
        startScanner(); // Iniciar el escaneo al abrir el modal
    });

    // Cuando se cierra el modal, detener el escaneo y la cámara
    modalElement.addEventListener('hidden.bs.modal', function () {
        stopScanner();
    });

});