function toggleMarca() {
    var marcaSelection = document.getElementById("marca-selection");
    var newMarca = document.getElementById("new-marca");
    var toggleButton = document.getElementById("toggle-button");

    // Alternar entre la selección de marca y la entrada de nueva marca
    if (newMarca.style.display === "none") {
        newMarca.style.display = "block"; // Mostrar nueva marca
        marcaSelection.style.display = "none"; // Ocultar selección de marca
        toggleButton.innerText = "Elegir Marca Registrada"; // Cambiar texto del botón
    } else {
        newMarca.style.display = "none"; // Ocultar nueva marca
        marcaSelection.style.display = "block"; // Mostrar selección de marca
        toggleButton.innerText = "Agregar Nueva Marca"; // Cambiar texto del botón
    }
}
function addInput(){
       
    var forms = document.querySelector('#id_form-TOTAL_FORMS');
    var newinput = document.querySelector('#id_form-0-nuevo_extra_name').cloneNode (true);
    var newinput2 = document.querySelector('#id_form-0-nuevo_extra_price').cloneNode (true);
    newinput.name = 'form-'+forms.value + '-nuevo_extra_name';
    newinput.id = 'id_form-' + forms.value + '-nuevo_extra_name';
    newinput2.name = 'form-'+forms.value + '-nuevo_extra_price';
    newinput2.id = 'id_form-' + forms.value + '--nuevo_extra_price';
    document.querySelector('#formExtraContent').appendChild(newinput);
    document.querySelector('#formExtraContent').appendChild(newinput2);
    
    var p = document.createElement("p");
    document.querySelector('#formExtraContent').appendChild(p);
    forms.value = parseInt(forms.value) + 1;
    
}
function addInput2() {
    var forms = document.querySelector('#id_form-TOTAL_FORMS');
    // Clonamos los campos para el nuevo extra
    var newInputName = document.querySelector('#id_form-0-nuevo_extra_name').cloneNode(true);
    var newInputPrice = document.querySelector('#id_form-0-nuevo_extra_price').cloneNode(true);

    // Limpiamos los valores de los campos clonados
    newInputName.value = '';
    newInputPrice.value = '';

    // Asignamos nuevos valores a los nombres y ids de los nuevos campos
    newInputName.name = 'form-' + forms.value + '-nuevo_extra_name';
    newInputName.id = 'id_form-' + forms.value + '-nuevo_extra_name';
    
    newInputPrice.name = 'form-' + forms.value + '-nuevo_extra_price';
    newInputPrice.id = 'id_form-' + forms.value + '-nuevo_extra_price';

    // Creamos un contenedor div para la fila de los campos
    var newRowDiv = document.createElement('div');
    newRowDiv.classList.add('row');  // Clase para que los elementos estén en una fila

    // Creamos el primer div para el nombre del extra
    var newDiv = document.createElement('div');
    newDiv.classList.add('col-md-6'); // Clase para que ocupe la mitad del espacio
    var newDivInputName = document.createElement('div');
    newDivInputName.classList.add('input-group', 'mb-3');
    var spanName = document.createElement('span');
    spanName.classList.add('input-group-text');
    spanName.textContent = 'Nuevo nombre del extra';
    
    newDivInputName.appendChild(spanName);
    newDivInputName.appendChild(newInputName);
    newDiv.appendChild(newDivInputName);

    // Creamos el segundo div para el precio del extra
    var newDiv2 = document.createElement('div');
    newDiv2.classList.add('col-md-6'); // Clase para que ocupe la mitad del espacio
    var newDivInputPrice = document.createElement('div');
    newDivInputPrice.classList.add('input-group', 'mb-3');
    var spanPrice = document.createElement('span');
    spanPrice.classList.add('input-group-text');
    spanPrice.textContent = '$ Nuevo Precio del Extra';

    
    newDivInputPrice.appendChild(newInputPrice);
    newDivInputPrice.appendChild(spanPrice);
    newDiv2.appendChild(newDivInputPrice);

    // Agregamos ambos divs a la fila
    newRowDiv.appendChild(newDiv);
    newRowDiv.appendChild(newDiv2);

    // Finalmente, agregamos la fila de campos al contenido del formulario
    document.querySelector('#formExtraContent').appendChild(newRowDiv);
    
    // Agregar un espacio entre los formularios
    var p = document.createElement("p");
    document.querySelector('#formExtraContent').appendChild(p);

    // Incrementar el total de formularios
    forms.value = parseInt(forms.value) + 1;
}

