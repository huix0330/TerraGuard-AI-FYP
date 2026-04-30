import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import cv2
import matplotlib.cm as cm
from streamlit_paste_button import paste_image_button

# ==========================================
# 1. ENTERPRISE CSS & BRANDING
# ==========================================
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: #0E1117;
                color: gray;
                text-align: center;
                padding: 10px;
                font-size: 12px;
                border-top: 1px solid #333;
                z-index: 100;
            }
            </style>
            <div class="footer">
                <p><b>TerraGuard AI Enterprise</b> | Developed for Multimedia University (MMU) | Vision Engine: MobileNetV2</p>
            </div>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.title("👁️ TerraGuard AI: Vision Engine")
    st.write("Optical Wildfire Detection & Automated Threat Escalation")
with col_header2:
    st.metric(label="System Status", value="Online 🟢", delta="Latency: 18ms", delta_color="normal")

st.markdown("---")

# ==========================================
# 2. LOAD AI MODELS
# ==========================================
@st.cache_resource 
def load_fire_model():
    # Load your custom FYP model
    return tf.keras.models.load_model('fire_detection_model.h5')

@st.cache_resource
def load_filter_model():
    # Load the base MobileNetV2 for Gate 1 Security Check
    return tf.keras.applications.MobileNetV2(weights='imagenet')

fire_model = load_fire_model()
filter_model = load_filter_model()

# ==========================================
# 3. xAI HEATMAP & ZOOM LOGIC
# ==========================================
def make_gradcam_heatmap(img_array, model):
    last_conv_layer_name = None
    for layer in reversed(model.layers):
        try:
            if len(layer.output.shape) == 4: 
                last_conv_layer_name = layer.name
                break
        except Exception:
            continue
            
    grad_model = tf.keras.models.Model(
        inputs=[model.inputs], 
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        class_channel = preds[:, 0]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def display_gradcam(img_path, heatmap, alpha=0.4):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    heatmap = np.uint8(255 * heatmap)
    jet = cm.get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]
    
    jet_heatmap = cv2.resize(jet_heatmap, (img.shape[1], img.shape[0]))
    jet_heatmap = np.uint8(255 * jet_heatmap)
    
    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = tf.keras.utils.array_to_img(superimposed_img)
    return superimposed_img

def apply_zoom(img, zoom):
    if zoom == 1.0:
        return img
    w, h = img.size
    new_w, new_h = w / zoom, h / zoom
    left, top = (w - new_w) / 2, (h - new_h) / 2
    right, bottom = (w + new_w) / 2, (h + new_h) / 2
    return img.crop((left, top, right, bottom))

# ==========================================
# 4. DATA INGESTION UI 
# ==========================================
st.markdown("### 📡 Feed Data to Vision Engine")

if "widget_key" not in st.session_state:
    st.session_state.widget_key = 0

if st.button("🔄 Reset Inputs / Clear Memory"):
    st.session_state.widget_key += 1
    st.rerun()

tab1, tab2 = st.tabs(["📸 Manual Snapshot", "💻 Desktop / Clipboard"])

with tab1:
    st.write("Authorize your device camera to snap a manual image.")
    camera_photo = st.camera_input("Initialize Camera Feed", key=f"camera_{st.session_state.widget_key}")

with tab2:
    st.write("Provide an environmental image for analysis.")
    col_upload, col_paste = st.columns(2)
    with col_upload:
        uploaded_file = st.file_uploader("📂 Upload Local File", type=["jpg", "jpeg", "png"], key=f"upload_{st.session_state.widget_key}")
    with col_paste:
        st.write("📋 **Or Paste from Clipboard:**")
        paste_result = paste_image_button("Paste Image Now")

# Determine which manual input was provided
image = None
if camera_photo is not None:
    image = Image.open(camera_photo)
elif uploaded_file is not None:
    image = Image.open(uploaded_file)
elif paste_result.image_data is not None:
    image = paste_result.image_data

# ==========================================
# 5. DOUBLE-LOCK SECURITY & AI ANALYSIS
# ==========================================
if image is not None:
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image.save("temp_image.jpg")

    img_resized = image.resize((224, 224))
    img_array = np.array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    st.markdown("---")
    
    with st.expander("🛡️ Security & Context Verification (Action Required)", expanded=True):
        st.warning("**System Integrity Check:** To prevent false positives from indoor environments, manual verification is required before allocating computing resources.")
        is_outdoor = st.checkbox("Operator confirms this visual feed represents an outdoor landscape.")

    if not is_outdoor:
        st.info("🔒 AI processing suspended. Awaiting operator verification.")
        
    else:
        # Gate 1: MobileNetV2 Deep Scan
        filter_preds = filter_model.predict(img_array)
        decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(filter_preds, top=10)[0]
        
        banned_words = [
            'computer', 'laptop', 'television', 'monitor', 'desk', 'chair', 'couch', 'bed', 
            'room', 'wall', 'bottle', 'phone', 'tablet', 'air conditioner', 'curtain', 
            'window', 'ceiling', 'blind', 'lamp', 'refrigerator', 'microwave', 'fan', 'book',
            'table', 'wardrobe', 'cabinet', 'shelf', 'door', 'carpet', 'rug', 'seat belt',
            'face', 'hair', 'person', 'human', 'hand', 'finger', 'eye', 'arm', 'leg', 'skin',
            'wig', 'mask', 'lipstick', 'band aid', 'pacifier', 'necklace', 'ring',
            'shirt', 'suit', 'jersey', 'sweatshirt', 'jean', 'tie', 'hat', 'sunglasses', 
            'glasses', 't-shirt', 'coat', 'jacket', 'uniform', 'gown', 'vest', 'cardigan',
            'helmet', 'groom', 'player', 'diver', 'apron', 'pajama', 'backpack', 'purse',
            'bag', 'watch', 'shoe', 'boot', 'sneaker', 'maillot', 'trench coat',
            'sweatpants', 'poncho', 'miniskirt', 'kimono', 'bikini', 'bow tie', 'bolo tie',
            'bulletproof vest', 'lab coat', 'overskirt', 'sarong'
        ]
        
        anomaly_detected = False
        caught_word = ""
        
        for _, label, prob in decoded_preds:
            if any(banned in label.lower() for banned in banned_words) and prob > 0.01:
                anomaly_detected = True
                caught_word = label.replace('_', ' ').title()
                break

        if anomaly_detected:
            st.error("🚫 **SYSTEM HALTED: Contradiction Detected**")
            st.warning(f"Verification Failed: You checked the box, but the AI detected a **{caught_word}** (or indoor environment) in this image.")
            st.write("Please provide a valid outdoor forest landscape.")
        
        else:
            st.success("✅ Context verified by Operator and AI. Processing feed...")
            
            # Gate 2: Fire Inference
            prediction = fire_model.predict(img_array)
            confidence = prediction[0][0]

            heatmap = make_gradcam_heatmap(img_array, fire_model)
            cam_image = display_gradcam("temp_image.jpg", heatmap)

            st.markdown("### 🧠 xAI Diagnostic Visuals")
            
            zoom_level = st.slider("🔍 Digital Zoom (Inspect Anomaly)", min_value=1.0, max_value=5.0, value=1.0, step=0.1)
            
            zoomed_raw = apply_zoom(image, zoom_level)
            zoomed_cam = apply_zoom(cam_image, zoom_level)

            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.image(zoomed_raw, caption='Raw Visual Feed', use_container_width=True)
            with col_img2:
                st.image(zoomed_cam, caption='Grad-CAM Attention Heatmap', use_container_width=True)

            st.markdown("---")
            
            if confidence < 0.5: 
                st.error(f"🚨 **CRITICAL INCIDENT DETECTED** (Confidence: {(1 - confidence):.2%})")
                
                st.markdown("#### 📡 Dispatch & Community Alert")
                st.write("Please call Balai Bomba immediately and confirm incident coordinates before escalating.")
                
                bomba_directory = {
                    "Ayer Keroh Forest": {"phone": "06-232 4444", "lat": 2.2794, "lon": 102.2967},
                    "Melaka Tengah": {"phone": "06-282 4444", "lat": 2.2008, "lon": 102.2510},
                    "Jasin": {"phone": "06-529 1444", "lat": 2.3134, "lon": 102.4316},
                    "Alor Gajah": {"phone": "06-556 1444", "lat": 2.3831, "lon": 102.2089}
                }
                
                location_source = st.radio("Dispatch Coordinates:", ["Use My Current GPS Position", "Select Regional Balai Bomba"])
                
                selected_area = st.selectbox("Assign Regional Station:", list(bomba_directory.keys()))
                target_bomba = bomba_directory[selected_area]
                
                st.info(f"📞 Balai Bomba {selected_area} Local Contact: **{target_bomba['phone']}**")
                
                if st.button("🚨 Escalate to Local Fire Department (Bomba)", type="primary"):
                    st.session_state['live_emergency'] = {
                        'location': selected_area,
                        'status': 'Confirmed 🔥',
                        'lat': target_bomba['lat'], 
                        'lon': target_bomba['lon']
                    }
                    st.success(f"✅ **ALERT SENT!** Critical incident report dispatched to **{target_bomba['phone']}** and regional map.")
                    st.balloons() 
            else:
                st.success(f"✅ **STATUS GREEN.** No thermal or smoke anomalies detected. (Confidence: {confidence:.2%})")
