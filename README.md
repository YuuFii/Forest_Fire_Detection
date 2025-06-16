# **Wireless Sensor Network Deployment for Detection Forest Fire**
![visualisasi-deteksi-kebakaran-dengan-map](https://github.com/user-attachments/assets/7dc9b8fa-0f12-4eb0-a94a-c372d92221da)

Visualisasi di atas digunakan untuk menunjukkan potensi kebakaran di suatu wilayah dengan menggunakan skema warna yang merepresentasikan tingkat intensitas potensi kebakaran. Wilayah dengan potensi kebakaran rendah ditandai dengan warna biru keunguan, sedangkan wilayah dengan potensi kebakaran tinggi diberi warna merah. Visualisasi ini sangat berguna sebagai alat bantu dalam perencanaan mitigasi bencana kebakaran dan pengelolaan sumber daya alam di wilayah tersebut.

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


![Arsitektur Diagram Sistem](https://github.com/user-attachments/assets/bc2ad243-8d75-4108-aa56-980ddc5ace09)

## HOW (BAGAIMANA ARSITKETUR SISTEM BERINTERAKSI)

Diagram diatas menggambarkan arsitektur system yang bekerja berdasarkan arsitketur Publisher-Subscriber dengan menggunakan MQTT Broker oleh HiveMQ Cloud sebagai pusat komunikasinya. Terdapat beberapa Sensor Node yang bekerja untuk mengumpulkan data lingkungan (suhu, kelembapan, dll) dari lokasi masing masing yang kemudian dikirim ke HiveMQ Cloud dengan protokol MQTT. Setiap sensor akan mempublikasi data dalam format JSON dengan topik 
forest/area/[location]/sensor/[node_id]/[sensor_type] 
(contoh: forest/area/sumatra/sensor/node1/temperature).
Broker kemudian akan menerima data dari publisher dan akan meneruskannya kepada subscriber yang berlangganan pada topik terkait yaitu Server Node. 
Server node akan berlangganan pada semua topik dalam sensor (forest/area/+/sensor/+/+) untuk memperoleh semua data dalam setiap sensor. Kemudian akan dilakukan analisis untuk mendeteksi kebakaran berdasarkan parameter yang telah ditentukan. Apabila terdeteksi bahwa data menunjukan adanya tanda tanda kebakaran maka akan dikirim sebuah pesan dengan topik forest/alert/[location]/[node_id].
Flask Dahsborad digunakan untuk menampilkan data yang diperoleh sensor melalui sebuah web secara real time.

## WHY (MENGAPA DIBANGUN DENGAN ARSITEKTUR INI)

1. Mengapa digunakan pola Pub/Sub dengan MQTT?
Digunakan arsitektur MQTT sehingga setiap node dapat bekerja secara independent dan tidak akan mempengaruhi komponen lain apabila terjadi permasalahan pada salah satu komponen. Node sensor dan Node Server hanya perlu mengetahui topik MQTT untuk diperoleh informasi. MQTT memiliki bandwith yang efisien dan mendukung QoS 1 sehingga alert harus terkirim setidaknya sekali. Selain itu didukungnya fitur Last Will & Testament (LWT) yang akan menguirim pesan akhir atau "last will" apabila koneksi pada node sensor terputus. Faktor tersebut menjadi alas an Utama digunakannya MQTT disbanding arsitektur lain. 

2. Mengapa sistem bersifat event-driven?
Karena kejadian seperti kebakaran hutan memiliki urgensi dalam peringatan yang lebih awal sehingga dipilih pemrosesan yang lebih reaktif yaitu event-driven. Node sensor akan menerima data lingkungan dan node server akan menganalisis data untuk menentukan apakah data lebihi parameter yang menandakan adanya kebakaran hutan. Arsitektur seperti Polling-Based tidak cocok karena sensor harus terus menjawab request dan memiliki latensi yang tinggi, Request-response tidak cocok karena sensor harus menunggu permintaan server sehingga tidak cocok untuk data kontinu. 

3. Megapa digunakan Heartbeat dan LWT?
Heartbeat akan mengirim pesan untuk mengindikasikan bahwa sensor masih aktif dan dikirim secara rutin untuk memastikan bahwa node sensor tetap aktif. Kemudian LWT atau Last Will & Testament akan secara langsung mengirimkan pesan bahwa sensor offline apabila sensor mati atau terjadi failure secara mendadak. Keduanya digunakan secara bersamaan sehingga server dapat mengetahui keadaan sensor setiap saat.  

4. Mengapa Alert system terpisah dari Data Stream?
Data dalam sensor bertopik sensors/# dan alert bertopik alter/# dipisah untuk memprioritaskan pengiriman alter yang memeiliki tingkat urgensi yang lebih tinggi sehingga peringatan kebarakan dapat disampaikan secara lnagsung setelah diperolehnya data yang mengidikasikan adanya kebakaran. Pemisahan ini juga dilakukan untuk mempermudah filtering dalam dashboard. 

