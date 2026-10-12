# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import io

app = FastAPI(title="API Peramalan ARIMA Ruma Rasa")

# Izinkan CORS agar frontend di Hostinger bisa memanggil API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict-arima")
async def predict_arima(
    menu_name: str = Form(...),
    forecast_steps: int = Form(1),
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Urutkan berdasarkan tanggal
        df['Tanggal_Periode'] = pd.to_datetime(df['Tanggal_Periode'])
        df = df.sort_values('Tanggal_Periode').reset_index(drop=True)
        
        series = df['Total_Qty_Terjual'].astype(float).values
        dates = df['Tanggal_Periode'].dt.strftime('%b %Y').tolist()
        
        # Fit Model ARIMA (0,1,2)
        model = ARIMA(series, order=(0, 1, 2))
        model_fit = model.fit()
        
        # Evaluasi In-Sample
        pred_in = model_fit.predict(start=1, end=len(series)-1)
        actual_in = series[1:]
        
        mae = float(mean_absolute_error(actual_in, pred_in))
        rmse = float(np.sqrt(mean_squared_error(actual_in, pred_in)))
        mape = float(mean_absolute_percentage_error(actual_in, pred_in) * 100)
        
        # Forecast Out-of-Sample (Jumlah Bulan yang Dipilih User)
        forecast_res = model_fit.get_forecast(steps=forecast_steps)
        forecast_vals = [int(round(float(x))) for x in forecast_res.predicted_mean]
        
        # Generate Tanggal Masa Depan
        last_date = df['Tanggal_Periode'].max()
        future_dates = [(last_date + pd.DateOffset(months=i+1)).strftime('%b %Y') for i in range(forecast_steps)]
        
        # Estimasi Omzet (Rata-rata Harga Item)
        avg_price = float(df['Total_Penjualan_Rp'].sum() / df['Total_Qty_Terjual'].sum()) if 'Total_Penjualan_Rp' in df.columns else 20600
        estimated_sales = [int(round(v * avg_price)) for v in forecast_vals]
        
        return {
            "status": "success",
            "menu_name": menu_name,
            "historical_dates": dates,
            "historical_actual": [int(x) for x in series],
            "historical_pred": [None] + [int(round(float(x))) for x in pred_in],
            "future_dates": future_dates,
            "forecast_values": forecast_vals,
            "estimated_sales_rp": estimated_sales,
            "metrics": {
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "mape": round(mape, 2)
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
