



// Obtener el total a cobrar desde el atributo 'data-total' del HTML
const totalCobrar = parseFloat(document.getElementById("total-cobrar").dataset.total) || 0;

// Función para actualizar el saldo
function actualizarSaldo() {
  const descuento = parseFloat(document.getElementById("descuento").value) || 0;
  const adelanto = parseFloat(document.getElementById("adelanto").value) || 0;
  const saldo = totalCobrar - descuento - adelanto;
  document.getElementById("saldo").value = saldo.toFixed(2); // Se actualiza el saldo dinámicamente
}
// Función para guardar los datos del formulario en localStorage
function guardarFormulario() {
  const formData = {};

  // Especificamos los IDs de los campos que queremos monitorear
  const camposMonitoreados = [
    'cliente_nombre', 'cliente_celular', 'descuento', 'adelanto', 'saldo', 
    'fecha_inicio', 'date', 'departamento', 'custom-department', 
    'direccion2', 'direccion', 'sucursal', 'carnet','id_type_payment',
  ];

  camposMonitoreados.forEach(function(id) {
    const element = document.getElementById(id);
    if (element) {
      if (element.type === 'date') {
        // Si el campo es de tipo 'date', lo guardamos tal cual en formato yyyy-mm-dd
        const dateValue = element.value;
        formData[element.id] = dateValue; // Guardamos la fecha en formato adecuado
      } else {
        formData[element.id] = element.value;
      }
    }
  });

  // Guardamos los datos en localStorage
  localStorage.setItem('formData', JSON.stringify(formData));
  console.log('Datos guardados temporalmente en localStorage');
}

// Función para restaurar los datos del formulario desde localStorage (si existen)
function restaurarFormulario() {
  const formData = JSON.parse(localStorage.getItem('formData'));

  if (formData) {
    // Restauramos los valores de cada campo por su ID
    for (const key in formData) {
      const element = document.getElementById(key);
      if (element) {
        if (element.type === 'date') {
          const dateValue = formData[key];
          if (dateValue) {
            // Convertimos la fecha de formato YYYY-MM-DD y la asignamos al input
            element.value = dateValue;
          }
        } else if (element.tagName === 'SELECT') {
          // Para los campos SELECT (como el departamento), seleccionamos la opción correspondiente
          const selectValue = formData[key];
          if (selectValue) {
            element.value = selectValue;
          }
        } else {
          element.value = formData[key] || '';
        }
      }
    }
  }

  // Después de restaurar los valores, actualizamos el saldo
  actualizarSaldo(); // Esto actualiza el saldo con los valores de descuento y adelanto
}

// Función para monitorizar cambios en los campos específicos
function monitorizarCampos() {
  // Escuchamos el evento 'input' para los campos de tipo 'input', 'textarea', 'select' específicos
  const camposMonitoreados = [
    'cliente_nombre', 'cliente_celular', 'descuento', 'adelanto', 'saldo', 
    'fecha_inicio', 'fecha_entrega', 'departamento', 'custom-department', 
    'direccion2', 'direccion', 'sucursal', 'carnet'
  ];

  camposMonitoreados.forEach(function(id) {
    const element = document.getElementById(id);
    if (element) {
      // Escuchamos los eventos 'input' para los campos que lo permiten (ej. texto, número)
      if (element.type !== 'select') {
        element.addEventListener('input', function() {
          guardarFormulario(); // Guardamos los datos cuando cambia un campo
          actualizarSaldo();    // Actualizamos el saldo dinámicamente
        });
      }
      
      // Escuchamos los eventos 'change' para los campos select
      if (element.tagName === 'SELECT') {
        element.addEventListener('change', function() {
          guardarFormulario(); // Guardamos los datos cuando cambia un select
          actualizarSaldo();    // Actualizamos el saldo dinámicamente
        });
      }
      
      // Para los campos de fecha, utilizamos 'change'
      if (element.type === 'date') {
        element.addEventListener('change', function() {
          guardarFormulario(); // Guardamos los datos cuando cambia una fecha
          actualizarSaldo();   // Actualizamos el saldo dinámicamente
        });
      }
    }
  });
}

// Llamar a la función para restaurar los datos cuando la página se haya cargado
window.addEventListener('load', function() {
  restaurarFormulario();
  monitorizarCampos(); // Iniciar la monitorización de los campos del formulario
});

// Función para borrar los datos del localStorage al finalizar el pedido
function borrarDatosLocalStorage() {
  localStorage.clear();
  console.log('Datos eliminados de localStorage');
}

// Seleccionamos el formulario "terminar_pedido"
const formularioTerminarPedido = document.getElementById("terminar_pedido");

// Escuchamos el evento submit del formulario para borrar los datos al enviar el formulario
formularioTerminarPedido.addEventListener('submit', function(event) {
  borrarDatosLocalStorage(); // Borrar los datos al enviar el formulario
});
document.addEventListener('DOMContentLoaded', function() {
  const tipoEntregaSelect = document.getElementById('tipo_entrega');
  
  // Función para manejar la visibilidad de las pestañas según la selección
  function updateTabs(selectedValue) {
      // Ocultar todas las pestañas
      const tabs = document.querySelectorAll('.tab-pane');
      tabs.forEach(tab => {
          tab.classList.remove('show', 'active');
      });

      // Mostrar las pestañas correspondientes según la selección
      if (selectedValue == '0') {  // En tienda
          document.getElementById('primaryhome').classList.add('show', 'active');
      } else if (selectedValue == '1') {  // Envio
          document.getElementById('primaryprofile').classList.add('show', 'active');
      } else if (selectedValue == '2') {  // Delivery
          document.getElementById('primarycontact').classList.add('show', 'active');
      }
  }

  // Evento para cuando se cambia la opción
  tipoEntregaSelect.addEventListener('change', function() {
      updateTabs(this.value);
  });

  // Asegurarse de que la pestaña inicial esté visible según el valor del Select
  updateTabs(tipoEntregaSelect.value);
});


    // Función para obtener la fecha actual en formato "YYYY-MM-DD"
    function obtenerFechaHoy() {
      const fechaHoy = new Date();
      const anio = fechaHoy.getFullYear();
      const mes = String(fechaHoy.getMonth() + 1).padStart(2, '0');  // Mes de 2 dígitos
      const dia = String(fechaHoy.getDate()).padStart(2, '0');  // Día de 2 dígitos
      return `${anio}-${mes}-${dia}`;  // Formato "YYYY-MM-DD"
    }

    // Establecer la fecha de hoy en el campo de entrada
    document.getElementById("fecha_inicio").value = obtenerFechaHoy();
    


     // Función que muestra el input y oculta el select cuando se elige "Otro"
function toggleCustomInput() {
    var selectElement = document.getElementById('departamento');
    var inputElement = document.getElementById('custom-department');
    
    // Si el valor seleccionado es "Otro", mostrar el campo de texto y ocultar el select
    if (selectElement.value === 'other') {
        // Usamos position absolute para mover el select fuera de la vista
        selectElement.style.position = 'absolute';  // Cambiamos la posición del select
        selectElement.style.left = '-9999px';  // Lo movemos fuera de la pantalla (lejos a la izquierda)

        inputElement.style.display = 'block';  // Mostramos el input
        inputElement.focus();  // Establecemos el foco en el input
    } else {
        // Si no es "Otro", restauramos el select
        selectElement.style.position = 'static';  // Restauramos su posición original
        selectElement.style.left = '0';  // Lo volvemos a poner en su posición natural

        inputElement.style.display = 'none';  // Ocultamos el input
    }
    
    // Guardamos el valor de 'custom-department' en localStorage si está visible
    if (inputElement.style.display === 'block') {
        localStorage.setItem('customDepartment', inputElement.value);
    }
}

// Función para restaurar el valor de 'custom-department' desde localStorage
function restaurarCustomDepartment() {
    var selectElement = document.getElementById('departamento');
    var inputElement = document.getElementById('custom-department');
    
    // Restauramos el valor de 'custom-department' desde localStorage si existe
    var savedCustomDepartment = localStorage.getItem('customDepartment');
    if (savedCustomDepartment) {
        inputElement.value = savedCustomDepartment;  // Restaura el valor al input
        selectElement.value = 'other';  // Seleccionamos "Otro" en el select
        toggleCustomInput();  // Mostramos el campo de texto y ocultamos el select
    }
}

// Llamamos a la función de restauración cuando la página se cargue
window.addEventListener('load', restaurarCustomDepartment);

// Aseguramos que al cambiar el valor del campo "Otro" se guarde en localStorage
document.getElementById('custom-department').addEventListener('input', function() {
    if (document.getElementById('departamento').value === 'other') {
        localStorage.setItem('customDepartment', this.value);
    }
});
    
    