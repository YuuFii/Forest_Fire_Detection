# **Wireless Sensor Network Deployment for Detection Forest Fire**

## Desain Sistem

### **Alur Komunikasi Sistem**
![mermaid-diagram-2025-06-16-114100](https://github.com/user-attachments/assets/64c317a1-71cf-47df-9fbe-1dfe3b0b2341)


**✅ HOW (BAGAIMANA SISTEM BEKERJA)**

Diagram komunikasi diatas menggambarkan alur kerja sistem deteksi kebakaran hutan yang terdistribusi mulai dari sensor hingga notifikasi kepada petugas. 
Proses dimulai dari sensor node yang secara berkala membaca data lingkungan seperti suhu, kelembaban, asap, dan PM2.5 setiap detik. 
Data ini dianalisis secara lokal di perangkat sensor. Jika terdeteksi kondisi anomali yang mengindikasikan adanya potensi kebakaran, 
maka sensor akan mengirimkan data lengkap ke topik MQTT tertentu. Nmaun jika tidak, hanya heartbeat yang dikirim sebagai sinyal bahwa sensor aktif dan berjalan normal. 
Data yang dikirim kemudian akan diteruskan oleh Edge Gateway yang telah melakukan subscribe pada topik sensor. Di tahap ini, edge gateway akan menjalankan proses filtering dan agregasi data.
Jika edge mendeteksi indikasi kebakaran lokal, maka akan segera mengirimkan peringatan dalam format JSON ke server. Sebaliknya, jika tidak ada kejadian penting, maka data agregat akan mengirimkan hearth beat setiap 30 detik ke server 
Hasil dari analisis ini kemudian disajikan melalui monitoring dashboard dalam bentuk visualisasi peta panas. 

**🔍 WHY (MENGAPA DIBANGUN DENGAN ARSITEKTUR INI)**
1. Mengapa Mengirim Heartbeat dan Data Lengkap Secara Terpisah?
Pemisahan antara pengiriman heartbeat (indikasi bahwa sensor aktif) dan data lengkap saat terjadi anomali bertujuan untuk menghemat bandwidth dan menghindari pengiriman data secara berlebihan. Heartbeat yang dikirim setiap 30 detik memastikan sensor tetap terpantau aktif, sementara data penuh hanya dikirim saat dibutuhkan yaitu ketika terjadi perubahan parameter signifikan yang mengindikasikan adanya potensi kebakaran.

2. Mengapa Alert dikirim dalam format JSON?
Karena JSON merupakan format data yang ringan, mudah dibaca oleh manusia, serta mudah diproses secara otomatis oleh sistem.

3. Mengapa Edge Gateway Melakukan Validasi dan Agregasi Data?
Edge Gateway berperan dalam menyaring dan merangkum data sebelum diteruskan ke server pusat. Tujuannya adalah mengurangi beban data yang harus dikirim. Agregasi memungkinkan sistem menyampaikan informasi yang lebih ringkas dan relevan untuk pengambilan keputusan yang cepat.

4. Mengapa Server Menentukan Threshold?
Penentuan threshold oleh server bertujuan untuk meminimalkan alarm palsu (false alarm) dan memastikan bahwa hanya kondisi yang benar-benar menunjukkan potensi bahaya yang akan ditindaklanjuti. Dengan menerapkan ambang batas yang tepat, sistem dapat membedakan antara fluktuasi normal dan kejadian yang perlu direspons secara serius.
