<p align="center">
  <img src="assets/readme-banner.svg" width="100%" alt="FaceGuard Santa Cruz — tecnología que cuida nuestra tierra." />
</p>

<p align="center">
  <samp>「 tecnología cruceña, datos en casa y reconocimiento al toque 」</samp>
</p>

<p align="center">
  <a href="#el-proyecto">el proyecto</a> &nbsp;•&nbsp;
  <a href="#instalacion">instalación</a> &nbsp;•&nbsp;
  <a href="#camaras">cámaras</a> &nbsp;•&nbsp;
  <a href="#base-de-datos">base de datos</a> &nbsp;•&nbsp;
  <a href="#privacidad">privacidad</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/alejondr3/Reconocedor-de-caras/tests.yml?branch=main&style=flat-square&label=COMPILACI%C3%93N&color=007A3D" alt="Estado de compilación" />
  <img src="https://img.shields.io/github/last-commit/alejondr3/Reconocedor-de-caras?style=flat-square&label=%C3%9ALTIMA%20ACTUALIZACI%C3%93N&color=007A3D" alt="Última actualización" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-007A3D?style=flat-square&logo=python&logoColor=white" alt="Python 3.10 o superior" />
  <img src="https://img.shields.io/badge/PROCESAMIENTO-LOCAL-007A3D?style=flat-square" alt="Procesamiento local" />
</p>

> [!IMPORTANT]
> **Prototipo tecnológico para presentación.** Este repositorio no es un sitio
> oficial, no usa el logotipo institucional y no implica aval formal del Gobierno
> Autónomo Departamental de Santa Cruz. Cualquier despliegue institucional debe
> pasar por revisión técnica, jurídica, de seguridad y de identidad corporativa.

<br />

<a id="el-proyecto"></a>

## 01 / El proyecto

**FaceGuard Santa Cruz** es un sistema local de reconocimiento facial para
webcams, cámaras IP y videos existentes. Está pensado como una demostración de
tecnología aplicada desde Santa Cruz, con énfasis en privacidad y funcionamiento
con cámaras de calidad variable.

| componente | qué hace |
| --- | --- |
| `YuNet` | detecta una o varias caras en la imagen |
| `SFace` | convierte cada rostro en un vector biométrico |
| `SQLite` | guarda nombres y embeddings de manera local |
| `RTSP` | conecta cámaras de seguridad en tiempo real |
| `Low-quality mode` | mejora contraste, tamaño y estabilidad temporal |
| `Recorder` | genera videos MP4 con nombres y rectángulos |

<p align="center">
  <img src="assets/live-terminal.svg" width="100%" alt="Nodo cruceño de FaceGuard funcionando en tiempo real." />
</p>

<details>
<summary><strong>🌴 Modo camba técnico — abrir glosario</strong></summary>

| como lo decimos | qué significa técnicamente |
| --- | --- |
| **levantalo al toque** | iniciar la aplicación y cargar los modelos |
| **de una, puej** | ejecutar el flujo sin pasos innecesarios |
| **cámara mañosa** | fuente con baja resolución, ruido o compresión |
| **sin hacer macanas** | validar antes de borrar, importar o desplegar |
| **quedó joya** | reconocimiento estable después de calibrar |
| **datos en casa** | procesamiento local sin API biométrica externa |
| **no te aplazés con el umbral** | medir falsos positivos antes de bajarlo |

</details>

<br />

<a id="instalacion"></a>

## 02 / Instalación al toque

### Windows — sin usar consola

1. Instala [Python 3.10 o superior](https://www.python.org/downloads/) y marca
   **Add Python to PATH**.
2. Pulsa **Code → Download ZIP** en GitHub.
3. Descomprime el proyecto en una carpeta normal.
4. Haz doble clic en `instalar.bat`.
5. Espera hasta ver **INSTALACIÓN COMPLETADA**.
6. Abre el sistema con `iniciar.bat`.

La primera instalación descarga OpenCV y dos modelos ONNX. Después de eso puede
funcionar sin Internet.

### Registrar una persona

1. Escribe el nombre del participante autorizado.
2. Deja `0` como cámara para usar la webcam principal.
3. Mantén activo **Modo cámara de baja calidad**.
4. Selecciona entre 30 y 60 fotografías.
5. Pulsa **Registrar persona**.
6. Mira al frente y gira lentamente la cabeza.

> **Consejo de la casa:** registrá a la persona con la misma cámara, distancia e
> iluminación que tendrá el sistema final. Así no hay sorpresas después, puej.

<br />

<a id="camaras"></a>

## 03 / Cámaras y videos

### Webcam

Usa `0` para la cámara principal. Si tienes varias, prueba `1`, `2` o `3`.

### Cámara de seguridad mediante RTSP

La cámara debe ofrecer un stream RTSP. Actívalo en su configuración y crea un
usuario exclusivo de solo lectura.

```text
rtsp://usuario:contraseña@192.168.1.50:554/ruta-del-stream
```

1. Conecta la computadora y la cámara a la misma red.
2. Prueba primero la URL en VLC.
3. Pégala en **Cámara (0 o URL RTSP)**.
4. Marca **Grabar reconocimiento en video** si necesitas una copia procesada.
5. Pulsa **Iniciar reconocimiento**.

Las grabaciones quedan en `data/recordings/`. No publiques la URL RTSP porque
normalmente contiene credenciales reales.

### Analizar un video existente

1. Pulsa **Elegir video**.
2. Selecciona MP4, AVI, MOV, MKV, M4V o WMV.
3. Activa la grabación si quieres conservar el resultado anotado.
4. Pulsa **Iniciar reconocimiento**.

El original nunca se modifica. El análisis termina automáticamente al llegar al
último cuadro.

<br />

## 04 / Protocolo para cámaras mañosas

El modo de baja calidad amplía el cuadro, aplica CLAHE, crea una segunda lectura
con realce de detalle y conserva temporalmente una identidad durante cuadros
borrosos.

1. Registra 40–60 vistas desde la cámara real.
2. Empieza con umbral `0.36`.
3. Si rechaza conocidos, prueba `0.34`.
4. Si confunde personas, sube a `0.40` o `0.44`.
5. No bajes de `0.30`.
6. Prueba también con personas no registradas.
7. Procura que la cara mida al menos unos 55 píxeles.

> **Desconocido también es una respuesta válida.** Forzar una identidad cuando
> no hay detalle suficiente aumenta los falsos positivos. Ni el mejor código
> puede inventar los píxeles que la cámara nunca capturó.

<br />

<a id="base-de-datos"></a>

## 05 / Base de datos — todo en casa

La memoria activa vive en `data/faces.db`. Las fotografías están en
`data/photos/` y las grabaciones en `data/recordings/`. Estas rutas están
excluidas de Git.

| opción | resultado |
| --- | --- |
| **Importar base SQLite** | valida y combina personas y embeddings |
| **Crear respaldo** | genera un ZIP con la base y las fotografías |
| **Eliminar base de datos** | pide dos confirmaciones y crea una base vacía |
| **Actualizar lista** | vuelve a leer las personas registradas |

Antes de importar se crea automáticamente un respaldo en `data/backups/`. Los
registros repetidos se omiten. Sin vueltas y sin hacer macanas.

<details>
<summary><strong>⌨️ Acceso técnico por consola</strong></summary>

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
faceguard download-models
faceguard enroll --name "Ana" --samples 40
faceguard recognize --camera 0 --threshold 0.36
faceguard list
faceguard delete --name "Ana"
```

Para una cámara IP:

```powershell
faceguard recognize --camera "rtsp://usuario:clave@192.168.1.50/stream"
```

</details>

<br />

<a id="privacidad"></a>

## 06 / Privacidad y uso responsable

Las fotografías, nombres, videos y embeddings son datos sensibles. Para una
presentación responsable ante una institución pública:

- Obtén consentimiento antes de registrar a cada participante.
- Señaliza las cámaras que realizan identificación.
- Usa cuentas RTSP de solo lectura.
- Cifra el disco y restringe el acceso a `data/`.
- Define tiempos de conservación y eliminación.
- Mantén revisión humana en cualquier decisión relevante.
- No uses reconocimiento facial como único control de acceso.
- Evalúa falsos positivos por cámara y condición de iluminación.
- Documenta quién puede crear, importar, respaldar o eliminar la base.

<br />

## 07 / Arquitectura

```mermaid
flowchart LR
    A[Webcam / RTSP / Video] --> B[CLAHE + Upscale]
    B --> C[YuNet Detector]
    C --> D[SFace / 128D]
    D --> E[(SQLite local)]
    E --> F{Umbral coseno}
    F -->|coincide| G[Identidad conocida]
    F -->|rechaza| H[Desconocido]
    G --> I[Vista + MP4]
    H --> I
```

```text
src/faceguard/     motor, interfaz, calidad, SQLite y CLI
tests/             pruebas unitarias sin cámara
assets/            identidad visual del proyecto
models/            modelos ONNX ignorados por Git
data/              base, fotos y grabaciones ignoradas por Git
```

### Pruebas

```powershell
pip install -r requirements-dev.txt
pytest -q
```

<br />

<p align="center">
  <strong>Verde por nuestra tierra. Blanco por nuestra gente. Datos bajo nuestro control.</strong><br />
  <samp>FaceGuard Santa Cruz // hecho con código, cuidado y orgullo cruceño</samp>
</p>
