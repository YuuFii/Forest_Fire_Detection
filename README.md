**Wireless Sensor Network Deployment for Detection Forest Fire**

Desain Sistem

**Alur Komunikasi Sistem**
![mermaid-diagram-2025-06-16-112822](https://github.com/user-attachments/assets/9764e6cf-1a5a-4608-9248-cc17891de6bb)

HOW
Diagram komunikasi diatas menggambarkan alur kerja sistem deteksi kebakaran hutan yang terdistribusi mulai dari sensor hingga notifikasi kepada petugas. 
Proses dimulai dari sensor node yang secara berkala membaca data lingkungan seperti suhu, kelembaban, asap, dan PM2.5 setiap detik. 
Data ini dianalisis secara lokal di perangkat sensor. Jika terdeteksi kondisi anomali yang mengindikasikan adanya potensi kebakaran, 
maka sensor akan mengirimkan data lengkap ke topik MQTT tertentu. Nmaun jika tidak, hanya heartbeat yang dikirim sebagai sinyal bahwa sensor aktif dan berjalan normal. 
Data yang dikirim kemudian akan diteruskan oleh Edge Gateway yang telah melakukan subscribe pada topik sensor. Di tahap ini, edge gateway akan menjalankan proses filtering dan agregasi data.
Jika edge mendeteksi indikasi kebakaran lokal, maka akan segera mengirimkan peringatan dalam format JSON ke server. Sebaliknya, jika tidak ada kejadian penting, maka data agregat akan mengirimkan hearth beat setiap 30 detik ke server 
Hasil dari analisis ini kemudian disajikan melalui monitoring dashboard dalam bentuk visualisasi peta panas. 
