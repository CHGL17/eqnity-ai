import os
import librosa
import numpy as np
import tempfile
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from langchain.tools import tool
from typing import Optional

def extract_features(audio_path):
    """Extrae características de audio usando librosa."""
    y, sr = librosa.load(audio_path, sr=None)
    
    # Características básicas
    spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    tempo = float(librosa.feature.tempo(y=y, sr=sr).mean())
    rms = float(np.mean(librosa.feature.rms(y=y)))
    
    # Características adicionales
    spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    spectral_bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    
    # MFCCs (coeficientes cepstrales)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_means = [float(np.mean(mfcc)) for mfcc in mfccs]
    
    return {
        "spectral_centroid": spectral_centroid,
        "zero_crossing_rate": zero_crossing_rate,
        "tempo": tempo,
        "rms": rms,
        "spectral_rolloff": spectral_rolloff,
        "spectral_bandwidth": spectral_bandwidth,
        "mfcc_means": mfcc_means[:5]  # Solo los primeros 5 para simplicidad
    }

def analyze_audio_characteristics(features):
    """Analiza las características y genera recomendaciones."""
    recommendations = []
    
    # Análisis de brillo
    if features["spectral_centroid"] < 1000:
        recommendations.append("🔆 Audio oscuro - Considera realzar frecuencias agudas (3-8kHz)")
    elif features["spectral_centroid"] > 3000:
        recommendations.append("✨ Audio brillante - Podría beneficiarse de suavizar agudos")
    
    # Análisis de energía
    if features["rms"] < 0.01:
        recommendations.append("📢 Nivel bajo - Considera normalizar o aplicar compresión")
    elif features["rms"] > 0.3:
        recommendations.append("⚠️ Nivel alto - Riesgo de distorsión, considera reducir ganancia")
    
    # Análisis de tempo
    if features["tempo"] < 80:
        recommendations.append(f"🐌 Tempo lento ({features['tempo']:.1f} BPM) - Ideal para baladas")
    elif features["tempo"] > 140:
        recommendations.append(f"🏃 Tempo rápido ({features['tempo']:.1f} BPM) - Ideal para dance/rock")
    
    return recommendations

@tool
def analyze_uploaded_audio(audio_path: str) -> str:
    """
    Analiza un archivo de audio subido por el usuario y proporciona características detalladas.
    
    Args:
        audio_path: Ruta al archivo de audio subido
    """
    try:
        if not os.path.exists(audio_path):
            return f"Error: No se encontró el archivo de audio en {audio_path}"
        
        features = extract_features(audio_path)
        recommendations = analyze_audio_characteristics(features)
        
        report = f"""
📊 **Análisis de Audio Completo**

**Características Técnicas:**
- Centroide Espectral: {features['spectral_centroid']:.2f} Hz
- Tasa de Cruces por Cero: {features['zero_crossing_rate']:.4f}
- Tempo: {features['tempo']:.1f} BPM
- RMS (Energía): {features['rms']:.4f}
- Rolloff Espectral: {features['spectral_rolloff']:.2f} Hz
- Ancho de Banda Espectral: {features['spectral_bandwidth']:.2f} Hz

**Recomendaciones:**
{chr(10).join(recommendations)}

**Interpretación:**
- El audio tiene un carácter {'brillante' if features['spectral_centroid'] > 2000 else 'cálido'}
- Nivel de energía {'alto' if features['rms'] > 0.1 else 'bajo a medio'}
- Tempo {'lento' if features['tempo'] < 90 else 'medio' if features['tempo'] < 120 else 'rápido'}
        """
        
        return report.strip()
        
    except Exception as e:
        return f"Error al analizar el audio: {str(e)}"

@tool
def suggest_audio_processing(audio_path: str) -> str:
    """
    Sugiere procesamientos específicos basados en el análisis del audio.
    
    Args:
        audio_path: Ruta al archivo de audio
    """
    try:
        features = extract_features(audio_path)
        
        suggestions = []
        
        # Sugerencias de EQ
        if features["spectral_centroid"] < 1500:
            suggestions.append("🎛️ **EQ**: Realzar 2-4kHz para más presencia")
        if features["spectral_centroid"] > 3000:
            suggestions.append("🎛️ **EQ**: Suavizar 6-8kHz para reducir harshness")
        
        # Sugerencias de compresión
        if features["rms"] < 0.05:
            suggestions.append("🔧 **Compresión**: Ratio 3:1, ataque lento para más punch")
        
        # Sugerencias de reverb/delay
        if features["zero_crossing_rate"] > 0.1:
            suggestions.append("🌊 **Reverb**: Room pequeño para preservar claridad")
        else:
            suggestions.append("🌊 **Reverb**: Hall largo para más ambiente")
            
        return "**Sugerencias de Procesamiento:**\n" + "\n".join(suggestions)
        
    except Exception as e:
        return f"Error al generar sugerencias: {str(e)}"

def separate_audio_placeholder(audio_path: str, output_dir: str = "output_stems") -> str:
    """
    Placeholder para separación de instrumentos. 
    En el futuro se puede integrar con Spleeter o similar.
    """
    # Para implementar Spleeter más adelante:
    # from spleeter.separator import Separator
    # separator = Separator('spleeter:4stems')
    # separator.separate_to_file(audio_path, output_dir)
    
    return """
🎵 **Separación de Instrumentos** (Próximamente)

Esta función separará el audio en:
- 🎤 Voces
- 🥁 Batería  
- 🎸 Bajo
- 🎹 Otros instrumentos

Para implementar completamente, instala Spleeter:
`pip install spleeter tensorflow`

Por ahora, usa el análisis general para obtener información detallada del audio.
    """