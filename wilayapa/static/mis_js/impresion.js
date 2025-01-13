document.addEventListener('DOMContentLoaded', function() {
    // Verificar la existencia de las imágenes al cargar la página
    fetch('/verificar_imagen_ticket/')  // URL para verificar los archivos específicos
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const images = data.images;
                if (images) {
                    let printQueue = [];  // Para almacenar las imágenes a imprimir

                    // Si la imagen de ticket_temp existe
                    if (images.ticket_temp) {
                        printQueue.push(images.ticket_temp);
                    }

                    // Si la imagen de combined_ticket existe
                    if (images.combined_ticket) {
                        printQueue.push(images.combined_ticket);
                    }

                    // Si hay imágenes para imprimir, procesarlas una por una
                    if (printQueue.length > 0) {
                        // Función para imprimir y eliminar la imagen
                        const printAndDelete = (imageUrl) => {
                            // Abrir la ventana de impresión
                            const printWindow = window.open('', '_blank');
                            printWindow.document.write(`
                                <html>
                                <head>
                                    <title>Impresión de Ticket</title>
                                    <style>
                                        @page { size: 7cm auto; margin: 0; }
                                        body { margin: 0; display: flex; justify-content: center; align-items: flex-start; height: 100vh; padding-top: 0; }
                                        img { width: 7cm; height: auto; display: block; image-rendering: crisp-edges; image-rendering: pixelated; }
                                    </style>
                                </head>
                                <body>
                                    <img src="${imageUrl}" onload="window.print(); window.close();" />
                                </body>
                                </html>
                            `);
                            printWindow.document.close();

                            // Después de la impresión o si se cancela, eliminar la imagen
                            printWindow.onafterprint = function() {
                                // Obtener el token CSRF
                                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                                
                                // Eliminar la imagen después de la impresión
                                fetch('/eliminar_imagenes_ticket/', {
                                    method: 'POST',  // Usamos POST para enviar la solicitud de eliminación
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': csrfToken  // Enviar el token CSRF en los headers
                                    },
                                    body: JSON.stringify({ image: imageUrl }),  // Enviar la imagen a eliminar
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.status === 'success') {
                                        console.log('Imagen eliminada: ' + imageUrl);
                                    } else {
                                        console.error('Error al eliminar la imagen: ' + imageUrl);
                                    }
                                })
                                .catch(error => console.error('Error al eliminar la imagen:', error));
                            };
                        };

                        // Imprimir las imágenes en secuencia
                        const processQueue = () => {
                            if (printQueue.length > 0) {
                                const currentImage = printQueue.shift();  // Obtener la siguiente imagen de la cola
                                printAndDelete(currentImage);  // Imprimir y luego eliminar la imagen

                                // Después de eliminar, procesar la siguiente imagen en la cola
                                setTimeout(processQueue, 2000);  // Retraso de 2 segundos entre impresiones
                            }
                        };

                        // Iniciar el proceso de impresión
                        processQueue();
                    } else {
                        console.error('No hay imágenes disponibles para imprimir.');
                    }
                } else {
                    console.error('No se encontraron imágenes en el servidor.');
                }
            } else {
                console.error('Error al verificar las imágenes:', data.message);
            }
        })
        .catch(error => console.error('Error al verificar las imágenes:', error));
});