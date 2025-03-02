#include <driver/i2s.h>
#include <arduinoFFT.h>

#define I2S_WS  15  // Wordselect
#define I2S_SCK 14  // Clock
#define I2S_SD  32  // DataIn

#define SAMPLES 1024 
#define SAMPLE_RATE 44100 //rată de esantioane

double vReal[SAMPLES];  
double vImag[SAMPLES];  

ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, SAMPLES, SAMPLE_RATE);

void setup() {
    Serial.begin(115200);

    // Configurare I2S
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 1024,
        .use_apll = false
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK,
        .ws_io_num = I2S_WS,
        .data_out_num = -1,
        .data_in_num = I2S_SD
    };

    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
}

void loop() {
    size_t bytesRead;
    int32_t samples[SAMPLES];

    // citire microfon
    i2s_read(I2S_NUM_0, &samples, sizeof(samples), &bytesRead, portMAX_DELAY);

    for (int i = 0; i < SAMPLES; i++) {
        vReal[i] = samples[i] / 2147483648.0;  // Normalizare 
        vImag[i] = 0;
    }

    // Aplicăm FFT
    FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD); //  Fereastră Hamming
    FFT.compute(FFT_FORWARD);                       // Fourier
    FFT.complexToMagnitude();                       // Magnitudine

    //frecvența dominantă
    double peakFrequency = FFT.majorPeak();
    Serial.println(peakFrequency);

    delay(1000);
}
