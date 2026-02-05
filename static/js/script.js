//Para que los mensajes se borren al teclar un input
const inputs = document.querySelectorAll("input");

inputs.forEach(input => {
    input.addEventListener("input", () => {
        document.querySelectorAll(".alert").forEach(alert => alert.remove());
    });
});

//Para que los mensajes se borren a los 3 segundos
setTimeout(function () {
    const alerts = document.querySelectorAll(".alert-auto-close");
    alerts.forEach(alert => {
        alert.style.transition = "opacity 0.5s";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
    });
}, 3000); // 3 segundos

//Para que al dar check al checkbox, se habilite introducir también correo
const adminCheckbox = document.getElementById('admin');
const emailInput = document.getElementById('email');
const roleCheckboxes = document.querySelectorAll('.role-checkbox');

if (adminCheckbox) {
    adminCheckbox.addEventListener('change', function () {

        const isAdmin = this.checked;

        // Email
        if (emailInput) {
            emailInput.disabled = !isAdmin;
            if (!isAdmin) {
                emailInput.value = '';
            }
        }

        // Roles
        roleCheckboxes.forEach(role => {
            role.disabled = !isAdmin;

            // Opcional: desmarcar roles si deja de ser admin
            if (!isAdmin) {
                role.checked = false;
            }
        });
    });
}


//Para que el dropdown de sexo sea required
document.querySelectorAll('.formAgregarPersona .dropdown-item').forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();

        const value = this.getAttribute('data-value');
        const text = this.textContent;

        document.getElementById('sexoInput').value = value;
        document.getElementById('sexoBtn').textContent = text;
    });
});

//Para que todas las filas de la tabla sean clickeables
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".clickable-row").forEach(row => {
        row.addEventListener("click", () => {
            // prueba
            console.log("Fila clickeada");
            window.location.href = row.dataset.href;
        });
    });
});

//Ajax para el search -------------------------------------------------------------------------
const searchInput = document.getElementById("search-input");
const tableBody = document.getElementById("personas-table");

if (searchInput) {
    let timeout = null;

    searchInput.addEventListener("keyup", function () {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            const query = this.value;
            const params = new URLSearchParams(window.location.search);

            if (query.trim() === "") {
                params.delete("search");
            } else {
                params.set("search", query);
            }

            fetch(`${window.location.pathname}?${params.toString()}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.text())
            .then(html => {
                tableBody.innerHTML = html;
                activarFilasClick(); // 🔥 volver a activar clicks
            });
        }, 300); // debounce
    });
}

function activarFilasClick() {
    document.querySelectorAll(".clickable-row").forEach(row => {
        row.addEventListener("click", () => {
            window.location.href = row.dataset.href;
        });
    });
}

document.addEventListener("DOMContentLoaded", activarFilasClick);

//Para activar o desactivar empleados y visitantes en Control ------------------------------------
const visitanteCheckbox = document.getElementById("soy-visitante");
const visitanteFields = document.getElementById("visitante-fields");
const empleadoFields = document.getElementById("empleado-fields");

const nombreInput = document.getElementById("nombre_visitante");
const apellidoInput = document.getElementById("apellido_visitante");
const cedulaInput = document.getElementById("cedula_visitante");
const codigoInput = document.getElementById("codigo_empleado");

if (visitanteCheckbox) {
    visitanteCheckbox.addEventListener("change", () => {
        if (visitanteCheckbox.checked) {
            visitanteFields.style.display = "block";
            nombreInput.required = true;
            apellidoInput.required = true;
            cedulaInput.required = true;
            codigoInput.required = false;
            empleadoFields.style.display = "none";
        } else {
            visitanteFields.style.display = "none";
            empleadoFields.style.display = "block";
            codigoInput.required = true;
            nombreInput.required = false;
            apellidoInput.required = false;
            cedulaInput.required = false;

            nombreInput.value = "";
            apellidoInput.value = "";
            cedulaInput.value = "";
        }
    });
}


//Para que autollene nombre y apellido al teclear cedula en control --------------------------------------

if (cedulaInput) {
    let timeout = null;

    cedulaInput.addEventListener("keyup", function () {
        clearTimeout(timeout);

        const cedula = this.value.trim();

        if (cedula.length < 5) {
            nombreInput.value = "";
            apellidoInput.value = "";
            return;
        }

        timeout = setTimeout(() => {
            fetch(`/buscar-persona/?cedula=${cedula}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.found) {
                    nombreInput.value = data.nombres;
                    apellidoInput.value = data.apellidos;
                } else {
                    nombreInput.value = "";
                    apellidoInput.value = "";
                }
            });
        }, 400); // debounce
    });
}

//Canvas para el gráfico de Dashboard -----------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const ingresosDataEl = document.getElementById('ingresos-data');

    if (ingresosDataEl) {  // ✅ Solo si existe
        const ingresos = JSON.parse(ingresosDataEl.textContent);
        const labels = ingresos.map(i => i.fecha);
        const values = ingresos.map(i => i.cantidad);

        const ctx = document.getElementById('ingresosChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ingresos',
                    data: values,
                    backgroundColor: 'rgba(0, 50, 160, 0.5)',
                    borderColor: '#0032A0',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        precision: 0
                    }
                }
            }
        });
    }
});

//Estadisticos - Ingresos dia --------------------------------------------------------------------------
const ingresosPeriodoEl = document.getElementById('ingresos-periodo-data');
if (ingresosPeriodoEl) {
    const ingresos = JSON.parse(ingresosPeriodoEl.textContent);
    if (Array.isArray(ingresos)) {
        const labels = ingresos.map(i => i.periodo);
        const values = ingresos.map(i => i.cantidad);

        const ctx = document.getElementById('ingresosPorPeriodoChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets: [{ label: 'Ingresos', data: values, backgroundColor: 'rgba(0,50,160,0.5)', borderColor: '#0032A0', borderWidth: 1 }] },
            options: {
                responsive: true,
                scales: {
                    x: {
                        ticks: { autoSkip: true, maxTicksLimit: 12 } // max 12 etiquetas visibles
                    },
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

//Estadisticos - Ingresos por hora ------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const el = document.getElementById("ingresos-por-hora-data");
    if (!el) return;

    const data = JSON.parse(el.textContent);

    // ⛔ NO reordenes aquí, Django ya lo hizo bien
    const labels = data.map(i => i.hora_label);
    const values = data.map(i => i.cantidad);

    const ctx = document.getElementById("ingresosPorHoraChart").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Ingresos",
                data: values,
                backgroundColor: "rgba(0,50,160,0.6)"
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});


//Estadisticos - Tipo de persona ------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const el = document.getElementById("ingresos-tipo-data");

    if (!el) return;

    const data = JSON.parse(el.textContent);

    const labels = data.map(i => i.nombre);
    const values = data.map(i => i.cantidad);

    const ctx = document.getElementById("tipoPersonaChart").getContext("2d");

    new Chart(ctx, {
        type: "pie",
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    "#0032A0",
                    "#0D6EFD",
                    "#6EA8FE",
                    "#ADB5BD",
                    "#198754",
                    "#DC3545"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
});

//Estadisticas: Ingresos por departamentos --------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const el = document.getElementById("ingresos-departamento-data");
    if (!el) return;

    const data = JSON.parse(el.textContent);

    const labels = data.map(d => d.nombre);
    const values = data.map(d => d.cantidad);

    const ctx = document.getElementById("departamentoChart").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Ingresos",
                data: values,
                backgroundColor: "rgba(25,135,84,0.6)"
            }]
        },
        options: {
            indexAxis: 'y', // 👈 horizontal (mejor para textos largos)
            scales: {
                x: { beginAtZero: true }
            }
        }
    });
});

//Estadisticas: Personas dentro por departamento ----------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    const el = document.getElementById("personas-dep-data");
    if (!el) return;

    const data = JSON.parse(el.textContent);

    const labels = data.map(i => i.nombre);
    const values = data.map(i => i.cantidad);

    const ctx = document
        .getElementById("personasDepartamentoChart")
        .getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Personas dentro",
                data: values,
                backgroundColor: "rgba(60, 160, 120, 0.7)"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});

//---------------------------------------------------------------------------------------
//    CAMBIAR IMAGEN AL EDITAR
//---------------------------------------------------------------------------------------
const fotoInput = document.getElementById('fotoInput');
const fotoPreview = document.getElementById('fotoPreview');

if (fotoInput) {
    fotoInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                fotoPreview.src = e.target.result;
                fotoPreview.style.display = 'block';
            }
            reader.readAsDataURL(file);
        }
    });
}

//------------------------------------------------------------------------------------------
//    HABILITAR Y DESABILITAR REQUIRED EN CONTROL
//------------------------------------------------------------------------------------------
const form = document.getElementById("movimientoForm");
const select = document.getElementById("departamentoSelect");
const btnEntrada = document.getElementById("btnEntrada");
const btnSalida = document.getElementById("btnSalida");

// Antes de enviar el formulario
if (btnEntrada && visitanteCheckbox.checked) {
    btnEntrada.addEventListener("click", function() {
        // Si se va a hacer Entrada, el select es obligatorio
        select.required = true;
    });
}

if (btnSalida && visitanteCheckbox.checked) {
    btnSalida.addEventListener("click", function() {
        // Si se va a hacer Salida, no hace falta seleccionar departamento
        select.required = false;
    });
}

//-------------------------------------------------------------------------------------------------
//    PARA CONTROL VEHICULO
//-------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {

    const placaInput = document.getElementById("placa");
    const vehiculoFields = document.getElementById("vehiculo-fields");

    if (!placaInput || !vehiculoFields) {
        console.log("No estamos en control_vehiculo");
        return;
    }

    if(placaInput){
        placaInput.addEventListener("blur", function () {
            const placa = this.value.trim();
            if (!placa) return;

            fetch(`/ajax/buscar-vehiculo/?placa=${placa}`)
                .then(res => res.json())
                .then(data => {
                    vehiculoFields.style.display = "block";

                    if (data.existe) {
                        document.getElementById("marca").value = data.marca;
                        document.getElementById("modelo").value = data.modelo;
                        document.getElementById("codigo_vehiculo").value = data.codigo;

                        document.getElementById("marca").readOnly = true;
                        document.getElementById("modelo").readOnly = true;
                        document.getElementById("codigo_vehiculo").readOnly = true;
                    } else {
                        document.getElementById("marca").value = "";
                        document.getElementById("modelo").value = "";
                        document.getElementById("codigo_vehiculo").value = "";

                        document.getElementById("marca").readOnly = false;
                        document.getElementById("modelo").readOnly = false;
                        document.getElementById("codigo_vehiculo").readOnly = false;
                    }
                })
                .catch(err => console.error("Error AJAX:", err));
        });
    }
});

//-----------------------------------------------------------------------------------------
//    MODAL DE FORZAR SALIDA
//-----------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {



    const btnForzar = document.getElementById("btnForzarSalida");
    const codigoInput = document.getElementById("codigo_empleado");
    const codigoCed = document.getElementById("cedula_visitante");

    if (!btnForzar || !codigoInput || !codigoCed) return;

    if (btnForzar) {

        btnForzar.addEventListener("click", function () {

            console.log(codigoInput.visibility )

            if (visitanteCheckbox.checked) {
                if (!codigoCed.value.trim()) {
                    codigoCed.focus();
                    codigoCed.reportValidity(); // muestra el required
                    return;
                }
            } else {
                if (!codigoInput.value.trim()) {
                    codigoInput.focus();
                    codigoInput.reportValidity(); // muestra el required
                    return;
                }
            }



            // llenar modal
            if (visitanteCheckbox.checked) {
                document.getElementById("codigoTexto").textContent = codigoCed.value;
                document.getElementById("tipoTexto").textContent = "cédula";
            }else{
                document.getElementById("codigoTexto").textContent = codigoInput.value;
                document.getElementById("tipoTexto").textContent = "código";
            }

            document.getElementById("modal_codigo").value = codigoInput.value;

            // abrir modal
            const modal = new bootstrap.Modal(
                document.getElementById("forzarSalidaModal")
            );
            modal.show();
        });

    }


    const btnConfirmarForzarSalida = document.querySelector(
        'button[name="forzar_salida"].btn-danger'
    );

    const motivoTextarea = document.getElementById("motivoForzarSalida");

    if (btnConfirmarForzarSalida && motivoTextarea) {
        btnConfirmarForzarSalida.addEventListener("click", function (e) {
            if (!motivoTextarea.value.trim()) {
                e.preventDefault();
                motivoTextarea.focus();
                motivoTextarea.setCustomValidity("Debes indicar el motivo de la salida forzada");
                motivoTextarea.reportValidity();
            } else {
                motivoTextarea.setCustomValidity("");
            }
        });
    }

});

//-------------------------------------------------------------------------
//    Ajax para el search de Vehiculos
//-------------------------------------------------------------------------
const searchInputVehiculos = document.getElementById("search-input-vehiculos");
const tableBodyVehiculos = document.getElementById("vehiculos-table");

if (searchInputVehiculos) {
    let timeout = null;

    searchInputVehiculos.addEventListener("keyup", function () {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            const query = this.value;
            const params = new URLSearchParams(window.location.search);

            if (query.trim() === "") {
                params.delete("search");
            } else {
                params.set("search", query);
            }

            fetch(`${window.location.pathname}?${params.toString()}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.text())
            .then(html => {
                tableBodyVehiculos.innerHTML = html;
                activarFilasClick(); // 🔥 volver a activar clicks
            });
        }, 300); // debounce
    });
}

function activarFilasClick() {
    document.querySelectorAll(".clickable-row").forEach(row => {
        row.addEventListener("click", () => {
            window.location.href = row.dataset.href;
        });
    });
}

document.addEventListener("DOMContentLoaded", activarFilasClick);