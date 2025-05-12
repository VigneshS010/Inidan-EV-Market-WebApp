# 🚗 India EV Insights (2001 to 2024)

![Header Image](images/bg_home.png)

**A Streamlit-based interactive dashboard for analyzing Electric Vehicle (EV) sales, infrastructure, and trends across India.**

This project was developed for a hackathon to provide actionable insights into the Indian EV market, leveraging data visualization and geospatial analysis. The **India EV Insights Dashboard** empowers users to explore EV sales by manufacturers and categories, visualize EV maker locations, analyze public charging station distribution, and track registration trends over time. Built with Python, Streamlit, and Plotly, this dashboard is intuitive, data-driven, and visually engaging.

---

## 📌 Project Overview

The Indian EV market is rapidly growing, driven by government policies, consumer demand, and infrastructure development. This dashboard provides a comprehensive view of the EV ecosystem in India by analyzing:

- **EV Sales Trends**: Sales performance by year, manufacturer, and vehicle category, including market share and growth insights.
- **Geospatial Insights**: Locations of EV manufacturers and the distribution of public charging stations across Indian states.
- **Vehicle Registrations**: Distribution of EV registrations by vehicle class and daily registration trends by category.
- **Key Performance Indicators (KPIs)**: Total EV registrations, sales in the latest year, and operational charging stations.

The dashboard is designed for policymakers, industry stakeholders, and enthusiasts to make data-driven decisions and understand market dynamics.

---

## 🎯 Features

The dashboard is organized into four interactive sections, accessible via a sidebar navigation:

1. **🏠 Geospatial Insights**:
   - **EV Maker Locations**: Interactive map showing geocoded locations of EV manufacturers, filtered by maker, place, or state.
   - **Charging Stations Map**: Choropleth map visualizing the density of public charging stations by state, highlighting infrastructure distribution.

2. **📋 EV Market Status**:
   - Bar and pie charts displaying EV registrations by vehicle class.
   - Line chart showing aggregated EV sales trends over time across all manufacturers and categories.

3. **📈 EV Sales**:
   - Detailed sales analysis with filters for year and manufacturer.
   - Visualizations include:
     - Pie chart for market share of top manufacturers.
     - Bar chart for top 10 manufacturers by sales volume.
     - Bar chart for sales by vehicle category.
     - Growth analysis showing percentage sales growth for manufacturers between the earliest and latest years.

4. **🚗 EV Category Trends**:
   - Heatmap of daily EV registrations by category over a selected date range.
   - Line chart for registration trends of a specific EV category, with customizable date filters.

### Additional Features:
- **Interactive KPIs**: Displays total EV registrations, latest-year sales, and operational charging stations on every page.
- **Data Downloads**: Users can download filtered datasets as CSV files for further analysis.
- **Responsive Design**: Clean, professional UI with custom CSS styling for readability and aesthetics.
- **Geocoding**: Dynamic geocoding of EV maker locations using the Nominatim API, cached for performance.

---

## 📊 Data Sources

The dashboard leverages datasets from various sources, primarily sourced from Kaggle and processed for analysis:

1. **Vehicle Class - All.csv**: Total EV registrations by vehicle class.
2. **ev_sales_by_makers_and_cat_15-24.csv**: Yearly EV sales by manufacturer and category (2015–2024).
3. **EV Maker by Place.csv**: EV manufacturer names and their associated places/states for geocoding.
4. **OperationalPC.csv**: Number of operational public charging stations by state.
5. **ev_cat_01-24.csv**: Daily EV registration data by category (Jan 2024 onwards).
6. **india_with_disputed_boundaries.geojson**: GeoJSON file for rendering state-level choropleth maps.

**Note**: All datasets are cleaned and normalized (e.g., state names standardized) to ensure consistency with GeoJSON mappings and accurate visualizations.

---

## 🛠️ Technical Stack

- **Programming Language**: Python 3.8+
- **Web Framework**: Streamlit for building the interactive dashboard.
- **Data Processing**: Pandas for data manipulation, GeoPandas for geospatial data handling.
- **Visualization**: Plotly Express for interactive charts (bar, pie, line, heatmap, scatter, choropleth).
- **Geocoding**: Geopy with Nominatim API for converting place names to latitude/longitude coordinates.
- **Geospatial Mapping**: Mapbox integration via Plotly for scatter and choropleth maps.
- **Caching**: Streamlit's `@st.cache_data` for optimizing data loading and geocoding performance.
- **Styling**: Custom CSS for a polished, user-friendly interface.
- **Dependencies**: Listed in `requirements.txt` (e.g., `streamlit`, `pandas`, `plotly`, `geopy`, `geopandas`).

---

## 📂 Project Structure

```
project/
│
├── app.py                         # Main Streamlit application script
├── data/                          # Directory for datasets and GeoJSON
│   ├── Vehicle Class - All.csv
│   ├── ev_sales_by_makers_and_cat_15-24.csv
│   ├── EV Maker by Place.csv
│   ├── OperationalPC.csv
│   ├── ev_cat_01-24.csv
│   ├── india_with_disputed_boundaries.geojson
├── images/                        # Directory for header images
│   ├── bg_home.png
│   ├── bg_glance.png
│   ├── bg_sales.png
│   ├── bg_category.png
├── notebooks/                     # Directory for exploratory data analysis
│   ├── eda.ipynb
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
```

---

## 🚀 Getting Started

Follow these steps to set up and run the dashboard locally:

### Prerequisites
- Python 3.8 or higher
- Git
- A code editor (e.g., VS Code)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/india-ev-insights-dashboard.git
   cd india-ev-insights-dashboard
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Data Files**:
   - Ensure all CSV files and the GeoJSON file are present in the `data/` directory.
   - Header images should be in the `images/` directory.

5. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```
   - The dashboard will open in your default browser at `http://localhost:8501`.

### Notes
- **Geocoding**: The Nominatim API is used for geocoding EV maker locations. Ensure a stable internet connection, as geocoding is rate-limited (1 request per second). Results are cached for 24 hours to improve performance.
- **GeoJSON**: The provided GeoJSON file includes India's state boundaries. If using a different GeoJSON, ensure state names match the normalized names in the datasets (handled via `STATE_NAME_MAPPING` in the code).
- **Performance**: Large datasets or extensive geocoding may take time on the first load. Caching is implemented to minimize delays.

---

## 📈 Example Visualizations

Here are some sample outputs from the dashboard:

1. **Home Page Dashboard**:
   ![EV Maker Locations](images/pic1.png)

2. **EV Maker Locations Map**:
   ![EV Maker Locations](images/pic2.png)
   *Interactive scatter map showing geocoded EV manufacturer locations.*

3. **Charging Stations Choropleth**:
   ![Charging Stations](images/pic5.png)
   *Choropleth map of public charging stations by state.*

4. **Sales Market Share**:
   ![Market Share](images/pic4.png)
   *Pie chart showing the market share of top EV manufacturers.*

5. **Category Registration Heatmap**:
   ![Category Heatmap](images/pic3.png)
   *Heatmap of daily EV registrations by category.*

---

## 🔍 Key Challenges and Solutions

2. **State Name Mismatch**:
   - **Challenge**: Inconsistent state names between datasets and GeoJSON (e.g., "NCT of Delhi" vs. "Delhi").
   - **Solution**: Implemented a `STATE_NAME_MAPPING` dictionary to normalize state names during data preprocessing.

3. **Geocoding Limitations**:
   - **Challenge**: The Nominatim API has rate limits, and ambiguous place names (e.g., "Bangalore") can lead to inaccurate geocoding.
   - **Solution**: Cached geocoding results for 24 hours, limited geocoding to 30 unique places per filter, and added user feedback via progress bars and warnings.

4. **Data Volume**:
   - **Challenge**: Large datasets slowed down initial loading and visualization rendering.
   - **Solution**: Used Streamlit's caching (`@st.cache_data`) and optimized data processing with Pandas.

4. **UI Readability**:
   - **Challenge**: Default Streamlit styling was not visually appealing for a hackathon presentation.
   - **Solution**: Applied custom CSS for content blocks, sidebar, buttons, and headers, ensuring a professional and clean interface.

---

## 🌟 Why This Project Stands Out

- **Comprehensive Analysis**: Covers sales, infrastructure, and registration trends, providing a 360-degree view of the Indian EV market.
- **Interactive and User-Friendly**: Streamlit’s intuitive interface, combined with Plotly’s interactive charts, makes data exploration seamless.
- **Geospatial Innovation**: Dynamic geocoding and choropleth mapping add a spatial dimension to EV market insights.
- **Scalable Design**: Modular code structure and caching make it easy to extend with new datasets or features.
- **Hackathon-Ready**: Polished visualizations, clear documentation, and a focus on actionable insights make this project impactful for judges.

---

## 📝 Future Enhancements

- **Real-Time Data Integration**: Incorporate live APIs for EV sales or charging station data.
- **Advanced Geocoding**: Use paid geocoding services (e.g., Google Maps API) for higher accuracy and fewer rate limits.
- **Predictive Analytics**: Add machine learning models to forecast EV sales or adoption trends.
- **Custom Visual Themes**: Allow users to toggle between light/dark modes or customize chart colors.
- **Mobile Optimization**: Enhance responsiveness for mobile users.

---

## 🙌 Acknowledgments

- **Data Sources**: Kaggle for providing the core EV datasets.
- **Libraries**: Streamlit, Plotly, Pandas, Geopy, and GeoPandas for enabling rapid development and visualization.
- **Inspiration**: The growing importance of EVs in India’s sustainable future.

---

## 👤 Author

**Vignesh S**  
🔗 [LinkedIn](https://www.linkedin.com/in/vignesh-s-9b86a7243)  
📧 Email: vigneshvaran0101@gmail.com   

This project was built with passion for data science and sustainable mobility. Feedback and contributions are welcome!

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Happy Hacking! 🚗⚡*

---

### Notes for You:
1. **Screenshots**: To make the README more engaging, capture screenshots of key visualizations (e.g., maps, charts) from your running dashboard and place them in the `images/` folder. Update the `![Image]` links in the "Example Visualizations" section with the correct filenames.
2. **Email**: Replace `your.email@example.com` with your actual contact email.
3. **GitHub URL**: Update the `git clone` URL with your actual GitHub repository URL once you push the project.
4. **License File**: If you want to include a license, create a `LICENSE` file in your repository with the MIT License text (or your preferred license).
5. **Images**: Ensure all images referenced in `IMAGE_PATHS` (`bg_home.png`, etc.) are in the `images/` folder. If you don’t have them, remove the header image section or use placeholders.
6. **GeoJSON URL**: The code references a GitHub URL for the GeoJSON file. Ensure it’s accessible, or revert to using the local `india_with_disputed_boundaries.geojson` file and update the README accordingly.

This README is designed to impress hackathon judges by clearly explaining the project’s purpose, technical details, and value while being visually structured and professional. Let me know if you need further tweaks or additional sections!
