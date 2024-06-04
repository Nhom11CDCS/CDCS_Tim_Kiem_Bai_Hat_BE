# CDCS_Tim_Kiem_Bai_Hat_BE

backend for our app
#1
crawler.py dùng lấy dữ liệu bài hát từ web lyrics.vn và thêm vào elasticsearch.
#2
folder BEfoleder là thư mục của app tìm kiếm bài hát.
changes: api /uploads của app.py nhận vào: tác giả, bài hát, file audio. chuyển tiếp audio đó tới api /transcribe của api.py. Kết quả nhận về là lời bài hát được nhận diện
#3
file api.py là api sử dụng viet asr, di chuyển file này tới cùng thư mục với infer.py
api.py. nhận file audio được gửi tới, lưu trữ vào hệ thống. sử dụng viet asr để nhận diện giọng nói từ file audio được gửi tới và trả về text
