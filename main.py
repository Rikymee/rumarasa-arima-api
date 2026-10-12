<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Restoran Ruma Rasa - Peramalan Penjualan ARIMA</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-amber-50 text-slate-800 font-sans min-h-screen">

  <!-- Header / Navbar -->
  <header class="bg-amber-900 text-amber-50 shadow-md py-4 px-6">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <h1 class="text-2xl font-bold tracking-wide"> Restoran Ruma Rasa</h1>
      <span class="text-sm bg-amber-800 px-3 py-1 rounded-full border border-amber-700">Sistem Peramalan ARIMA</span>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6">

    <!-- Form Input (Kiri) -->
    <section class="bg-white p-6 rounded-xl shadow-md border border-amber-100 md:col-span-1 h-fit">
      <h2 class="text-xl font-bold text-amber-900 mb-4 border-b pb-2">Input Data Penjualan</h2>
      <form id="arimaForm" class="space-y-4">
        <div>
          <label class="block text-sm font-semibold mb-1">Nama Menu / Kategori</label>
          <input type="text" id="menuName" required placeholder="Contoh: Total Penjualan Restoran" class="w-full border rounded-lg p-2.5 focus:ring-2 focus:ring-amber-600 outline-none">
        </div>

        <div>
          <label class="block text-sm font-semibold mb-1">File Excel / CSV Series</label>
          <input type="file" id="dataFile" accept=".xlsx, .xls, .csv" required class="w-full border rounded-lg p-2 text-sm focus:ring-2 focus:ring-amber-600 outline-none">
        </div>

        <div>
          <label class="block text-sm font-semibold mb-1">Proyeksi Bulan ke Depan</label>
          <select id="forecastSteps" class="w-full border rounded-lg p-2.5 focus:ring-2 focus:ring-amber-600 outline-none">
            <option value="1">1 Bulan Ke Depan (Default)</option>
            <option value="3">3 Bulan Ke Depan</option>
            <option value="6">6 Bulan Ke Depan</option>
            <option value="12">12 Bulan Ke Depan</option>
          </select>
        </div>

        <button type="submit" id="btnSubmit" class="w-full bg-amber-800 hover:bg-amber-900 text-white font-bold py-2.5 rounded-lg transition shadow">
          Hitung & Ramalkan ARIMA
        </button>
      </form>
    </section>

    <!-- Hasil & Visualisasi Grafik (Kanan) -->
    <section class="bg-white p-6 rounded-xl shadow-md border border-amber-100 md:col-span-2 space-y-6">
      
      <!-- Metrics Card -->
      <div class="grid grid-cols-3 gap-4 text-center">
        <div class="bg-amber-50 p-3 rounded-lg border border-amber-200">
          <p class="text-xs text-amber-800 font-semibold">MAPE (Akurasi)</p>
          <p id="mapeVal" class="text-xl font-extrabold text-amber-900">-</p>
        </div>
        <div class="bg-amber-50 p-3 rounded-lg border border-amber-200">
          <p class="text-xs text-amber-800 font-semibold">MAE Error</p>
          <p id="maeVal" class="text-xl font-extrabold text-amber-900">-</p>
        </div>
        <div class="bg-amber-50 p-3 rounded-lg border border-amber-200">
          <p class="text-xs text-amber-800 font-semibold">RMSE Error</p>
          <p id="rmseVal" class="text-xl font-extrabold text-amber-900">-</p>
        </div>
      </div>

      <!-- Chart Canvas -->
      <div>
        <h3 id="chartTitle" class="text-lg font-bold text-slate-800 mb-2">Grafik Penjualan & Hasil Peramalan</h3>
        <div class="relative h-72 w-full">
          <canvas id="arimaChart"></canvas>
        </div>
      </div>

      <!-- Forecast Summary Table -->
      <div>
        <h3 class="text-md font-bold text-slate-800 mb-2">Hasil Peramalan Periode Mendatang</h3>
        <table class="w-full text-sm text-left border">
          <thead class="bg-amber-800 text-white">
            <tr>
              <th class="p-2 border">Periode</th>
              <th class="p-2 border">Estimasi Qty Terjual</th>
              <th class="p-2 border">Estimasi Omzet (Rp)</th>
            </tr>
          </thead>
          <tbody id="forecastTable">
            <tr><td colspan="3" class="p-3 text-center text-gray-500">Belum ada data dihitung.</td></tr>
          </tbody>
        </table>
      </div>

    </section>
  </main>

  <script>
    const API_URL = "https://DOMAIN-API-KAMU.com/api/predict-arima"; // Ganti URL API FastAPI Kamu
    let chartInstance = null;

    document.getElementById('arimaForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('btnSubmit');
      btn.innerText = "Memproses ARIMA...";
      btn.disabled = true;

      const formData = new FormData();
      formData.append('menu_name', document.getElementById('menuName').value);
      formData.append('forecast_steps', document.getElementById('forecastSteps').value);
      formData.append('file', document.getElementById('dataFile').files[0]);

      try {
        const response = await fetch(API_URL, { method: 'POST', body: formData });
        const res = await response.json();

        if(res.status === 'success') {
          // Update Metrik
          document.getElementById('mapeVal').innerText = res.metrics.mape + "%";
          document.getElementById('maeVal').innerText = res.metrics.mae + " item";
          document.getElementById('rmseVal').innerText = res.metrics.rmse + " item";
          document.getElementById('chartTitle').innerText = "Grafik Penjualan ARIMA: " + res.menu_name;

          // Render Tabel Forecast
          let tableHtml = "";
          for(let i=0; i<res.future_dates.length; i++){
            tableHtml += `<tr class="border-b">
              <td class="p-2 font-semibold">${res.future_dates[i]}</td>
              <td class="p-2 text-amber-900 font-bold">${res.forecast_values[i].toLocaleString()} item</td>
              <td class="p-2 text-green-700 font-bold">Rp ${res.estimated_sales_rp[i].toLocaleString()}</td>
            </tr>`;
          }
          document.getElementById('forecastTable').innerHTML = tableHtml;

          // Render Chart.js
          renderChart(res);
        } else {
          alert("Gagal memproses data: " + res.message);
        }
      } catch (err) {
        alert("Terjadi kesalahan koneksi ke server API Python.");
      } finally {
        btn.innerText = "Hitung & Ramalkan ARIMA";
        btn.disabled = false;
      }
    });

    function renderChart(res) {
      const ctx = document.getElementById('arimaChart').getContext('2d');
      if (chartInstance) chartInstance.destroy();

      const labels = [...res.historical_dates, ...res.future_dates];
      const actualData = [...res.historical_actual, ...Array(res.future_dates.length).fill(null)];
      
      // Hubungkan garis titik terakhir historis ke titik pertama forecast
      const lastHistVal = res.historical_actual[res.historical_actual.length - 1];
      const forecastData = [...Array(res.historical_dates.length - 1).fill(null), lastHistVal, ...res.forecast_values];

      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Data Penjualan Historis',
              data: actualData,
              borderColor: '#92400e',
              backgroundColor: '#92400e',
              tension: 0.2
            },
            {
              label: 'Hasil Peramalan ARIMA',
              data: forecastData,
              borderColor: '#dc2626',
              borderDash: [5, 5],
              backgroundColor: '#dc2626',
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } }
        }
      });
    }
  </script>
</body>
</html>
