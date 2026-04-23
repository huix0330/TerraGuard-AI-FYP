import streamlit as st

# 1. Main Enterprise Config (Must be the very first line of Streamlit code!)
st.set_page_config(page_title="TerraGuard AI Enterprise", page_icon="🌍", layout="wide")

# 2. Define your pages with custom names and icons
vision_page = st.Page(
    page="views/vision.py", 
    title="Vision Engine", 
    icon="👁️", 
    default=True
)

map_page = st.Page(
    page="views/intel_map.py", 
    title="Geospatial Intel", 
    icon="🗺️"
)

# 3. Build the Navigation Sidebar
pg = st.navigation(
    {"TerraGuard Command Center": [vision_page, map_page]}
)

# 4. Run the selected page
pg.run()