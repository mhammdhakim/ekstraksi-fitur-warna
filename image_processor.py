"""
Module: image_processor.py
Deskripsi: Modul pengolahan citra digital untuk ekstraksi fitur warna (RGB & HSV)
           serta segmentasi citra berbasis ruang warna HSV menggunakan OpenCV dan NumPy.
Referensi: https://pemrogramanmatlab.com/pengenalan-pola-citra-digital-menggunakan-matlab/pola-warna/
"""

import os
import cv2
import numpy as np

# ==============================================================================
# DEFINISI RENTANG WARNA HSV UNTUK OPENCV
# Skala HSV OpenCV:
#   - Hue (H)        : 0 - 179 (setengah dari derajat 0-360)
#   - Saturation (S) : 0 - 255 (intensitas / kejenuhan warna)
#   - Value (V)      : 0 - 255 (kecerahan)
# ==============================================================================

COLOR_PRESETS = {
    'merah': {
        'id': 'merah',
        'name': 'Merah',
        'hex': '#EF4444',
        'description': 'Hue berada di awal dan akhir spektrum lingkaran (0-10 & 170-179).',
        # Spektrum merah melingkar (wrap around 0/180) sehingga membutuhkan 2 rentang HSV
        'ranges': [
            (np.array([0, 70, 50], dtype=np.uint8), np.array([10, 255, 255], dtype=np.uint8)),
            (np.array([170, 70, 50], dtype=np.uint8), np.array([179, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 0, 'h_max': 10,
            's_min': 70, 's_max': 255,
            'v_min': 50, 'v_max': 255,
            'wrap_h_min': 170, 'wrap_h_max': 179
        }
    },
    'jingga': {
        'id': 'jingga',
        'name': 'Jingga',
        'hex': '#F97316',
        'description': 'Hue berada di antara merah dan kuning (~20-50 derajat atau H: 11-25).',
        'ranges': [
            (np.array([11, 70, 50], dtype=np.uint8), np.array([25, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 11, 'h_max': 25,
            's_min': 70, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'kuning': {
        'id': 'kuning',
        'name': 'Kuning',
        'hex': '#EAB308',
        'description': 'Hue berada di sekitar 50-70 derajat spektrum warna (H: 26-35).',
        'ranges': [
            (np.array([26, 70, 50], dtype=np.uint8), np.array([35, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 26, 'h_max': 35,
            's_min': 70, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'hijau': {
        'id': 'hijau',
        'name': 'Hijau',
        'hex': '#22C55E',
        'description': 'Hue mencakup area luas spektrum hijau (~70-170 derajat atau H: 36-85).',
        'ranges': [
            (np.array([36, 50, 50], dtype=np.uint8), np.array([85, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 36, 'h_max': 85,
            's_min': 50, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'cyan': {
        'id': 'cyan',
        'name': 'Cyan',
        'hex': '#06B6D4',
        'description': 'Hue peralihan antara hijau dan biru (~170-200 derajat atau H: 86-100).',
        'ranges': [
            (np.array([86, 50, 50], dtype=np.uint8), np.array([100, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 86, 'h_max': 100,
            's_min': 50, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'biru': {
        'id': 'biru',
        'name': 'Biru',
        'hex': '#3B82F6',
        'description': 'Hue di spektrum biru dominan (~200-260 derajat atau H: 101-130).',
        'ranges': [
            (np.array([101, 50, 50], dtype=np.uint8), np.array([130, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 101, 'h_max': 130,
            's_min': 50, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'ungu': {
        'id': 'ungu',
        'name': 'Ungu',
        'hex': '#8B5CF6',
        'description': 'Hue peralihan biru ke magenta (~260-290 derajat atau H: 131-145).',
        'ranges': [
            (np.array([131, 50, 50], dtype=np.uint8), np.array([145, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 131, 'h_max': 145,
            's_min': 50, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'magenta': {
        'id': 'magenta',
        'name': 'Magenta',
        'hex': '#D946EF',
        'description': 'Hue perpaduan merah-biru jenuh (~290-320 derajat atau H: 146-160).',
        'ranges': [
            (np.array([146, 50, 50], dtype=np.uint8), np.array([160, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 146, 'h_max': 160,
            's_min': 50, 's_max': 255,
            'v_min': 50, 'v_max': 255
        }
    },
    'merah_muda': {
        'id': 'merah_muda',
        'name': 'Merah Muda',
        'hex': '#F472B6',
        'description': 'Hue mendekati merah dengan saturasi lebih rendah/sedang (H: 161-172).',
        'ranges': [
            (np.array([161, 30, 100], dtype=np.uint8), np.array([172, 255, 255], dtype=np.uint8))
        ],
        'slider': {
            'h_min': 161, 'h_max': 172,
            's_min': 30, 's_max': 255,
            'v_min': 100, 'v_max': 255
        }
    }
}


def load_image(filepath):
    """
    Membaca gambar digital dari filesystem menggunakan OpenCV.
    Memeriksa kevalidan format dan data piksel.
    Mengembalikan BGR image numpy array.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File gambar tidak ditemukan: {filepath}")

    # Membaca gambar menggunakan imdecode agar aman terhadap karakter path non-ASCII
    with open(filepath, 'rb') as f:
        bytes_data = f.read()
    nparr = np.frombuffer(bytes_data, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None or img_bgr.size == 0:
        raise ValueError("Gambar rusak atau format tidak didukung oleh OpenCV.")

    return img_bgr


def extract_features(img_bgr):
    """
    Melakukan ekstraksi fitur warna citra:
    - Rata-rata nilai Red, Green, Blue (RGB)
    - Rata-rata nilai Hue, Saturation, Value (HSV)
    - Standar deviasi fitur warna
    - Metadata dimensi citra (tinggi, lebar, kanal, total piksel)

    Semua perhitungan dilakukan secara nyata menggunakan NumPy.
    """
    # OpenCV membaca dalam format BGR, konversi ke RGB dan HSV
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    height, width, channels = img_bgr.shape
    total_pixels = height * width

    # Ekstraksi kanal RGB
    r_channel = img_rgb[:, :, 0]
    g_channel = img_rgb[:, :, 1]
    b_channel = img_rgb[:, :, 2]

    # Ekstraksi kanal HSV
    h_channel = img_hsv[:, :, 0]
    s_channel = img_hsv[:, :, 1]
    v_channel = img_hsv[:, :, 2]

    features = {
        'dimensions': {
            'height': int(height),
            'width': int(width),
            'channels': int(channels),
            'total_pixels': int(total_pixels)
        },
        'rgb_mean': {
            'red': round(float(np.mean(r_channel)), 2),
            'green': round(float(np.mean(g_channel)), 2),
            'blue': round(float(np.mean(b_channel)), 2)
        },
        'rgb_std': {
            'red': round(float(np.std(r_channel)), 2),
            'green': round(float(np.std(g_channel)), 2),
            'blue': round(float(np.std(b_channel)), 2)
        },
        'hsv_mean': {
            'hue': round(float(np.mean(h_channel)), 2),
            'saturation': round(float(np.mean(s_channel)), 2),
            'value': round(float(np.mean(v_channel)), 2)
        },
        'hsv_std': {
            'hue': round(float(np.std(h_channel)), 2),
            'saturation': round(float(np.std(s_channel)), 2),
            'value': round(float(np.std(v_channel)), 2)
        }
    }

    return features, img_rgb, img_hsv


def generate_hsv_components(img_hsv, output_dir, prefix):
    """Alias untuk generate_hsv_component_images."""
    return generate_hsv_component_images(img_hsv, output_dir, prefix)


def generate_hsv_component_images(img_hsv, output_dir, prefix):
    """
    Menghasilkan visualisasi untuk 3 komponen HSV:
    1. Hue (H)        : Dinormalisasi dari 0-179 ke 0-255 skala grayscale untuk kontras optimal.
    2. Saturation (S) : 0-255 skala grayscale.
    3. Value (V)      : 0-255 skala grayscale.

    Menyimpan file hasil ke direktori output dan mengembalikan path relatifnya.
    """
    os.makedirs(output_dir, exist_ok=True)

    h_channel = img_hsv[:, :, 0]
    s_channel = img_hsv[:, :, 1]
    v_channel = img_hsv[:, :, 2]

    # Normalisasi Hue (0-179 -> 0-255) agar kontras corak warna terlihat jelas pada grayscale
    h_norm = (h_channel.astype(np.float32) * (255.0 / 179.0)).astype(np.uint8)

    h_filename = f"{prefix}_hue.png"
    s_filename = f"{prefix}_saturation.png"
    v_filename = f"{prefix}_value.png"

    cv2.imwrite(os.path.join(output_dir, h_filename), h_norm)
    cv2.imwrite(os.path.join(output_dir, s_filename), s_channel)
    cv2.imwrite(os.path.join(output_dir, v_filename), v_channel)

    return {
        'hue_image': f"/static/results/{h_filename}",
        'saturation_image': f"/static/results/{s_filename}",
        'value_image': f"/static/results/{v_filename}"
    }


def perform_segmentation(img_bgr, color_key=None, custom_range=None, output_dir='static/results', prefix='seg'):
    """
    Melakukan segmentasi warna pada citra BGR menggunakan ruang warna HSV:
    1. cv2.inRange() untuk thresholding biner.
    2. cv2.bitwise_and() untuk mengekstraksi piksel warna terpilih.
    3. Perhitungan jumlah dan persentase piksel terdeteksi.

    Mendukung 9 preset warna terdaftar maupun slider manual kustom.
    """
    os.makedirs(output_dir, exist_ok=True)

    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    height, width, _ = img_bgr.shape
    total_pixels = height * width

    mask = np.zeros((height, width), dtype=np.uint8)
    color_info = {
        'id': 'kustom',
        'name': 'Kustom / Manual',
        'description': 'Segmentasi menggunakan rentang slider manual HSV.'
    }
    applied_ranges = []

    if custom_range is not None:
        # Gunakan parameter rentang kustom dari slider
        h_min = int(custom_range.get('h_min', 0))
        h_max = int(custom_range.get('h_max', 179))
        s_min = int(custom_range.get('s_min', 0))
        s_max = int(custom_range.get('s_max', 255))
        v_min = int(custom_range.get('v_min', 0))
        v_max = int(custom_range.get('v_max', 255))

        # Jika h_min > h_max, tangani spektrum melingkar (wrap around 0-180, misal merah)
        if h_min > h_max:
            lower1 = np.array([h_min, s_min, v_min], dtype=np.uint8)
            upper1 = np.array([179, s_max, v_max], dtype=np.uint8)
            lower2 = np.array([0, s_min, v_min], dtype=np.uint8)
            upper2 = np.array([h_max, s_max, v_max], dtype=np.uint8)

            mask1 = cv2.inRange(img_hsv, lower1, upper1)
            mask2 = cv2.inRange(img_hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
            applied_ranges = [
                {'lower': [h_min, s_min, v_min], 'upper': [179, s_max, v_max]},
                {'lower': [0, s_min, v_min], 'upper': [h_max, s_max, v_max]}
            ]
        else:
            lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
            upper = np.array([h_max, s_max, v_max], dtype=np.uint8)
            mask = cv2.inRange(img_hsv, lower, upper)
            applied_ranges = [{'lower': [h_min, s_min, v_min], 'upper': [h_max, s_max, v_max]}]

        slider_params = {
            'h_min': h_min, 'h_max': h_max,
            's_min': s_min, 's_max': s_max,
            'v_min': v_min, 'v_max': v_max
        }
    elif color_key in COLOR_PRESETS:
        preset = COLOR_PRESETS[color_key]
        color_info = {
            'id': preset['id'],
            'name': preset['name'],
            'hex': preset['hex'],
            'description': preset['description']
        }
        slider_params = dict(preset['slider'])

        # Terapkan semua rentang HSV untuk preset yang dipilih
        for lower, upper in preset['ranges']:
            sub_mask = cv2.inRange(img_hsv, lower, upper)
            mask = cv2.bitwise_or(mask, sub_mask)
            applied_ranges.append({'lower': lower.tolist(), 'upper': upper.tolist()})
    else:
        raise ValueError(f"Warna tidak dikenali: {color_key}")

    # Menghasilkan citra hasil segmentasi menggunakan cv2.bitwise_and
    segmented_bgr = cv2.bitwise_and(img_bgr, img_bgr, mask=mask)

    # Perhitungan statistik piksel nyata
    detected_pixels = int(np.count_nonzero(mask > 0))
    detected_percentage = round((detected_pixels / total_pixels) * 100.0, 2) if total_pixels > 0 else 0.0

    # Simpan mask dan citra hasil segmentasi
    mask_filename = f"{prefix}_mask.png"
    segmented_filename = f"{prefix}_segmented.png"

    mask_path = os.path.join(output_dir, mask_filename)
    segmented_path = os.path.join(output_dir, segmented_filename)

    cv2.imwrite(mask_path, mask)
    cv2.imwrite(segmented_path, segmented_bgr)

    return {
        'color_info': color_info,
        'slider_params': slider_params,
        'applied_ranges': applied_ranges,
        'statistics': {
            'total_pixels': total_pixels,
            'detected_pixels': detected_pixels,
            'detected_percentage': detected_percentage
        },
        'files': {
            'mask_image': f"/static/results/{mask_filename}",
            'segmented_image': f"/static/results/{segmented_filename}",
            'mask_filename': mask_filename,
            'segmented_filename': segmented_filename
        }
    }
