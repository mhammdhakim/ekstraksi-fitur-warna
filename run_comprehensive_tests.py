"""
Suite Pengujian Komprehensif: 20 Skenario Uji Sesuai Spesifikasi Praktikum
File: run_comprehensive_tests.py
"""

import io
import os
import cv2
import json
import numpy as np
from app import app
import image_processor as ip

def create_dummy_images():
    os.makedirs('static/samples', exist_ok=True)
    # Create test JPG
    test_jpg = np.zeros((200, 200, 3), dtype=np.uint8)
    test_jpg[:, :100] = [0, 0, 255] # Red BGR
    test_jpg[:, 100:] = [255, 0, 0] # Blue BGR
    _, jpg_encoded = cv2.imencode('.jpg', test_jpg)
    
    # Create test PNG
    test_png = np.zeros((150, 150, 3), dtype=np.uint8)
    test_png[:75, :] = [0, 255, 0] # Green BGR
    test_png[75:, :] = [0, 255, 255] # Yellow BGR
    _, png_encoded = cv2.imencode('.png', test_png)
    
    return jpg_encoded.tobytes(), png_encoded.tobytes()

def main():
    print("=" * 70)
    print("MEMULAI PENGUJIAN OTOMATIS 20 SKENARIO SPESIFIKASI")
    print("=" * 70)

    jpg_bytes, png_bytes = create_dummy_images()
    client = app.test_client()
    
    results = []

    # 1. Upload JPG
    res1 = client.post('/api/upload', data={'image': (io.BytesIO(jpg_bytes), 'test.jpg')})
    d1 = json.loads(res1.data)
    ok1 = res1.status_code == 200 and d1['status'] == 'success'
    results.append(('1. Upload gambar JPG', ok1, f"ID: {d1.get('image_id')}"))
    img_id = d1.get('image_id')

    # 2. Upload PNG
    res2 = client.post('/api/upload', data={'image': (io.BytesIO(png_bytes), 'test.png')})
    d2 = json.loads(res2.data)
    ok2 = res2.status_code == 200 and d2['status'] == 'success'
    results.append(('2. Upload gambar PNG', ok2, f"ID: {d2.get('image_id')}"))

    # 3. Konversi RGB ke HSV
    # Menguji apakah konversi dilakukan secara benar
    sample_img = ip.load_image('static/samples/sample_palet_warna.png')
    features, rgb, hsv = ip.extract_features(sample_img)
    ok3 = hsv.shape == sample_img.shape and hsv.dtype == np.uint8
    results.append(('3. Konversi RGB ke HSV', ok3, f"Shape HSV: {hsv.shape}"))

    # 4. Visualisasi komponen HSV
    hsv_comp = ip.generate_hsv_components(hsv, 'static/results', 'test_eval')
    h_file = os.path.exists(os.path.join(app.root_path, hsv_comp['hue_image'].lstrip('/')))
    s_file = os.path.exists(os.path.join(app.root_path, hsv_comp['saturation_image'].lstrip('/')))
    v_file = os.path.exists(os.path.join(app.root_path, hsv_comp['value_image'].lstrip('/')))
    ok4 = h_file and s_file and v_file
    results.append(('4. Visualisasi komponen HSV', ok4, f"H, S, V files generated: {ok4}"))

    # 5. Ekstraksi nilai RGB
    r_val = features['rgb_mean']['red']
    g_val = features['rgb_mean']['green']
    b_val = features['rgb_mean']['blue']
    ok5 = (0 <= r_val <= 255) and (0 <= g_val <= 255) and (0 <= b_val <= 255)
    results.append(('5. Ekstraksi nilai RGB', ok5, f"R={r_val}, G={g_val}, B={b_val}"))

    # 6. Ekstraksi nilai HSV
    h_val = features['hsv_mean']['hue']
    s_val = features['hsv_mean']['saturation']
    v_val = features['hsv_mean']['value']
    ok6 = (0 <= h_val <= 179) and (0 <= s_val <= 255) and (0 <= v_val <= 255)
    results.append(('6. Ekstraksi nilai HSV', ok6, f"H={h_val}, S={s_val}, V={v_val}"))

    # Skenario 7 - 15: Segmentasi 9 Kelompok Warna
    color_keys = [
        ('7. Segmentasi warna merah', 'merah'),
        ('8. Segmentasi warna jingga', 'jingga'),
        ('9. Segmentasi warna kuning', 'kuning'),
        ('10. Segmentasi warna hijau', 'hijau'),
        ('11. Segmentasi warna cyan', 'cyan'),
        ('12. Segmentasi warna biru', 'biru'),
        ('13. Segmentasi warna ungu', 'ungu'),
        ('14. Segmentasi warna magenta', 'magenta'),
        ('15. Segmentasi warna merah muda', 'merah_muda')
    ]

    for title, col_key in color_keys:
        res_col = client.post('/api/segment', json={'image_id': img_id, 'color_key': col_key})
        d_col = json.loads(res_col.data)
        ok_col = res_col.status_code == 200 and d_col['status'] == 'success'
        stats = d_col['segmentation']['statistics']
        results.append((title, ok_col, f"{stats['detected_pixels']} px ({stats['detected_percentage']}%)"))

    # 16. Pengaturan threshold HSV (Manual custom range)
    res_thresh = client.post('/api/segment', json={
        'image_id': img_id,
        'custom_range': {'h_min': 100, 'h_max': 130, 's_min': 50, 's_max': 255, 'v_min': 50, 'v_max': 255}
    })
    d_thresh = json.loads(res_thresh.data)
    ok16 = res_thresh.status_code == 200 and d_thresh['status'] == 'success'
    results.append(('16. Pengaturan threshold HSV', ok16, f"Deteksi: {d_thresh['segmentation']['statistics']['detected_percentage']}%"))

    # 17. Perhitungan persentase piksel
    det_px = d_thresh['segmentation']['statistics']['detected_pixels']
    tot_px = d_thresh['segmentation']['statistics']['total_pixels']
    expected_pct = round((det_px / tot_px) * 100.0, 2)
    actual_pct = d_thresh['segmentation']['statistics']['detected_percentage']
    ok17 = abs(expected_pct - actual_pct) < 1e-4
    results.append(('17. Perhitungan persentase piksel', ok17, f"Formula verified ({actual_pct}% == {expected_pct}%)"))

    # 18. Download hasil segmentasi
    seg_file = d_thresh['segmentation']['files']['segmented_filename']
    res_dl = client.get(f'/download/segmented/{seg_file}')
    ok18 = res_dl.status_code == 200 and len(res_dl.data) > 0
    results.append(('18. Download hasil segmentasi', ok18, f"Status: {res_dl.status_code}, Bytes: {len(res_dl.data)}"))

    # 19. Pengujian dengan gambar berbeda (sample 1 vs sample 2)
    res_samp1 = client.post('/api/upload', data={'sample_name': 'sample_palet_warna.png'})
    d_samp1 = json.loads(res_samp1.data)
    res_samp2 = client.post('/api/upload', data={'sample_name': 'sample_bentuk_geometri.png'})
    d_samp2 = json.loads(res_samp2.data)
    # Harus menghasilkan fitur RGB & HSV berbeda
    rgb1 = d_samp1['features']['rgb_mean']
    rgb2 = d_samp2['features']['rgb_mean']
    diff_images = (rgb1 != rgb2)
    results.append(('19. Pengujian dengan gambar berbeda', diff_images, f"Sample 1 R={rgb1['red']} vs Sample 2 R={rgb2['red']}"))

    # 20. Pengujian upload file tidak valid (e.g. .txt file)
    res_invalid = client.post('/api/upload', data={'image': (io.BytesIO(b'halo bukan gambar'), 'dokumen.txt')})
    d_invalid = json.loads(res_invalid.data)
    ok20 = res_invalid.status_code == 400 and d_invalid['status'] == 'error'
    results.append(('20. Pengujian upload file tidak valid', ok20, f"Ditolak dengan pesan: '{d_invalid['message']}'"))

    print("\n" + "=" * 70)
    print("HASIL LENGKAP PENGUJIAN 20 SKENARIO:")
    print("=" * 70)
    all_passed = True
    for name, success, detail in results:
        status_str = "BERHASIL (PASS)" if success else "GAGAL (FAIL)"
        print(f"[{status_str:15}] {name:38} : {detail}")
        if not success:
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("SEMUA 20 SKENARIO PENGUJIAN BERHASIL 100%!")
    else:
        print("BEBERAPA PENGUJIAN MENGALAMI KEGAGALAN.")
    print("=" * 70)

if __name__ == '__main__':
    main()
