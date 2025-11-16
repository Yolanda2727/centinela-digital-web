# app.py
import streamlit as st

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Centinela Digital – Integridad Académica con IA",
        layout="centered"
    )

    # Título
    st.title("🛡️ Centinela Digital")
    st.subheader("Monitorizando la integridad académica y científica con apoyo de IA")

    # Descripción inicial
    st.markdown(
        """
        Bienvenido al **Centinela Digital**, una herramienta web diseñada para apoyar a 
        profesores, semilleros, comités académicos y comités de ética en la identificación 
        preliminar de posibles inconsistencias, desviaciones o riesgos en trabajos académicos 
        y científicos.

        ### 🔧 Estado actual (versión inicial)
        Esta es la **versión mínima estable**, necesaria para desplegar en Streamlit Cloud, 
        que incluye:
        - Registro del rol de quien entrega el producto académico.
        - Registro del tipo de documento entregado.
        - Área para pegar un fragmento de texto.
        - Resumen del caso ingresado.

        ### 🚀 Próximos pasos que iremos agregando:
        - Carga de archivos Word/PDF.
        - Evidencias y matriz de riesgo.
        - Gráficos.
        - Explicación narrativa basada en IA.
        - Generación automática de informe ético.

        *Vamos paso a paso, construyéndolo de forma profesional.*
        """
    )

    st.divider()

    # Formulario
    st.header("1️⃣ Datos básicos del caso")

    rol = st.radio(
        "Rol de quien entrega el trabajo:",
        ["estudiante", "docente-investigador"],
        horizontal=True
    )

    tipo_producto = st.text_input(
        "Tipo de producto académico (ensayo, artículo, tesis, informe, etc.):"
    )

    texto_trabajo = st.text_area(
        "Pega aquí un fragmento del texto a analizar:",
        height=200
    )

    st.divider()

    # Botón de análisis
    if st.button("🔍 Analizar (versión de prueba)"):
        if not tipo_producto.strip() or not texto_trabajo.strip():
            st.warning("⚠️ Debes ingresar el tipo de producto y un fragmento de texto para continuar.")
        else:
            st.header("2️⃣ Resultado preliminar (demo)")

            st.markdown(f"- **Rol registrado:** `{rol}`")
            st.markdown(f"- **Tipo de producto:** `{tipo_producto}`")

            st.markdown("**Fragmento recibido:**")
            st.write(texto_trabajo[:700] + ("..." if len(texto_trabajo) > 700 else ""))

            st.info(
                """
                ✔️ Esta es solo una demostración inicial.

                En los siguientes pasos incorporaremos:
                - Algoritmo de riesgo ético.
                - Evidencias marcadas por el profesor.
                - Indicadores de integridad.
                - Programas sugeridos.
                - Informe ético narrativo generado por IA (OpenAI).
                """
            )

if __name__ == "__main__":
    main()
