import streamlit as st
from shared_functions import (
    load_food_data,
    create_similarity_search_collection,
    populate_similarity_collection,
    perform_similarity_search,
    perform_filtered_similarity_search,
)

# Configuración de la página
st.set_page_config(
    page_title="Buscador de Comida",
    page_icon="🍽️",
    layout="centered",
)

# Cargar datos solo una vez (se queda en memoria mientras la app esté abierta)
@st.cache_resource
def inicializar_buscador():
    food_items = load_food_data("./FoodDataSet.json")
    collection = create_similarity_search_collection(
        "web_food_search",
        {"description": "Colección para la app web"},
    )
    populate_similarity_collection(collection, food_items)
    return collection

# Título y subtítulo
st.title("🍽️ Buscador de Comida")
st.caption("Encuentra platos por significado, no solo por palabras exactas.")

# Inicializar (la primera vez tarda un poco; después es instantáneo)
with st.spinner("Cargando base de datos de alimentos..."):
    collection = inicializar_buscador()

# Barra lateral con filtros
st.sidebar.header("Filtros opcionales")

cocinas = [
    "Todas",
    "Italian",
    "Thai",
    "Mexican",
    "Indian",
    "Japanese",
    "French",
    "Mediterranean",
    "American",
    "Health Food",
    "Dessert",
]
cocina_seleccionada = st.sidebar.selectbox("Tipo de cocina", cocinas)

usar_calorias = st.sidebar.checkbox("Limitar calorías")
max_calorias = None
if usar_calorias:
    max_calorias = st.sidebar.slider("Máximo de calorías", 50, 800, 400, step=50)

num_resultados = st.sidebar.slider("Número de resultados", 1, 10, 5)

# Caja de búsqueda principal
query = st.text_input(
    "¿Qué estás buscando?",
    placeholder="Ej: chocolate dessert, spicy chicken, light meal...",
)

# Botón de búsqueda
buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)

# Lógica de búsqueda
if buscar and query:
    with st.spinner("Buscando..."):
        if cocina_seleccionada == "Todas" and max_calorias is None:
            resultados = perform_similarity_search(collection, query, num_resultados)
        else:
            cocina_filtro = None if cocina_seleccionada == "Todas" else cocina_seleccionada
            resultados = perform_filtered_similarity_search(
                collection,
                query,
                cuisine_filter=cocina_filtro,
                max_calories=max_calorias,
                n_results=num_resultados,
            )

    if not resultados:
        st.warning("No se encontraron platos con esos criterios. Prueba con otros términos.")
    else:
        st.success(f"Se encontraron {len(resultados)} recomendaciones")
        st.markdown("---")

        for i, plato in enumerate(resultados, 1):
            score = plato["similarity_score"] * 100
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{i}. {plato['food_name']}")
                with col2:
                    st.metric("Coincidencia", f"{score:.1f}%")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"🏷️ **Cocina:** {plato['cuisine_type']}")
                with col_b:
                    st.write(f"🔥 **Calorías:** {plato['food_calories_per_serving']}")

                st.write(f"📝 {plato['food_description']}")
                st.markdown("---")

elif buscar and not query:
    st.error("Por favor escribe algo en la caja de búsqueda.")

# Pie de página
st.markdown("---")
st.caption(
    "Construido con Streamlit y ChromaDB · "
    "Búsqueda semántica con el modelo all-MiniLM-L6-v2"
)