"""
Aplikasi Ekstraksi Fitur Warna dan Segmentasi Citra Digital Menggunakan Metode HSV
Framework: Flask
Pengolahan Citra: OpenCV (cv2) & NumPy
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, abort

import image_processor as ip

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hsv-color-segmentation-secret-key-2026')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(app.root_path, 'static', 'results')
app.config['SAMPLES_FOLDER'] = os.path.join(app.root_path, 'static', 'samples')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs(app.config['SAMPLES_FOLDER'], exist_ok=True)

# Cache runtime metadata gambar aktif berdasarkan image_id
ACTIVE_IMAGES = {}


def allowed_file(filename):
    """Memeriksa apakah ekstensi file termasuk dalam daftar yang diizinkan."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Halaman utama aplikasi."""
    samples = [
        {
            'id': 'sample_palet_warna.png',
            'title': 'Palet 9 Warna Lengkap',
            'desc': 'Gambar uji dengan 9 blok warna (Merah, Jingga, Kuning, Hijau, Cyan, Biru, Ungu, Magenta, Pink).'
        },
        {
            'id': 'sample_bentuk_geometri.png',
            'title': 'Komposisi Bentuk Geometri',
            'desc': 'Objek geometris berwarna-warni di atas latar belakang netral.'
        }
    ]
    return render_template('index.html', presets=ip.COLOR_PRESETS, samples=samples)


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Menyajikan file gambar asli yang diunggah pengguna."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    Endpoint untuk mengunggah gambar baru atau memilih contoh gambar.
    Melakukan:
    1. Validasi file & integritas gambar.
    2. Ekstraksi fitur rata-rata RGB dan HSV.
    3. Pembuatan visualisasi komponen H, S, V.
    4. Segmentasi warna awal (Merah).
    """
    try:
        sample_name = request.form.get('sample_name')
        image_id = str(uuid.uuid4())[:8]

        if sample_name:
            # Pengguna memilih gambar contoh
            safe_sample = secure_filename(sample_name)
            source_path = os.path.join(app.config['SAMPLES_FOLDER'], safe_sample)
            if not os.path.exists(source_path):
                return jsonify({'status': 'error', 'message': 'File sampel tidak ditemukan.'}), 404

            filename = f"sample_{image_id}_{safe_sample}"
            target_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                dst.write(src.read())
            original_display_name = safe_sample
        else:
            # Pengguna mengunggah file gambar
            if 'image' not in request.files:
                return jsonify({'status': 'error', 'message': 'Tidak ada berkas gambar yang dikirim.'}), 400

            file = request.files['image']
            if file.filename == '':
                return jsonify({'status': 'error', 'message': 'Nama berkas kosong.'}), 400

            if not allowed_file(file.filename):
                return jsonify({
                    'status': 'error',
                    'message': 'Format berkas tidak didukung. Harap unggah berkas gambar berformat JPG, JPEG, atau PNG.'
                }), 400

            original_display_name = secure_filename(file.filename)
            extension = original_display_name.rsplit('.', 1)[1].lower()
            filename = f"{image_id}_{original_display_name}"
            target_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(target_path)

        # Validasi integritas pembacaan gambar oleh OpenCV
        try:
            img_bgr = ip.load_image(target_path)
        except Exception as e:
            if os.path.exists(target_path):
                os.remove(target_path)
            return jsonify({'status': 'error', 'message': f'Gagal membaca citra digital: {str(e)}'}), 400

        # Ekstraksi fitur warna nyata (RGB & HSV)
        features, img_rgb, img_hsv = ip.extract_features(img_bgr)

        # Visualisasi komponen Hue, Saturation, Value
        hsv_components = ip.generate_hsv_components(
            img_hsv,
            output_dir=app.config['RESULTS_FOLDER'],
            prefix=f"{image_id}_comp"
        )

        # Segmentasi warna default (Merah) saat gambar pertama kali dimuat
        default_seg = ip.perform_segmentation(
            img_bgr,
            color_key='merah',
            output_dir=app.config['RESULTS_FOLDER'],
            prefix=f"{image_id}_merah"
        )

        # Simpan metadata gambar aktif
        ACTIVE_IMAGES[image_id] = {
            'filepath': target_path,
            'filename': filename,
            'original_name': original_display_name,
            'dimensions': features['dimensions']
        }

        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'filename': original_display_name,
            'original_image_url': f"/uploads/{filename}",
            'features': features,
            'hsv_components': hsv_components,
            'segmentation': default_seg
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan saat memproses gambar: {str(e)}'}), 500


@app.route('/api/segment', methods=['POST'])
def segment():
    """
    Endpoint untuk melakukan segmentasi warna secara dinamis:
    - Berdasarkan preset warna pilihan (merah, jingga, kuning, hijau, cyan, biru, ungu, magenta, merah muda).
    - Berdasarkan nilai slider HSV manual secara real-time.
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'status': 'error', 'message': 'Data permintaan tidak valid.'}), 400

        image_id = data.get('image_id')
        if not image_id or image_id not in ACTIVE_IMAGES:
            return jsonify({'status': 'error', 'message': 'Gambar tidak ditemukan atau sesi telah berakhir.'}), 404

        img_info = ACTIVE_IMAGES[image_id]
        img_bgr = ip.load_image(img_info['filepath'])

        color_key = data.get('color_key')
        custom_range = data.get('custom_range')

        prefix_tag = color_key if color_key else 'custom'
        prefix = f"{image_id}_{prefix_tag}"

        seg_result = ip.perform_segmentation(
            img_bgr,
            color_key=color_key,
            custom_range=custom_range,
            output_dir=app.config['RESULTS_FOLDER'],
            prefix=prefix
        )

        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'segmentation': seg_result
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Gagal melakukan segmentasi warna: {str(e)}'}), 500


@app.route('/download/<file_type>/<filename>')
def download_result(file_type, filename):
    """
    Endpoint unduh file hasil segmentasi atau mask biner dalam format PNG.
    """
    safe_name = secure_filename(filename)
    file_path = os.path.join(app.config['RESULTS_FOLDER'], safe_name)

    if not os.path.exists(file_path):
        abort(404, description="File hasil segmentasi tidak ditemukan.")

    download_name = f"hasil_{file_type}_{safe_name}"
    return send_from_directory(
        app.config['RESULTS_FOLDER'],
        safe_name,
        as_attachment=True,
        download_name=download_name
    )


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'status': 'error',
        'message': 'Ukuran berkas terlalu besar. Maksimal ukuran berkas yang diperbolehkan adalah 16 MB.'
    }), 413


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Endpoint tidak ditemukan.'}), 404
    return render_template('index.html', presets=ip.COLOR_PRESETS, samples=[]), 404


if __name__ == '__main__':
    # Berjalan di port 5000 pada localhost
    print("Memulai server Aplikasi Ekstraksi Fitur Warna & Segmentasi HSV...")
    app.run(host='127.0.0.1', port=5000, debug=True)
