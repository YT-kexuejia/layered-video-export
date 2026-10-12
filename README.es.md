# Talking Head Studio / Exportación de vídeo por capas

[简体中文](README.md) · [English](README.en.md) · **Español**

Entrega un vídeo de presentación a tu Agent para que realice la transcripción local, comprenda el contenido, diseñe escenas explicativas, añada animación 3D, genere subtítulos, prepare una vista previa web y exporte el resultado con renderizado acelerado por capas. El repositorio incluye la plantilla **Studio Blue** y admite otras plantillas compatibles.

![Vista previa web y panel de exportación](docs/images/web-interface.jpg)

![Plantilla Studio Blue](docs/images/studio-blue-template.png)

La persona de la imagen es ficticia. El repositorio no incluye retratos, vídeos de prueba, transcripciones ni exportaciones del usuario.

## Cómo funciona

Tu Agent interpreta la narración, decide qué debe comunicar cada escena y revisa el resultado. Las herramientas locales realizan la transcripción, la construcción, la vista previa y el renderizado. El proyecto no necesita una clave API de IA adicional ni inicia un servicio de IA oculto.

El flujo contiene nueve módulos conectados mediante archivos: entrada, voz, edición, dirección de arte, código visual, 3D, audio/subtítulos, renderizado por capas y revisión independiente. Consulta la [especificación de módulos](docs/zh/MODULES.md) y el [registro legible por máquina](config/workflow.modules.json). La arquitectura conserva la plantilla, los tiempos, las reglas de subtítulos y el resultado 1080p24.

## Usar el Skill con un Agent

```sh
git clone https://github.com/YT-kexuejia/layered-video-export.git
cd layered-video-export
npm install
python -m pip install -r requirements.txt
```

Entrega la carpeta del repositorio y tu vídeo a un Agent capaz de leer archivos, ejecutar comandos y revisar una página local. Usa este mensaje:

> Lee SKILL.md y realiza la posproducción de este vídeo con la plantilla incluida. Primero entrega la vista previa web y el archivo SRT. Comprueba la sincronización entre voz e imagen, el encuadre de la persona, las transiciones y la cobertura completa del lienzo; después exporta el resultado aprobado a 1080p24.

El Agent seguirá [SKILL.md](SKILL.md). Comandos principales:

```sh
python pipeline.py init "D:\ruta\video.mp4" --project "D:\ruta\mi-proyecto"
python pipeline.py transcribe --project "D:\ruta\mi-proyecto" --device cpu
# El Agent lee la transcripción y crea plan.json.
python pipeline.py build --project "D:\ruta\mi-proyecto"
set LVE_CONFIG=D:\ruta\mi-proyecto\config.json
python serve.py
```

Abre la dirección local que muestra `serve.py`. Desde la página puedes previsualizar, buscar, cambiar de capítulo, descargar el SRT e iniciar, continuar o pausar la exportación. La [guía completa](docs/zh/WORKFLOW.md) y la [especificación del plan](docs/zh/PLAN.md) describen el contrato técnico.

## Plantillas

La plantilla incluida está en [`templates/studio-blue`](templates/studio-blue). Ofrece fondos azules continuos, tipografía editorial, columna lateral para la persona, paletas por capítulo, esferas metálicas y varios diagramas 3D. La información aparece cuando se pronuncia la frase correspondiente. Los subtítulos eliminan la puntuación de frase, separan bloques con espacios y dividen las líneas largas.

Para usar una plantilla compatible descargada:

```sh
python pipeline.py build --project "D:\ruta\mi-proyecto" --template "D:\ruta\plantilla"
```

Consulta el [protocolo de plantillas](docs/zh/TEMPLATES.md). Las animaciones incluidas usan Anime.js y Three.js con licencia MIT; el fondo luminoso y el sistema visual Studio Blue son implementaciones propias. No se distribuyen fuentes, material del usuario ni imágenes de terceros.

## Exportación acelerada por capas

El motor codifica de forma continua el fondo y el 3D, captura la interfaz solo cuando cambia, crea una pequeña capa de onda con ManimGX, procesa la persona con FFmpeg y codifica segmentos verificados con NVIDIA NVENC. Cada 7.200 fotogramas, equivalentes a cinco minutos, valida un segmento antes de borrar sus imágenes temporales. Si el proceso se interrumpe, el trabajo queda disponible para continuar.

## Estructura del repositorio

```text
src/python/             módulos internos de Python
src/js/                 módulos de renderizado JavaScript
templates/studio-blue/  plantilla incluida
web/                    panel local de exportación
examples/basic/         ejemplo sintético y configuración
config/                 configuración del flujo de trabajo
docs/                   documentación de diseño, flujo y licencias
```

## Requisitos y licencia

El entorno validado es Windows con Python 3.13+, Node 22+, Chrome, FFmpeg/ffprobe, NVIDIA NVENC y Chrome AVC WebCodecs. La instalación de dependencias y la primera descarga del modelo de transcripción necesitan conexión a Internet.

El código propio y la plantilla incluida se publican con licencia MIT. Las dependencias mantienen sus licencias originales. El repositorio no incluye FFmpeg, wheels nativos de ManimGX, fuentes ni material del usuario. Consulta los [avisos de terceros](docs/legal/THIRD-PARTY-NOTICES.md) y la [auditoría de licencias](docs/legal/LICENSE-AUDIT.md).
