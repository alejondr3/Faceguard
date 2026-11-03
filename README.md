<p align="center">
  <img src="assets/puejface-cover-v3.svg" width="100%" alt="PuejFace. Reconocimiento facial, al toque. Diseño verde bosque y marfil con identidad cruceña." />
</p>

<p align="center">
  <strong>Tecnología cruceña. Procesamiento local. Datos en casa.</strong><br />
  Una herramienta de escritorio para registrar personas, reconocer rostros y analizar video.
</p>

<p align="center">
  <a href="#instalacion">Instalación</a> &nbsp; / &nbsp;
  <a href="#primer-uso">Primer uso</a> &nbsp; / &nbsp;
  <a href="#fuentes">Cámaras y videos</a> &nbsp; / &nbsp;
  <a href="#datos">Datos y respaldos</a> &nbsp; / &nbsp;
  <a href="#tecnico">Documentación técnica</a>
</p>

<p align="center">
  <a href="https://github.com/alejondr3/Faceguard/actions"><img src="https://img.shields.io/github/actions/workflow/status/alejondr3/Faceguard/tests.yml?branch=main&amp;style=flat-square&amp;label=tests&amp;color=08714c" alt="Estado de las pruebas" /></a>
  <img src="https://img.shields.io/github/last-commit/alejondr3/Faceguard?style=flat-square&amp;label=actualizado&amp;color=08714c" alt="Última actualización" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-174c35?style=flat-square" alt="Python 3.10 o superior" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/licencia-MIT-174c35?style=flat-square" alt="Licencia MIT" /></a>
</p>

<br />

<img src="assets/puejface-sources-v3.svg" width="100%" alt="Webcam: registro desde computadora. Cámara IP: stream RTSP. Video: análisis de archivos locales." />

## Hecho para conectar, registrar y reconocer

**PuejFace** utiliza YuNet para detectar rostros y SFace para extraer embeddings.
Las identidades se comparan con una base SQLite en tu computadora. El registro
incorpora muestras a esa base usando modelos preentrenados.

<table>
<tr>
<td width="50%" valign="top">

### 📷 Registro guiado

Nombre, cámara y cantidad de fotos desde la interfaz. Los recortes aceptados se guardan como dataset local.

</td>
<td width="50%" valign="top">

### 🌿 Calidad variable

Contraste local, escalado y una segunda lectura realzada para trabajar con imágenes difíciles.

</td>
</tr>
<tr>
<td valign="top">

### 🎞️ Video procesado

Visualización con nombres y rectángulos, con opción de guardar una copia MP4 anotada.

</td>
<td valign="top">

### 🗄️ SQLite integrada

Importación compatible, respaldos y eliminación con confirmación desde la aplicación.

</td>
</tr>
</table>

<a id="instalacion"></a>

## Arrancá en tres pasos

| 01 · Descargá | 02 · Instalá | 03 · Abrí |
| :--- | :--- | :--- |
| **Code → Download ZIP**, y descomprimí la carpeta. | Ejecutá **instalar.bat** y esperá el mensaje de finalización. | Doble clic en **iniciar.bat**. De una, puej. |

Necesitás Windows, Python 3.10 o superior y conexión durante la primera instalación.

<details>
<summary><strong>Ver instalación paso a paso y soluciones frecuentes</strong></summary>

1. Instalá [Python](https://www.python.org/downloads/) y marcá **Add Python to PATH**.
2. Descargá el ZIP del repositorio y extraé su contenido en una carpeta normal.
3. Abrí esa carpeta y ejecutá `instalar.bat`.
4. Esperá **INSTALACIÓN COMPLETADA**. Se descargarán dependencias y modelos ONNX.
5. Ejecutá `iniciar.bat` cada vez que quieras usar la aplicación.

**Si falta Python:** instalalo y volvé a ejecutar el instalador.  
**Si la cámara no abre:** cerrá otras aplicaciones que la estén usando y probá los índices 0, 1 o 2.  
**Si falla una descarga:** comprobá la conexión y repetí la instalación.  
**Si actualizaste:** cerrá la aplicación y abrila otra vez. Ejecutá el instalador si cambiaron las dependencias.

</details>

<a id="primer-uso"></a>

## Tu primer reconocimiento

1. **Registrá:** escribí un nombre, dejá la cámara en `0` y elegí 30–60 fotos.
2. **Capturá:** pulsá **Registrar persona** y variá suavemente el ángulo de la cabeza.
3. **Reconocé:** pulsá **Iniciar reconocimiento**.
4. **Guardá:** activá la opción de grabación antes de iniciar si querés exportar el resultado.

> Registrá con iluminación, distancia y cámara similares a las del uso final.

<a id="fuentes"></a>

## Elegí tu fuente

<details open>
<summary><strong>Webcam · la conexión más rápida</strong></summary>

Escribí `0` en el campo de cámara. Si tenés varias, probá `1` o `2`.
Después pulsá **Iniciar reconocimiento**.

</details>

<details>
<summary><strong>Cámara IP · reconocimiento por RTSP</strong></summary>

1. Conectá cámara y computadora a la misma red.
2. Activá RTSP en la cámara y obtené la ruta del fabricante.
3. Probá esa dirección en VLC.
4. Pegala en el campo **Cámara (0 o URL RTSP)**.
5. Elegí si querés grabar y pulsá **Iniciar reconocimiento**.

Ejemplo de formato:

```text
rtsp://usuario:contraseña@192.168.1.50:554/ruta-del-stream
```

La dirección puede contener credenciales: evitá publicarla en capturas o commits.

</details>

<details>
<summary><strong>Archivo de video · analizá una grabación</strong></summary>

Pulsá **Elegir video**, seleccioná un MP4, AVI, MOV, MKV, M4V o WMV y luego
**Iniciar reconocimiento**. El archivo original permanece intacto.

Si activaste la grabación, la copia anotada se guarda en `data/recordings/`.
El análisis se detiene al terminar el archivo. Las personas deben estar registradas previamente.

</details>

## Cuando la cámara sale mañosa

El modo de baja calidad aplica escalado, CLAHE y realce de detalle.
Su eficacia depende del detalle real del rostro y debe evaluarse con tu cámara.

| Situación | Qué probar |
| :--- | :--- |
| Rechaza a alguien registrado | Agregá muestras desde la cámara final y compará resultados. |
| Confunde identidades | Subí el umbral y evaluá con personas ajenas a la base. |
| Imagen oscura o comprimida | Activá el modo de baja calidad y mejorá la iluminación. |
| Rostro muy pequeño | Acercá la cámara o utilizá un stream con mayor resolución. |
| Procesamiento lento | Reducí la resolución de entrada y comprobá la carga del equipo. |

El valor inicial es `0.36`. Cualquier ajuste debe medirse con coincidencias
correctas y falsos positivos. El realce no recupera detalle que nunca fue capturado.

<a id="datos"></a>

## Datos bajo control

| Botón | Acción |
| :--- | :--- |
| **Importar** | Combina bases compatibles y omite embeddings idénticos. |
| **Respaldo** | Exporta un ZIP con SQLite y fotografías. |
| **Eliminar** | Vacía la base tras dos confirmaciones; conserva las fotos. |
| **Actualizar** | Refresca las personas registradas. |

```text
data/
├── faces.db       Identidades y embeddings
├── photos/        Fotografías de registro
├── recordings/    Videos anotados
└── backups/       Copias previas a una importación
```

Estas rutas están excluidas de Git. Las fotos se copian por separado cuando
importás una base SQLite. El respaldo ZIP incluye base y fotos; las grabaciones se gestionan aparte.

<a id="tecnico"></a>

<details>
<summary><strong>Documentación técnica · modelos, comandos y pruebas</strong></summary>

### Flujo de procesamiento

```mermaid
flowchart LR
    A["Webcam · RTSP · Video"] --> B["Preparación de imagen"]
    B --> C["YuNet: detección"]
    C --> D["SFace: embeddings"]
    D --> E["Comparación con SQLite"]
    E --> F["Identidad o desconocido"]
    F --> G["Vista y MP4 opcional"]
    style A fill:#e8f2df,stroke:#08714c,color:#174c35
    style E fill:#e8f2df,stroke:#08714c,color:#174c35
    style G fill:#e8f2df,stroke:#08714c,color:#174c35
```

### Instalación y uso por consola

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
faceguard download-models
faceguard enroll --name "Ana" --samples 40
faceguard recognize --camera 0 --threshold 0.36
faceguard list
```

Los comandos conservan el nombre `faceguard`.

### Pruebas

```powershell
pip install -r requirements-dev.txt
pytest -q
```

Código en `src/faceguard/`, pruebas en `tests/` y recursos visuales en `assets/`.

</details>

<details>
<summary><strong>Presentación institucional y privacidad</strong></summary>

Prototipo para demostración y evaluación. El repositorio no acredita aval oficial
de la Gobernación de Santa Cruz.

Registrá participantes con consentimiento, restringí el acceso a fotografías,
embeddings y videos, y definí plazos de conservación. Para decisiones relevantes,
mantené revisión humana y un método adicional de verificación.

</details>

<br />

---

<p align="center">
  <strong>PuejFace · Santa Cruz, Bolivia</strong><br />
  <sub>De una, puej. Tecnología cercana, con los datos en casa.</sub>
</p>
