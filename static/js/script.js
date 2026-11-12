/**
 * Aplikasi Ekstraksi Fitur Warna dan Segmentasi Citra Digital Menggunakan Metode HSV
 * File: static/js/script.js
 * Deskripsi: Logika interaksi antarmuka pengguna, pemanggilan API async (fetch),
 *            pengaturan slider threshold real-time, dan manipulasi DOM.
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // STATE APLIKASI
    // =========================================================================
    const state = {
        imageId: null,
        filename: null,
        activeColorKey: 'merah',
        activeColorName: 'Merah',
        colorPresets: {},
        isProcessing: false,
        debounceTimer: null,
        downloadFiles: {
            mask: null,
            segmented: null
        }
    };

    // Preset data mirror dari backend untuk penyesuaian instan
    const PRESET_DEFAULTS = {
        'merah': { h_min: 0, h_max: 10, s_min: 70, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue berada di awal dan akhir spektrum lingkaran (0-10 & 170-179).' },
        'jingga': { h_min: 11, h_max: 25, s_min: 70, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue berada di antara merah dan kuning (~20-50 derajat atau H: 11-25).' },
        'kuning': { h_min: 26, h_max: 35, s_min: 70, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue berada di sekitar 50-70 derajat spektrum warna (H: 26-35).' },
        'hijau': { h_min: 36, h_max: 85, s_min: 50, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue mencakup area luas spektrum hijau (~70-170 derajat atau H: 36-85).' },
        'cyan': { h_min: 86, h_max: 100, s_min: 50, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue peralihan antara hijau dan biru (~170-200 derajat atau H: 86-100).' },
        'biru': { h_min: 101, h_max: 130, s_min: 50, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue di spektrum biru dominan (~200-260 derajat atau H: 101-130).' },
        'ungu': { h_min: 131, h_max: 145, s_min: 50, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue peralihan biru ke magenta (~260-290 derajat atau H: 131-145).' },
        'magenta': { h_min: 146, h_max: 160, s_min: 50, s_max: 255, v_min: 50, v_max: 255, desc: 'Hue perpaduan merah-biru jenuh (~290-320 derajat atau H: 146-160).' },
        'merah_muda': { h_min: 161, h_max: 172, s_min: 30, s_max: 255, v_min: 100, v_max: 255, desc: 'Hue mendekati merah dengan saturasi lebih rendah/sedang (H: 161-172).' }
    };

    // =========================================================================
    // ELEMEN DOM
    // =========================================================================
    const dropzone = document.getElementById('dropzone');
    const imageInput = document.getElementById('imageInput');
    const btnChangeImage = document.getElementById('btnChangeImage');
    const alertBox = document.getElementById('alertBox');
    const alertMessage = document.getElementById('alertMessage');
    const systemStatusBadge = document.getElementById('systemStatusBadge');
    const systemStatusText = document.getElementById('systemStatusText');

    // Preview citra asli
    const originalPreviewImage = document.getElementById('originalPreviewImage');
    const previewPlaceholder = document.getElementById('previewPlaceholder');
    const imageMetadataBox = document.getElementById('imageMetadataBox');
    const metaFilename = document.getElementById('metaFilename');
    const metaDimensions = document.getElementById('metaDimensions');
    const metaTotalPixels = document.getElementById('metaTotalPixels');

    // Statistik RGB
    const meanRed = document.getElementById('meanRed');
    const meanGreen = document.getElementById('meanGreen');
    const meanBlue = document.getElementById('meanBlue');
    const barRed = document.getElementById('barRed');
    const barGreen = document.getElementById('barGreen');
    const barBlue = document.getElementById('barBlue');

    // Statistik HSV
    const meanHue = document.getElementById('meanHue');
    const meanSat = document.getElementById('meanSat');
    const meanVal = document.getElementById('meanVal');
    const barHue = document.getElementById('barHue');
    const barSat = document.getElementById('barSat');
    const barVal = document.getElementById('barVal');

    // Visualisasi Komponen H, S, V
    const imgComponentHue = document.getElementById('imgComponentHue');
    const imgComponentSat = document.getElementById('imgComponentSat');
    const imgComponentVal = document.getElementById('imgComponentVal');
    const placeholderHue = document.getElementById('placeholderHue');
    const placeholderSat = document.getElementById('placeholderSat');
    const placeholderVal = document.getElementById('placeholderVal');

    // Preset Buttons & Badges
    const presetButtons = document.querySelectorAll('.preset-btn');
    const activePresetBadge = document.getElementById('activePresetBadge');
    const presetDescriptionText = document.getElementById('presetDescriptionText');
    const btnResetThreshold = document.getElementById('btnResetThreshold');

    // Slider Inputs & Labels
    const sliderHMin = document.getElementById('sliderHMin');
    const sliderHMax = document.getElementById('sliderHMax');
    const sliderSMin = document.getElementById('sliderSMin');
    const sliderSMax = document.getElementById('sliderSMax');
    const sliderVMin = document.getElementById('sliderVMin');
    const sliderVMax = document.getElementById('sliderVMax');

    const valHMin = document.getElementById('valHMin');
    const valHMax = document.getElementById('valHMax');
    const valSMin = document.getElementById('valSMin');
    const valSMax = document.getElementById('valSMax');
    const valVMin = document.getElementById('valVMin');
    const valVMax = document.getElementById('valVMax');

    // Visualisasi 4 Kuadran Hasil
    const resultOriginalImage = document.getElementById('resultOriginalImage');
    const placeholderOriginal = document.getElementById('placeholderOriginal');
    const resultHueOverview = document.getElementById('resultHueOverview');
    const placeholderHueOverview = document.getElementById('placeholderHueOverview');
    const resultMaskImage = document.getElementById('resultMaskImage');
    const placeholderMask = document.getElementById('placeholderMask');
    const resultSegmentedImage = document.getElementById('resultSegmentedImage');
    const placeholderSegmented = document.getElementById('placeholderSegmented');

    // Laporan Analisis Kuantitatif
    const statImageName = document.getElementById('statImageName');
    const statDimensions = document.getElementById('statDimensions');
    const statTotalPixels = document.getElementById('statTotalPixels');
    const statActiveColor = document.getElementById('statActiveColor');
    const statDetectedPixels = document.getElementById('statDetectedPixels');
    const statPercentage = document.getElementById('statPercentage');
    const detectionMeterText = document.getElementById('detectionMeterText');
    const detectionMeterFill = document.getElementById('detectionMeterFill');

    // Download Buttons
    const btnDownloadSegmented = document.getElementById('btnDownloadSegmented');
    const btnDownloadMask = document.getElementById('btnDownloadMask');

    // =========================================================================
    // FUNGSI NOTIFIKASI & STATUS
    // =========================================================================
    function showAlert(msg) {
        alertMessage.textContent = msg;
        alertBox.classList.remove('d-none');
    }

    window.hideAlert = function() {
        alertBox.classList.add('d-none');
    };

    function setStatus(text, isBusy = false) {
        systemStatusText.textContent = text;
        if (isBusy) {
            systemStatusBadge.className = 'status-pill status-processing';
        } else {
            systemStatusBadge.className = 'status-pill status-ready';
        }
    }

    // =========================================================================
    // UPLOAD & SAMPLE HANDLERS
    // =========================================================================
    window.triggerNewUpload = function() {
        imageInput.click();
    };

    imageInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Drag and Drop
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // Sample buttons
    document.querySelectorAll('.btn-sample').forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleId = btn.getAttribute('data-sample');
            handleSampleSelection(sampleId);
        });
    });

    async function handleFileUpload(file) {
        hideAlert();
        const validExtensions = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validExtensions.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png)$/i)) {
            showAlert('Format berkas tidak didukung. Harap unggah berkas berekstensi .jpg, .jpeg, atau .png.');
            return;
        }

        const formData = new FormData();
        formData.append('image', file);

        await sendUploadRequest(formData);
    }

    async function handleSampleSelection(sampleName) {
        hideAlert();
        const formData = new FormData();
        formData.append('sample_name', sampleName);

        await sendUploadRequest(formData);
    }

    async function sendUploadRequest(formData) {
        setStatus('Mengunggah & menganalisis citra...', true);
        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (!res.ok || data.status === 'error') {
                throw new Error(data.message || 'Gagal memproses citra.');
            }

            // Update state
            state.imageId = data.image_id;
            state.filename = data.filename;
            state.activeColorKey = 'merah';
            state.activeColorName = 'Merah';

            // Update UI dengan hasil ekstraksi dan segmentasi awal
            renderImageMetadata(data.filename, data.features.dimensions);
            renderOriginalImage(data.original_image_url);
            renderFeatureStatistics(data.features);
            renderHsvComponents(data.hsv_components);
            renderSegmentationResult(data.segmentation);

            // Set preset awal ke merah
            setActivePreset('merah');

            setStatus(`Citra "${data.filename}" aktif`, false);
            btnChangeImage.classList.remove('d-none');
        } catch (err) {
            console.error(err);
            showAlert(err.message || 'Terjadi kesalahan teknis saat mengunggah citra.');
            setStatus('Gagal memproses gambar', false);
        }
    }

    // =========================================================================
    // RENDER FUNCTIONS (UI UPDATES)
    // =========================================================================
    function renderImageMetadata(filename, dims) {
        metaFilename.textContent = filename;
        metaDimensions.textContent = `${dims.width} × ${dims.height} px`;
        metaTotalPixels.textContent = dims.total_pixels.toLocaleString('id-ID') + ' px';
        imageMetadataBox.classList.remove('d-none');
    }

    function renderOriginalImage(url) {
        originalPreviewImage.src = url;
        originalPreviewImage.classList.remove('d-none');
        previewPlaceholder.classList.add('d-none');

        // Kuadran 1
        resultOriginalImage.src = url;
        resultOriginalImage.classList.remove('d-none');
        placeholderOriginal.classList.add('d-none');
    }

    function renderFeatureStatistics(features) {
        // RGB
        const r = features.rgb_mean.red;
        const g = features.rgb_mean.green;
        const b = features.rgb_mean.blue;

        meanRed.textContent = r.toFixed(2);
        meanGreen.textContent = g.toFixed(2);
        meanBlue.textContent = b.toFixed(2);

        barRed.style.width = `${Math.min(100, (r / 255) * 100)}%`;
        barGreen.style.width = `${Math.min(100, (g / 255) * 100)}%`;
        barBlue.style.width = `${Math.min(100, (b / 255) * 100)}%`;

        // HSV
        const h = features.hsv_mean.hue;
        const s = features.hsv_mean.saturation;
        const v = features.hsv_mean.value;

        meanHue.textContent = h.toFixed(2);
        meanSat.textContent = s.toFixed(2);
        meanVal.textContent = v.toFixed(2);

        barHue.style.width = `${Math.min(100, (h / 179) * 100)}%`;
        barSat.style.width = `${Math.min(100, (s / 255) * 100)}%`;
        barVal.style.width = `${Math.min(100, (v / 255) * 100)}%`;
    }

    function renderHsvComponents(components) {
        // Tampilkan 3 citra grayscale komponen
        imgComponentHue.src = components.hue_image + '?t=' + Date.now();
        imgComponentHue.classList.remove('d-none');
        placeholderHue.classList.add('d-none');

        imgComponentSat.src = components.saturation_image + '?t=' + Date.now();
        imgComponentSat.classList.remove('d-none');
        placeholderSat.classList.add('d-none');

        imgComponentVal.src = components.value_image + '?t=' + Date.now();
        imgComponentVal.classList.remove('d-none');
        placeholderVal.classList.add('d-none');

        // Kuadran 2 (Hue Overview)
        resultHueOverview.src = components.hue_image + '?t=' + Date.now();
        resultHueOverview.classList.remove('d-none');
        placeholderHueOverview.classList.add('d-none');
    }

    function renderSegmentationResult(seg) {
        // Update gambar Mask (Kuadran 3)
        resultMaskImage.src = seg.files.mask_image + '?t=' + Date.now();
        resultMaskImage.classList.remove('d-none');
        placeholderMask.classList.add('d-none');

        // Update gambar Segmented (Kuadran 4)
        resultSegmentedImage.src = seg.files.segmented_image + '?t=' + Date.now();
        resultSegmentedImage.classList.remove('d-none');
        placeholderSegmented.classList.add('d-none');

        // Update File unduhan
        state.downloadFiles.mask = seg.files.mask_filename;
        state.downloadFiles.segmented = seg.files.segmented_filename;
        btnDownloadMask.disabled = false;
        btnDownloadSegmented.disabled = false;

        // Update Laporan Kuantitatif
        statImageName.textContent = state.filename || '-';
        statDimensions.textContent = `${metaDimensions.textContent}`;
        statTotalPixels.textContent = seg.statistics.total_pixels.toLocaleString('id-ID') + ' px';
        statActiveColor.textContent = seg.color_info.name;
        statDetectedPixels.textContent = seg.statistics.detected_pixels.toLocaleString('id-ID') + ' px';
        statPercentage.textContent = seg.statistics.detected_percentage.toFixed(2) + '%';

        detectionMeterText.textContent = seg.statistics.detected_percentage.toFixed(2) + '%';
        detectionMeterFill.style.width = `${Math.min(100, seg.statistics.detected_percentage)}%`;

        // Update Slider jika params diberikan dari backend
        if (seg.slider_params) {
            updateSliderUI(seg.slider_params);
        }
    }

    function updateSliderUI(params) {
        sliderHMin.value = params.h_min;
        sliderHMax.value = params.h_max;
        sliderSMin.value = params.s_min;
        sliderSMax.value = params.s_max;
        sliderVMin.value = params.v_min;
        sliderVMax.value = params.v_max;

        valHMin.textContent = params.h_min;
        valHMax.textContent = params.h_max;
        valSMin.textContent = params.s_min;
        valSMax.textContent = params.s_max;
        valVMin.textContent = params.v_min;
        valVMax.textContent = params.v_max;
    }

    function setActivePreset(colorKey) {
        state.activeColorKey = colorKey;
        presetButtons.forEach(btn => {
            if (btn.getAttribute('data-color') === colorKey) {
                btn.classList.add('active');
                state.activeColorName = btn.getAttribute('data-name');
                activePresetBadge.textContent = `Pilihan: ${state.activeColorName}`;
            } else {
                btn.classList.remove('active');
            }
        });

        if (PRESET_DEFAULTS[colorKey]) {
            presetDescriptionText.textContent = PRESET_DEFAULTS[colorKey].desc;
            updateSliderUI(PRESET_DEFAULTS[colorKey]);
        }
    }

    // =========================================================================
    // INTERAKSI PRESET WARNA & SEGMENTASI DINAMIS
    // =========================================================================
    presetButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const colorKey = btn.getAttribute('data-color');
            if (!state.imageId) {
                showAlert('Harap unggah atau pilih citra digital terlebih dahulu.');
                return;
            }

            setActivePreset(colorKey);
            await triggerSegmentation({ color_key: colorKey });
        });
    });

    // Reset Threshold button
    btnResetThreshold.addEventListener('click', async () => {
        if (!state.imageId) return;
        const defaults = PRESET_DEFAULTS[state.activeColorKey] || PRESET_DEFAULTS['merah'];
        updateSliderUI(defaults);
        await triggerSegmentation({
            custom_range: {
                h_min: parseInt(defaults.h_min, 10),
                h_max: parseInt(defaults.h_max, 10),
                s_min: parseInt(defaults.s_min, 10),
                s_max: parseInt(defaults.s_max, 10),
                v_min: parseInt(defaults.v_min, 10),
                v_max: parseInt(defaults.v_max, 10)
            }
        });
    });

    // =========================================================================
    // SLIDER REAL-TIME EVENTS DENGAN DEBOUNCE
    // =========================================================================
    const sliders = [sliderHMin, sliderHMax, sliderSMin, sliderSMax, sliderVMin, sliderVMax];

    sliders.forEach(slider => {
        slider.addEventListener('input', () => {
            // Update label secara instan
            valHMin.textContent = sliderHMin.value;
            valHMax.textContent = sliderHMax.value;
            valSMin.textContent = sliderSMin.value;
            valSMax.textContent = sliderSMax.value;
            valVMin.textContent = sliderVMin.value;
            valVMax.textContent = sliderVMax.value;

            // Indikasi mode kustom jika slider digeser manual
            activePresetBadge.textContent = 'Mode: Kustom / Slider';
            presetButtons.forEach(b => b.classList.remove('active'));

            // Debounce request segmentasi agar ringan dan responsif
            clearTimeout(state.debounceTimer);
            state.debounceTimer = setTimeout(() => {
                if (!state.imageId) return;
                triggerSegmentation({
                    custom_range: {
                        h_min: parseInt(sliderHMin.value, 10),
                        h_max: parseInt(sliderHMax.value, 10),
                        s_min: parseInt(sliderSMin.value, 10),
                        s_max: parseInt(sliderSMax.value, 10),
                        v_min: parseInt(sliderVMin.value, 10),
                        v_max: parseInt(sliderVMax.value, 10)
                    }
                });
            }, 80);
        });
    });

    async function triggerSegmentation(payload) {
        if (!state.imageId || state.isProcessing) return;

        state.isProcessing = true;
        setStatus('Memproses segmentasi warna...', true);

        try {
            const bodyData = Object.assign({ image_id: state.imageId }, payload);
            const res = await fetch('/api/segment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bodyData)
            });

            const data = await res.json();
            if (!res.ok || data.status === 'error') {
                throw new Error(data.message || 'Gagal melakukan segmentasi.');
            }

            renderSegmentationResult(data.segmentation);
            setStatus(`Citra "${state.filename}" aktif`, false);
        } catch (err) {
            console.error(err);
            showAlert(err.message || 'Terjadi kesalahan saat memproses segmentasi.');
            setStatus('Gagal segmentasi', false);
        } finally {
            state.isProcessing = false;
        }
    }

    // =========================================================================
    // DOWNLOAD HANDLERS
    // =========================================================================
    btnDownloadSegmented.addEventListener('click', () => {
        if (!state.downloadFiles.segmented) return;
        window.location.href = `/download/segmented/${state.downloadFiles.segmented}`;
    });

    btnDownloadMask.addEventListener('click', () => {
        if (!state.downloadFiles.mask) return;
        window.location.href = `/download/mask/${state.downloadFiles.mask}`;
    });

    // =========================================================================
    // SIDEBAR NAVIGATION & SCROLLSPY
    // =========================================================================
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    const sections = document.querySelectorAll('.content-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            const targetEl = document.getElementById(targetId);
            if (targetEl) {
                targetEl.scrollIntoView({ behavior: 'smooth' });
                navItems.forEach(n => n.classList.remove('active'));
                item.classList.add('active');
            }
        });
    });

    window.addEventListener('scroll', () => {
        let currentSection = '';
        const scrollPosition = window.scrollY + 140;

        sections.forEach(sec => {
            const top = sec.offsetTop;
            const height = sec.offsetHeight;
            if (scrollPosition >= top && scrollPosition < top + height) {
                currentSection = sec.getAttribute('id');
            }
        });

        if (currentSection) {
            navItems.forEach(item => {
                if (item.getAttribute('data-target') === currentSection) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
    });

    // =========================================================================
    // INISIALISASI OTOMATIS DENGAN SAMPEL PERTAMA AGAR APLIKASI LANGSUNG AKTIF
    // =========================================================================
    const initialSampleBtn = document.querySelector('.btn-sample');
    if (initialSampleBtn) {
        initialSampleBtn.click();
    }
});
