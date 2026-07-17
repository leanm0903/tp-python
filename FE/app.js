// Referencias a los elementos del DOM
const fileInput = document.getElementById('csvFileInput');
const loader = document.getElementById('loader');
const resultsContainer = document.getElementById('results-container');
const llmText = document.getElementById('llm-insight-text');
const tableBody = document.getElementById('data-table-body');

// Escuchar el evento cuando el usuario selecciona un archivo
fileInput.addEventListener('change', async (event) => {
    const archivo = event.target.files[0];
    
    if (!archivo) return;

    // 1. Mostrar estado de carga y ocultar resultados anteriores
    loader.style.display = 'block';
    resultsContainer.style.display = 'none';
    tableBody.innerHTML = ''; 
    llmText.textContent = ''; 

    // 2. Preparar los datos para enviar al backend
    const formData = new FormData();
    formData.append('archivo', archivo);

    try {
        // 3. Hacer la petición POST al backend (FastAPI)
        const respuesta = await fetch('https://tp-python-m77v.onrender.com/api/analisis-bonos', {
            method: 'POST',
            body: formData
        });

        if (!respuesta.ok) {
            throw new Error('Error en el servidor de Python');
        }

        const datos = await respuesta.json();

        // 4. Inyectar el texto del LLM
        llmText.innerHTML = datos.analisis_llm;
        // 5. Generar las filas de la tabla con los datos de Pandas
        datos.metricas.forEach(fila => {
            const tr = document.createElement('tr');
            
            // Formatear números a 2 decimales
            const precioStr = `$${fila.precio_promedio.toFixed(2)}`;
            const volatilidadStr = fila.volatilidad.toFixed(2);

            tr.innerHTML = `
                <td>${fila.Ticker}</td>
                <td>${precioStr}</td>
                <td>${volatilidadStr}</td>
            `;
            tableBody.appendChild(tr);
        });

        // 6. Mostrar los resultados
        resultsContainer.style.display = 'block';

    } catch (error) {
        console.error('Hubo un problema procesando el archivo:', error);
        alert('Hubo un error al procesar el archivo. Revisá la consola.');
    } finally {
        // 7. Ocultar el loader termine bien o mal
        loader.style.display = 'none';
        fileInput.value = ''; // Resetear el input para permitir subir el mismo archivo de nuevo
    }
});