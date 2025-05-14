import streamlit as st
import pandas as pd
import plotly.express as px
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from datetime import datetime
import base64
import os
import geopandas as gpd

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="India EV Insights Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Static CSS Styling (No Background Image) ----------
# Apply styling for content blocks, sidebar, buttons, and headers
st.markdown(
    """
    <style>
    /* Ensure the app background is a standard color */
    /* Content blocks with semi-transparent background for readability */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.92); /* White with 92% opacity */
        border-radius: 10px;
        padding: 20px;
        margin-top: 1rem; /* Add some margin to avoid sticking to header */
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Optional: subtle shadow */
    }
    /* Sidebar styling */
    .css-1d391kg { /* This class targets sidebar, might change with Streamlit updates */
        background-color: rgba(240, 242, 246, 0.95) !important; /* Light grey with more opacity */
    }
    /* Specific styling for buttons in sidebar for better appearance */
    div[data-testid="stSidebarNav"] ul {
        padding-top: 1rem;
    }
    /* Styling for the main sidebar buttons (not the nav links) */
    div[data-testid="stSidebarContent"] div[data-testid="stButton"] > button {
        display: block;
        width: 95%; /* Try to make it take most of the sidebar width */
        margin: 8px auto 8px auto; /* Some vertical margin, auto for horizontal centering */
        padding: 12px 0px; /* More vertical padding */
        font-size: 1.1em; /* Larger font */
        font-weight: bold;
        border-radius: 5px;
        border: 1px solid #cccccc; /* Subtle border */
        text-align: center;
    }
     div[data-testid="stSidebarContent"] div[data-testid="stButton"] > button:hover {
        border-color: #007bff; /* Highlight on hover */
        background-color: #e9ecef; /* Slight background change on hover */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50; /* Darker color for headers for better contrast */
    }
    /* Style for the image container in the header */
    .header-image-container img {
        border-radius: 8px; /* Optional: round the corners of the header image */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Optional: add a slight shadow to the image */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------- Data Loading and Caching ----------
@st.cache_data(ttl=3600) # Cache for 1 hour
def load_data():
    try:
        vehicalclass_df = pd.read_csv("data/Vehicle Class - All.csv")
        evsales_df_orig = pd.read_csv("data/ev_sales_by_makers_and_cat_15-24.csv")
        ev_market_place_df = pd.read_csv("data/EV Maker by Place.csv")
        operationIpc_df = pd.read_csv("data/OperationalPC.csv")
        evcat_df = pd.read_csv("data/ev_cat_01-24.csv")

        geojson_data = None
        # IMPORTANT: Check your GeoJSON filename. Corrected potential double extension.
        geojson_path = "data/india_with_disputed_boundaries.geojson.geojson"
        if os.path.exists(geojson_path):
             with open(geojson_path, "r") as f:
                geojson_data = json.load(f)
        elif os.path.exists("data/india_with_disputed_boundaries.geojson.geojson"):
             st.warning("Found GeoJSON file with double extension '.geojson.geojson'. Attempting to load.")
             with open("data/india_with_disputed_boundaries.geojson.geojson", "r") as f:
                geojson_data = json.load(f)
        else:
            raise FileNotFoundError(f"GeoJSON file not found at expected paths: {geojson_path} or data/india_with_disputed_boundaries.geojson.geojson")


    except FileNotFoundError as e:
        st.error(f"Error: A required data file was not found. Please check your `data/` directory. Missing file related to: {e}")
        st.info("Please ensure all 5 CSV files (Vehicle Class - All.csv, ev_sales_by_makers_and_cat_15-24.csv, EV Maker by Place.csv, OperationalPC.csv, ev_cat_01-24.csv) and your GeoJSON file (e.g., india_with_disputed_boundaries.geojson) are in the 'data' folder.")
        return None, None, None, None, None, None, None
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None, None, None, None, None, None, None

    # Data Cleaning and Preparation (Keep existing logic)
    vehicalclass_df["Total Registration"] = vehicalclass_df["Total Registration"].str.replace(",", "").astype(int)
    sales_year_columns = [col for col in evsales_df_orig.columns if col.isdigit() and len(col) == 4]
    evsales_melted_df = evsales_df_orig.melt(id_vars=["Cat", "Maker"],
                                             value_vars=sales_year_columns,
                                             var_name="Year", value_name="Sales")
    evsales_melted_df["Sales"] = pd.to_numeric(evsales_melted_df["Sales"], errors='coerce').fillna(0)
    evsales_melted_df["Year"] = evsales_melted_df["Year"].astype(str)

    evsales_df_with_growth = evsales_df_orig.copy()
    if sales_year_columns:
        earliest_year = min(sales_year_columns)
        latest_year = max(sales_year_columns)
        evsales_df_with_growth[f'{earliest_year}_numeric'] = pd.to_numeric(evsales_df_with_growth[earliest_year], errors='coerce').fillna(0)
        evsales_df_with_growth[f'{latest_year}_numeric'] = pd.to_numeric(evsales_df_with_growth[latest_year], errors='coerce').fillna(0)
        evsales_df_with_growth['Growth %'] = evsales_df_with_growth.apply(
            lambda row: ((row[f'{latest_year}_numeric'] - row[f'{earliest_year}_numeric']) / row[f'{earliest_year}_numeric']) * 100
            if row[f'{earliest_year}_numeric'] != 0 else pd.NA, axis=1)
        evsales_df_with_growth.loc[(evsales_df_with_growth[f'{earliest_year}_numeric'] == 0) & (evsales_df_with_growth[f'{latest_year}_numeric'] > 0), 'Growth %'] = 10000 # Placeholder for very high growth
        evsales_df_with_growth['Growth %'] = evsales_df_with_growth['Growth %'].fillna(0)

    ev_market_place_df['State'] = ev_market_place_df['State'].apply(normalize_state_name)
    operationIpc_df['State'] = operationIpc_df['State'].apply(normalize_state_name)
    operationIpc_df["No. of Operational PCS"] = pd.to_numeric(operationIpc_df["No. of Operational PCS"], errors='coerce').fillna(0)

    evcat_df["Date"] = pd.to_datetime(evcat_df["Date"], errors='coerce', dayfirst=True)
    evcat_df = evcat_df.dropna(subset=['Date'])
    for col in evcat_df.columns:
        if col != 'Date':
            evcat_df[col] = pd.to_numeric(evcat_df[col], errors='coerce').fillna(0)

    return vehicalclass_df, evsales_df_with_growth, evsales_melted_df, ev_market_place_df, operationIpc_df, evcat_df, geojson_data

# State Name Normalization (Crucial for GeoJSON mapping)
STATE_NAME_MAPPING = {
    "Andaman & Nicobar Islands": "Andaman and Nicobar Islands", "Arunanchal Pradesh": "Arunachal Pradesh",
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu",
    "NCT of Delhi": "Delhi", "Delhi": "Delhi", "Odisha": "Orissa", "Telengana": "Telangana",
    "Jammu & Kashmir": "Jammu and Kashmir", "Pondicherry" : "Puducherry",
    "Uttaranchal": "Uttarakhand" # Add more mappings as needed by comparing data states with GeoJSON states
}
def normalize_state_name(name):
    if pd.isna(name): return "Unknown"
    name_stripped = str(name).strip()
    return STATE_NAME_MAPPING.get(name_stripped, name_stripped)

# Load data
vehicalclass_df, evsales_df, evsales_melted_df, ev_market_place_df, operationIpc_df, evcat_df, india_geojson = load_data()

# Check if essential data loaded
if any(df is None for df in [vehicalclass_df, evsales_df, evsales_melted_df, ev_market_place_df, operationIpc_df, evcat_df]) or india_geojson is None:
    st.error("Essential data files could not be loaded. Dashboard cannot proceed.")
    # No background setting here, rely on static CSS
    st.stop()

# ---------- Sidebar Navigation ----------
st.sidebar.header("📊 Analysis Sections")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Geospatial Insights"

# Sidebar Buttons (using standard Streamlit buttons, styling applied via CSS)
if st.sidebar.button("🏠 Geospatial Insights"): st.session_state.app_mode = "Geospatial Insights"
if st.sidebar.button("📋 EV Market Status"): st.session_state.app_mode = "EV Market Status"
if st.sidebar.button("📈 EV Sales"): st.session_state.app_mode = "EV Sales"
if st.sidebar.button("🚗 EV Category Trends"): st.session_state.app_mode = "EV Category Trends"

st.sidebar.markdown("---")
st.sidebar.info("Select a section above to explore different aspects of the Indian EV market.")

# ---------- Define Image Paths for Each Section ----------
# Ensure these PNG images exist in your data/ folder
IMAGE_PATHS = {
    "Geospatial Insights": "images/bg_home.png",
    "EV Market Status": "images/bg_glance.png",
    "EV Sales": "images/bg_sales.png",
    "EV Category Trends": "images/bg_category.png"
}
DEFAULT_IMAGE = "images/bg_home.png" # Fallback image


# ---------- Header Section with Dynamic Image ----------
header_col_main, header_col_image = st.columns([0.7, 0.3]) # Adjust ratio as needed (e.g., 3:1)

with header_col_main:
    st.title("🚗 India EV Insights: Sales, Infrastructure & Trends")
    st.markdown("---") # Separator below title/subtitle

    # ---------- Key Performance Indicators (KPIs) - Shown on all pages ----------
    st.header("🚀 Key Insights")
    try:
        total_registrations_all_classes = vehicalclass_df["Total Registration"].sum()
        total_sales_all_time = evsales_melted_df["Sales"].sum()
        latest_year_in_sales = ""
        if not evsales_melted_df["Year"].empty: latest_year_in_sales = evsales_melted_df["Year"].max()
        total_sales_latest_year = evsales_melted_df[evsales_melted_df["Year"] == latest_year_in_sales]["Sales"].sum() if latest_year_in_sales else 0
        total_pcs = operationIpc_df["No. of Operational PCS"].sum()

        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        kpi_col1.metric(label="Total EV Registrations (All Classes)", value=f"{total_registrations_all_classes:,.0f}")
        kpi_col2.metric(label=f"Total EV Sales ({latest_year_in_sales if latest_year_in_sales else 'N/A'})", value=f"{total_sales_latest_year:,.0f}")
        kpi_col3.metric(label="Operational Public Charging Stations", value=f"{total_pcs:,.0f}")
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")
        total_registrations_all_classes = 0
        total_sales_latest_year = 0
        total_pcs = 0
        # Display placeholders or zeros if calculation fails
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        kpi_col1.metric(label="Total EV Registrations (All Classes)", value="Error")
        kpi_col2.metric(label=f"Total EV Sales (Latest Year)", value="Error")
        kpi_col3.metric(label="Operational Public Charging Stations", value="Error")

with header_col_image:
    current_mode = st.session_state.app_mode
    image_path = IMAGE_PATHS.get(current_mode, DEFAULT_IMAGE) # Get image for current page, fallback to default

    # Add a container div with a class for potential specific CSS targeting
    st.markdown('<div class="header-image-container">', unsafe_allow_html=True)
    if os.path.exists(image_path):
        st.image(image_path, use_container_width='auto') # 'auto' scales based on column width
        # st.caption(f"Illustrative: {current_mode.split('(')[0].strip()}") # Optional caption
    else:
        st.warning(f"Header image not found: {image_path}")
        # Optionally display a placeholder if the image is missing
        # st.markdown("*(Image unavailable)*")
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---") # Separator below the entire header section


# ---------- Main Content Area - Dynamic based on Sidebar Navigation ----------

if st.session_state.app_mode == "Geospatial Insights":
    # --- Geospatial Section ---
    st.header("🗺️ Geospatial Insights") # Added header for clarity
    st.markdown("Analyze EV maker locations and charging infrastructure distribution.")

    # --- Explore EV Maker Locations ---
    st.subheader("📍 EV Maker Locations")
    st.caption("Geocodes 'Place' names from 'EV Maker by Place.csv'. Can be slow. Results depend on name clarity & service availability.")

    # Filters for geocoding
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        unique_makers_for_geo = ["All"] + sorted(ev_market_place_df['EV Maker'].unique().tolist())
        selected_maker_geo = st.selectbox("Select EV Maker", unique_makers_for_geo, key="maker_geo_select_home")
    with col_filter2:
        unique_places_for_geo = ["All"] + sorted(ev_market_place_df['Place'].dropna().unique().tolist())
        selected_place_geo = st.selectbox("Select Place", unique_places_for_geo, key="place_geo_select_home")
    with col_filter3:
        unique_states_for_geo = ["All"] + sorted([s for s in ev_market_place_df["State"].unique() if s not in ["Unknown", None]])
        selected_state_geo = st.selectbox("Select State", unique_states_for_geo, key="state_geo_select_home")

    # Filter data for geocoding
    locations_to_geocode = ev_market_place_df.copy()
    if selected_maker_geo != "All": locations_to_geocode = locations_to_geocode[locations_to_geocode['EV Maker'] == selected_maker_geo]
    if selected_place_geo != "All": locations_to_geocode = locations_to_geocode[locations_to_geocode['Place'] == selected_place_geo]
    if selected_state_geo != "All": locations_to_geocode = locations_to_geocode[locations_to_geocode['State'] == selected_state_geo]

    unique_places = locations_to_geocode[locations_to_geocode['Place'].notna()]['Place'].unique()
    limit_geocode = 30 # Limit API calls
    unique_places_to_process = unique_places[:limit_geocode] if len(unique_places) > limit_geocode else unique_places
    if len(unique_places) > limit_geocode: st.warning(f"Geocoding limited to the first {limit_geocode} unique places ({len(unique_places)} total found for filters). Refine filters for more specific results.")

    # Geocoding function (cached)
    @st.cache_data(ttl=3600*24) # Cache for 24 hours
    def geocode_places(places_tuple):
        geolocator = Nominatim(user_agent=f"ev_dashboard_streamlit_map_{int(time.time())}", timeout=10)
        coords = {}
        progress_bar_geo = st.progress(0)
        status_text_geo = st.empty()
        total_places = len(places_tuple)
        status_text_geo.text(f"Geocoding {total_places} unique places...")

        for idx, place in enumerate(places_tuple):
            try:
                location = geolocator.geocode(f"{place}, India")
                time.sleep(0.4) # Increased delay to be respectful of Nominatim's usage policy
                if location: coords[place] = (location.latitude, location.longitude)
                else: coords[place] = (None, None)
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                # print(f"Geocoding service error for {place}: {e}") # Server-side log
                coords[place] = (None, None) # Mark as failed
                time.sleep(1) # Longer sleep on error
            except Exception as e:
                # print(f"Unexpected geocoding error for {place}: {e}") # Server-side log
                coords[place] = (None, None) # Mark as failed
            finally:
                 # Update progress (inside the loop)
                 progress = (idx + 1) / total_places if total_places > 0 else 1
                 try: # Handle potential UI element removal if user navigates away
                     progress_bar_geo.progress(progress)
                 except Exception:
                     pass # Ignore if progress bar no longer exists

        status_text_geo.text("Geocoding complete.")
        time.sleep(1) # Keep "complete" message visible briefly
        status_text_geo.empty()
        progress_bar_geo.empty()
        return coords

    # Execute geocoding and display map
    if len(unique_places_to_process) > 0:
        geocoded_coordinates = geocode_places(tuple(unique_places_to_process)) # Pass tuple for caching

        locations_to_geocode['Coordinates'] = locations_to_geocode['Place'].map(geocoded_coordinates)
        # Split coordinates into Lat/Lon columns
        locations_to_geocode[['Latitude', 'Longitude']] = pd.DataFrame(
            locations_to_geocode['Coordinates'].apply(lambda x: x if isinstance(x, tuple) else (None, None)).tolist(),
            index=locations_to_geocode.index
        )
        plot_data_geocoded = locations_to_geocode.dropna(subset=['Latitude', 'Longitude'])

        if not plot_data_geocoded.empty:
            fig_scatter_map = px.scatter_mapbox(plot_data_geocoded, lat="Latitude", lon="Longitude",
                                                hover_name="EV Maker", hover_data=["Place", "State"], color="EV Maker",
                                                size_max=20, zoom=3.9, center={"lat": 20.5937, "lon": 78.9629},
                                                mapbox_style="carto-positron", title="EV Maker Locations (Geocoded)")
            fig_scatter_map.update_traces(marker=dict(size=10)) # Uniform marker size
            fig_scatter_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, legend_title_text='EV Maker')
            st.plotly_chart(fig_scatter_map, use_container_width=True)

            with st.expander("View Geocoded Maker Data & Download"):
                st.dataframe(plot_data_geocoded[['EV Maker', 'Place', 'State', 'Latitude', 'Longitude']].reset_index(drop=True))
                st.download_button("Download Geocoded Data",
                                   plot_data_geocoded[['EV Maker', 'Place', 'State', 'Latitude', 'Longitude']].to_csv(index=False).encode('utf-8'),
                                   "geocoded_maker_locations.csv", "text/csv", key="geo_maker_data_csv")
        else:
            st.warning("Could not geocode any locations for the current selection, or no valid coordinates were returned.")
    else:
        st.info("No 'Place' data available to geocode based on the current filter selection.")

    st.markdown("---") # Separator

    # --- Choropleth Map for Charging Stations ---
    # st.subheader("⚡ Public Charging Stations (PCS) by State")
    # pcs_by_state = operationIpc_df.groupby("State")["No. of Operational PCS"].sum().reset_index()
    # # Ensure GeoJSON state names match pcs_by_state['State'] after normalization
    # fig_choropleth_pcs = px.choropleth_mapbox(pcs_by_state,
    #                                         geojson=india_geojson,
    #                                         locations="State",
    #                                         featureidkey="properties.NAME_1", # Key in GeoJSON matching state names
    #                                         color="No. of Operational PCS",
    #                                         color_continuous_scale="Viridis",
    #                                         mapbox_style="carto-positron",
    #                                         zoom=3.9, center={"lat": 20.5937, "lon": 78.9629},
    #                                         opacity=0.6,
    #                                         hover_name="State",
    #                                         hover_data={"No. of Operational PCS": True},
    #                                         title="Operational Public Charging Stations Density")
    # fig_choropleth_pcs.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, coloraxis_colorbar=dict(title="PCS Count"))
    # st.plotly_chart(fig_choropleth_pcs, use_container_width=True)

    # with st.expander("View Charging Station Data by State & Download"):
    #     st.dataframe(pcs_by_state.sort_values("No. of Operational PCS", ascending=False).reset_index(drop=True))
    #     st.download_button("Download PCS Data", pcs_by_state.to_csv(index=False).encode('utf-8'),
    #                        "operational_pcs_by_state.csv", "text/csv", key="pcs_state_data_csv")




    # Load India GeoJSON
    url = "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States"
    try:
        gdf = gpd.read_file(url)
        gdf["geometry"] = gdf.to_crs(gdf.estimate_utm_crs()).simplify(1000).to_crs(gdf.crs)
        gdf = gdf.rename(columns={"NAME_1": "State"})
        india_geojson = gdf.__geo_interface__
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}. Please ensure the URL is correct and the file is accessible.")
        india_geojson = None

    st.subheader("⚡ Public Charging Stations (PCS) by State")

    if india_geojson:
        pcs_by_state = operationIpc_df.groupby("State")["No. of Operational PCS"].sum().reset_index()

        fig = px.choropleth(
            pcs_by_state,
            geojson=india_geojson,
            locations="State",
            featureidkey="properties.State",
            color="No. of Operational PCS",
            color_continuous_scale="viridis",
            hover_name="State",
            hover_data=["No. of Operational PCS"],
            title="Operational Public Charging Stations Density",
            fitbounds="locations",
            scope="asia"
        )

        fig.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            coloraxis_colorbar=dict(title="PCS Count"),
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View Charging Station Data by State & Download"):
            st.dataframe(pcs_by_state.sort_values("No. of Operational PCS", ascending=False).reset_index(drop=True).style.background_gradient(cmap="viridis"))
            csv_data = pcs_by_state.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download PCS Data",
                data=csv_data,
                file_name="operational_pcs_by_state.csv",
                mime="text/csv",
                key="pcs_state_data_csv",
            )








elif st.session_state.app_mode == "EV Market Status":
    st.header("📋 At a Glance: Overall EV Market Status")
    # This section shows overall data, not affected by local filters here.
    st.subheader("Vehicle Class Distribution & Overall Registrations")
    if vehicalclass_df is not None and not vehicalclass_df.empty:
        col_vc1, col_vc2 = st.columns([0.6, 0.4])
        with col_vc1:
            fig_bar_vc = px.bar(vehicalclass_df, x="Vehicle Class", y="Total Registration",
                                color="Vehicle Class", title="EV Registrations by Vehicle Class", text_auto=True)
            fig_bar_vc.update_layout(showlegend=False, yaxis_title="Total Registrations")
            st.plotly_chart(fig_bar_vc, use_container_width=True)
        with col_vc2:
            fig_pie_vc = px.pie(vehicalclass_df, names="Vehicle Class", values="Total Registration",
                                title="Share of EV Registrations by Vehicle Class", hole=0.4)
            fig_pie_vc.update_traces(textposition='inside', textinfo='percent+label', pull=0.02)
            fig_pie_vc.update_layout(legend_title_text='Vehicle Class')
            st.plotly_chart(fig_pie_vc, use_container_width=True)

        with st.expander("View Vehicle Class Data & Download"):
            st.dataframe(vehicalclass_df)
            st.download_button("Download Vehicle Class CSV", vehicalclass_df.to_csv(index=False).encode('utf-8'), "glance_vehicle_class_data.csv", "text/csv", key="glance_vc_csv")
    else:
        st.warning("Vehicle class data is unavailable.")

    st.markdown("---")
    st.subheader("Overall EV Sales Trend (All Makers, All Categories)")
    if evsales_melted_df is not None and not evsales_melted_df.empty:
        overall_yearly_sales = evsales_melted_df.groupby("Year")["Sales"].sum().reset_index().sort_values("Year")
        fig_overall_sales_trend = px.line(overall_yearly_sales, x="Year", y="Sales", markers=True,
                                          title="Total EV Sales Growth Over Time (Aggregated)", text="Sales")
        fig_overall_sales_trend.update_traces(textposition="top center")
        fig_overall_sales_trend.update_layout(yaxis_title="Total Units Sold", xaxis_title="Year")
        st.plotly_chart(fig_overall_sales_trend, use_container_width=True)
        with st.expander("View Aggregated Yearly Sales Data"):
            st.dataframe(overall_yearly_sales)
    else:
        st.warning("Overall sales trend data is unavailable.")


elif st.session_state.app_mode == "EV Sales":
    st.header("📈 Sales Deep Dive")
    st.markdown("Analyze sales performance by year, manufacturer, and category.")

    st.markdown("#### Select Filters for Sales Analysis:")
    sd_col1, sd_col2 = st.columns(2)
    with sd_col1:
        sd_year_options = ["All"] + sorted(evsales_melted_df["Year"].unique().tolist(), reverse=True)
        sd_selected_year = st.selectbox("Year", sd_year_options, key="sd_year")
    with sd_col2:
        # Handle potential NaN or None makers if data issues exist
        valid_makers = evsales_melted_df["Maker"].dropna().unique()
        sd_maker_options = ["All"] + sorted(valid_makers.tolist())
        sd_selected_maker = st.selectbox("EV Maker", sd_maker_options, key="sd_maker")

    # Filter data based on selections
    sales_deep_dive_data = evsales_melted_df.copy()
    if sd_selected_year != "All": sales_deep_dive_data = sales_deep_dive_data[sales_deep_dive_data["Year"] == sd_selected_year]
    if sd_selected_maker != "All": sales_deep_dive_data = sales_deep_dive_data[sales_deep_dive_data["Maker"] == sd_selected_maker]

    section_title_suffix = f"({sd_selected_year if sd_selected_year != 'All' else 'All Years'}, {sd_selected_maker if sd_selected_maker != 'All' else 'All Makers'})"
    st.markdown(f"### Sales Insights for: {section_title_suffix}")

    if not sales_deep_dive_data.empty:
        col_mkt_share, col_top_makers = st.columns(2)
        with col_mkt_share:
            st.subheader(f"Market Share")
            market_share_data = sales_deep_dive_data.groupby("Maker")["Sales"].sum().reset_index()
            market_share_data = market_share_data[market_share_data["Sales"] > 0].sort_values("Sales", ascending=False)
            if not market_share_data.empty:
                # Combine small slices into 'Others' if too many makers
                num_makers = len(market_share_data)
                top_n_share = 9 # Show top 9 + Others
                if num_makers > top_n_share + 1:
                     market_share_data_plot = pd.concat([
                         market_share_data.head(top_n_share),
                         pd.DataFrame([{'Maker': 'Others', 'Sales': market_share_data.iloc[top_n_share:]['Sales'].sum()}])
                     ], ignore_index=True)
                else:
                     market_share_data_plot = market_share_data

                fig_market_share = px.pie(market_share_data_plot, names="Maker", values="Sales", hole=0.4,
                                          title=f"Top {len(market_share_data_plot)-1 if 'Others' in market_share_data_plot['Maker'].tolist() else len(market_share_data_plot)} Makers' Share {section_title_suffix}")
                fig_market_share.update_traces(textposition='outside', textinfo='percent+label', pull=0.03)
                fig_market_share.update_layout(legend_title_text='EV Maker', showlegend=True)
                st.plotly_chart(fig_market_share, use_container_width=True)
            else: st.info("No sales data for current filter to display market share.")

        with col_top_makers:
            st.subheader(f"Top Makers by Volume")
            top_makers_volume = sales_deep_dive_data.groupby("Maker")["Sales"].sum().nlargest(10).reset_index()
            if not top_makers_volume.empty:
                fig_top_makers_bar = px.bar(top_makers_volume, x="Sales", y="Maker", orientation='h',
                                            title=f"Top 10 Makers by Sales Volume {section_title_suffix}", text_auto=True)
                fig_top_makers_bar.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Units Sold", yaxis_title="EV Maker")
                st.plotly_chart(fig_top_makers_bar, use_container_width=True)
            else: st.info("No sales data for current filter to display top makers.")

        with st.expander("View Detailed Filtered Sales Data & Download"):
            st.dataframe(sales_deep_dive_data[['Year', 'Cat', 'Maker', 'Sales']].sort_values(by=['Year', 'Maker']).reset_index(drop=True))
            st.download_button("Download Filtered Sales CSV", sales_deep_dive_data.to_csv(index=False).encode('utf-8'), f"sales_deep_dive_{sd_selected_year}_{sd_selected_maker}.csv", "text/csv", key="sdd_filt_sales_csv")

        st.markdown("---")
        st.subheader(f"Sales by Vehicle Category {section_title_suffix}")
        sales_by_cat_data = sales_deep_dive_data.groupby("Cat")["Sales"].sum().reset_index()
        sales_by_cat_data = sales_by_cat_data[sales_by_cat_data['Sales'] > 0] # Filter out zero sales categories
        if not sales_by_cat_data.empty:
            fig_cat_sales_bar = px.bar(sales_by_cat_data, x="Cat", y="Sales", color="Cat",
                                       title=f"Sales Distribution by Category {section_title_suffix}", text_auto=".2s")
            fig_cat_sales_bar.update_layout(xaxis_title="Vehicle Category", yaxis_title="Units Sold")
            st.plotly_chart(fig_cat_sales_bar, use_container_width=True)
        else: st.info("No sales data for current filters to display by category.")

        st.markdown("---")
        st.subheader("Manufacturer Growth Insights (Across All Available Years)")
        st.caption(f"Calculated between earliest ({evsales_df.columns[2]} approx.) and latest ({evsales_df.columns[-2]} approx.) years in the source data. Growth % is shown; requires data for both start/end years.")

        if 'Growth %' in evsales_df.columns:
            # Use the evsales_df (which has growth calculated)
            growth_data_to_display = evsales_df[['Maker', 'Growth %']].dropna(subset=['Growth %'])
            # Filter out infinite or placeholder growth for better visualization, and zero growth
            growth_data_to_display = growth_data_to_display[ (growth_data_to_display['Growth %'] < 9999) & (growth_data_to_display['Growth %'] != 0) ]
            growth_data_to_display = growth_data_to_display.sort_values(by='Growth %', ascending=False)


            if sd_selected_maker != "All":
                growth_data_to_display_filtered = growth_data_to_display[growth_data_to_display['Maker'] == sd_selected_maker]
                chart_title_growth = f"Sales Growth (%) for {sd_selected_maker}"
            else:
                growth_data_to_display_filtered = growth_data_to_display.head(15) # Show top 15 overall growers
                chart_title_growth = f"Top 15 EV Manufacturers by Sales Growth (%)"

            if not growth_data_to_display_filtered.empty:
                fig_growth_dive = px.bar(growth_data_to_display_filtered, x='Growth %', y='Maker', orientation='h',
                                         color='Growth %', color_continuous_scale=px.colors.sequential.Tealgrn,
                                         title=chart_title_growth, text='Growth %')
                fig_growth_dive.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_growth_dive.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Growth (%)", yaxis_title="EV Maker", coloraxis_showscale=False)
                st.plotly_chart(fig_growth_dive, use_container_width=True)
            else: st.info(f"No valid growth data available for '{sd_selected_maker}' (requires sales in both earliest and latest years, excluding zero start year).")
        else: st.warning("Growth % calculation was not performed or is missing in the sales data.")

    else:
        st.warning(f"No sales data found for the selected filters: Year '{sd_selected_year}', Maker '{sd_selected_maker}'.")


elif st.session_state.app_mode == "EV Category Trends":
    st.header("🚗 EV Category Registration Trends Over Time")
    st.markdown("Explore daily registration trends across different EV categories.")

    if evcat_df is None or evcat_df.empty or 'Date' not in evcat_df.columns:
        st.warning("EV Category time series data (from ev_cat_01-24.csv) is not available or the 'Date' column is missing/invalid.")
    else:
        # Identify numeric category columns automatically
        category_cols_for_ts = [col for col in evcat_df.columns if col != 'Date' and pd.api.types.is_numeric_dtype(evcat_df[col])]

        if not category_cols_for_ts:
             st.warning("No numeric category columns found in the EV category data file.")
        else:
            # Ensure Date column is datetime
            evcat_df['Date'] = pd.to_datetime(evcat_df['Date'])
            date_min_cat = evcat_df["Date"].min()
            date_max_cat = evcat_df["Date"].max()

            st.subheader("Select Date Range and Category")
            trend_dt_col1, trend_dt_col2 = st.columns(2)
            with trend_dt_col1:
                start_date_trend_cat = st.date_input("Start Date", date_min_cat, min_value=date_min_cat, max_value=date_max_cat, key="trend_cat_start")
            with trend_dt_col2:
                end_date_trend_cat = st.date_input("End Date", date_max_cat, min_value=start_date_trend_cat, max_value=date_max_cat, key="trend_cat_end")

            # Filter data based on date range
            trend_data_filtered_cat = evcat_df[
                (evcat_df['Date'] >= pd.to_datetime(start_date_trend_cat)) &
                (evcat_df['Date'] <= pd.to_datetime(end_date_trend_cat))
            ].copy() # Use .copy() to avoid SettingWithCopyWarning if modifying later

            if trend_data_filtered_cat.empty:
                st.info("No data available for the selected date range.")
            else:
                # --- Heatmap ---
                st.subheader("Heatmap of Daily EV Registrations by Category")
                st.caption("Shows relative registration volume across categories over the selected period.")
                heatmap_data_ts_indexed = trend_data_filtered_cat.set_index('Date')

                if not heatmap_data_ts_indexed.empty and category_cols_for_ts:
                    # Consider resampling for long periods to make heatmap clearer (e.g., 'W' for weekly sum)
                    # Example: heatmap_data_resampled = heatmap_data_ts_indexed[category_cols_for_ts].resample('W').sum()
                    # If resampling, use heatmap_data_resampled below
                    # For now, using daily data:
                    fig_heatmap_ts = px.imshow(heatmap_data_ts_indexed[category_cols_for_ts].T, # Transpose for dates on x-axis
                                               labels=dict(x="Date", y="Vehicle Category", color="Registrations"),
                                               aspect="auto", color_continuous_scale="Plasma",
                                               title="Daily EV Registrations Heatmap")
                    fig_heatmap_ts.update_xaxes(type='date', tickformat="%Y-%m-%d") # Ensure correct date formatting
                    fig_heatmap_ts.update_layout(yaxis_title="EV Category")
                    st.plotly_chart(fig_heatmap_ts, use_container_width=True)
                else: st.info("Not enough data or no numeric category columns for the selected date range to display category heatmap.")

                st.markdown("---")
                # --- Line Chart for Specific Category ---
                st.subheader("Trend for Specific EV Category")
                selected_cat_for_trend = st.selectbox("Select EV Category:", category_cols_for_ts, key="cat_trend_select_page_local")

                if selected_cat_for_trend:
                    fig_cat_trend_line = px.line(trend_data_filtered_cat.sort_values(by="Date"),
                                                 x="Date", y=selected_cat_for_trend, markers=False, # Use markers=True for fewer points
                                                 title=f"Registration Trend for {selected_cat_for_trend}")
                    fig_cat_trend_line.update_layout(yaxis_title="Daily Registrations", xaxis_title="Date")
                    st.plotly_chart(fig_cat_trend_line, use_container_width=True)

                    with st.expander(f"View Data for {selected_cat_for_trend} ({start_date_trend_cat.strftime('%Y-%m-%d')} to {end_date_trend_cat.strftime('%Y-%m-%d')}) & Download"):
                        display_df_cat = trend_data_filtered_cat[['Date', selected_cat_for_trend]].sort_values('Date').reset_index(drop=True)
                        st.dataframe(display_df_cat)
                        st.download_button("Download Category Trend CSV",
                                           display_df_cat.to_csv(index=False).encode('utf-8'),
                                           f"{selected_cat_for_trend}_trend_{start_date_trend_cat.strftime('%Y%m%d')}_{end_date_trend_cat.strftime('%Y%m%d')}.csv",
                                           "text/csv", key="cat_trend_filt_csv")
                else:
                     st.info("Please select an EV category to view its trend.")

# ---------- Footer ----------
st.markdown("---")
st.caption(
    "📍 *Note: Data has been cleaned and standardized. Map accuracy depends on the quality of input data and geographic mapping.* \n\n "
    "🛠️ Developed by **Vignesh S**\n\n"
    '<a href="https://www.linkedin.com/in/vignesh-s-9b86a7243" target="_blank">Connect on LinkedIn</a>',
    unsafe_allow_html=True
)
