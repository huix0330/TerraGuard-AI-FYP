TerraGuard-AI-FYP
**xAI-Driven Community-Based Forest Fire Detection & Prediction System**

*Developed for Multimedia University (MMU) Final Year Project.*

👉 [**CLICK HERE TO LAUNCH THE LIVE WEB APP**](https://terraguard-ai-fyp.streamlit.app/intel_map) 👈

## 🚀 Project Overview
TerraGuard AI is an interactive, crowdsourced environmental monitoring dashboard. It allows community members to upload images of potential forest fires and uses a highly secure, Two-Gate Artificial Intelligence system to verify the threat, generate xAI heatmaps, and dispatch local authorities.

## ✨ Key Features
* **Two-Gate Security System:** Uses MobileNetV2 to filter out indoor/human images and prevent false alarms before scanning for fire.
* **Explainable AI (xAI):** Utilizes Grad-CAM heatmaps to provide visual transparency, showing exactly *where* the AI detects thermal anomalies.
* **Dynamic Geospatial Routing:** Automatically pulls regional emergency contact numbers (Balai Bomba) based on the user's selected district in Melaka.
* **Live Monitoring Map:** A real-time Folium geospatial map displaying active threat escalations and an automated community activity log.

## 🛠️ Tech Stack
* **Framework:** Streamlit (Python)
* **AI & Computer Vision:** TensorFlow, Keras (MobileNetV2), OpenCV
* **Geospatial & Data:** Folium, Pandas
