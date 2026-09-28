
import os
import tempfile
import streamlit as st

# Configurar variables de entorno antes de importar librerías pesadas
os.environ["HOME"] = "/tmp"
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TORCH_HOME"] = "/tmp/torch"
os.environ["RAPIDOCR_CACHE_DIR"] = "/tmp/rapidocr"

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# 1. Configuración de la interfaz de usuario
st.set_page_config(
    page_title="PDF a Markdown con Docling",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Conversor de PDF a Markdown")
st.markdown("Sube tu archivo PDF para extraer texto, tablas y estructuras complejas formateadas nativamente en **Markdown** mediante la IA de **IBM Docling**.")

# 2. Inicialización optimizada del modelo (Se ejecuta una sola vez gracias a la caché)
@st.cache_resource
def obtener_convertidor():
    pipeline_options = PdfPipelineOptions()
    # Desactivar OCR de imágenes escaneadas para PDFs digitales nativos (evita el bug de descarga externa de RapidOCR)
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

with st.spinner("Inicializando modelos de Docling en el contenedor..."):
    convertidor = obtener_convertidor()

# 3. Zona de carga del archivo
archivo_subido = st.file_uploader("Elige un archivo PDF", type=["pdf"])

if archivo_subido is not None:
    st.success(f"Archivo cargado con éxito: {archivo_subido.name}")
    
    # Botón para iniciar el procesamiento pesado de IA
    if st.button("🚀 Convertir a Markdown"):
        
        # Crear un spinner para indicar progreso en la UI
        with st.spinner("Procesando estructura del PDF, tablas y OCR... por favor espera."):
            try:
                # Docling necesita una ruta de archivo física. 
                # Guardamos el archivo subido en memoria temporalmente en el contenedor.
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as archivo_temporal:
                    archivo_temporal.write(archivo_subido.getvalue())
                    ruta_temporal = archivo_temporal.name

                # Ejecutar la conversión nativa de Docling
                resultado = convertidor.convert(ruta_temporal)
                
                # Exportar el resultado estructurado directamente a Markdown
                contenido_markdown = resultado.document.export_to_markdown()

                # Eliminar el archivo temporal del contenedor de forma segura
                os.unlink(ruta_temporal)

                # 4. Mostrar resultados y habilitar descarga
                st.balloons()
                st.subheader("✅ Conversión Finalizada")

                # Crear dos columnas: una para descargar y otra para previsualizar
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # Configurar botón de descarga del archivo .md generado
                    nombre_salida = archivo_subido.name.replace(".pdf", ".md")
                    st.download_button(
                        label="💾 Descargar Markdown",
                        data=contenido_markdown,
                        file_name=nombre_salida,
                        mime="text/markdown"
                    )

                with col2:
                    st.info("Puedes copiar el contenido o descargarlo usando el botón de la izquierda.")

                # Mostrar previsualización del Markdown estructurado y del código crudo
                pestana_visual, pestana_codigo = st.tabs(["👁️ Vista Previa Renderizada", "💻 Código Markdown Nativo"])
                
                with pestana_visual:
                    st.markdown(contenido_markdown)
                    
                with pestana_codigo:
                    st.code(contenido_markdown, language="markdown")

            except Exception as e:
                st.error(f"Ocurrió un error durante la conversión: {e}")
                st.info("Asegúrate de que tu contenedor tenga asignados mínimo 8GB de memoria RAM.")

