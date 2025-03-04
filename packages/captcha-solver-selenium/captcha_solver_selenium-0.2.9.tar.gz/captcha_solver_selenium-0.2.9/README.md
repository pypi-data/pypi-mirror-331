## A package for solving Google reCAPTCHA using Selenium and Speech Recognition
# Authors
- [@Deno9099 - Nguyễn Văn Vinh](https://pypi.org/user/deno9099/)
# Cách Cài
1. cài package với pip hoặc pip3
```python
    pip install captcha-solver-selenium
    pip3 install captcha-solver-selenium
```
2. Cài trình xử lý âm thanh [ffmpeg](https://www.ffmpeg.org/download.html#build-windows)
* Click vào ảnh để xem hướng dẫn
[![FFMPEG](https://i.postimg.cc/DZ6mdk4k/viet-code-ffmpeg-tao-video-hang-loat-e-spam-tu-video-anh-nhac-213015755.png)](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/)
3. Cài môi trường cho trình xử lý âm thanh(Đã có trong hướng dẫn trên)
![FFMPEG SETUP](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnh4b2pubXZueTk4c24xc3V5dGZrMDBqdXlhbGUxeDZmeWZkMGJ6byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6WKmMaCZjqCzCA5Hvj/giphy.gif)
# Chức năng
- Giải captcha google bằng selenium
# Cách sử dụng
- Import thư viện
```python
import captcha_solver
```
- Sử dụng hàm
```python
captcha_solver.captcha_resolve(driver,False,delaytime,audio_click_delay)
```
- driver : là driver khi sử dụng selenium hoặc seleniumbase
- False : Là tham số khi sử dụng [captcha invisible](https://2captcha.com/vi/demo/recaptcha-v2-invisible) nếu không phải là False ngược lại là True
- delaytime : là thời gian chờ khi sử dụng ! 
- audio_click_delay : là thời gian chờ khi click vào phần audio !
# VÍ DỤ
- Trong ví dụ có sử dụng [seleniumbase](https://seleniumbase.io/help_docs/install/)
```python
import captcha_solver
from seleniumbase import Driver
driver = Driver()
driver.get('https://2captcha.com/vi/demo/recaptcha-v2')
captcha_solver.captcha_resolve(driver,False,2,2)
```
![Demo Captcha](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbXd1dHNzOW1kejk2dW50aXExNmJqc2d3bnFpNHhyaDEyNmVkNmR6aiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/zyhEvFZ81gKQh6qSuL/giphy.gif)
# Hỗ trợ
Vui lòng liên hệ qua email [vinhytb3010@gmail.com](mailto:vinhytb3010@gmail.com) hoặc hỗ trợ qua các nền tảng của tác giả trực thuộc.
# 🔗 Links
[![Youtube](https://pypi-camo.freetls.fastly.net/be6f6294510dc074c3451a292d5de17a3874322a/68747470733a2f2f692e706f7374696d672e63632f37686b38366a77582f696d616765732d72656d6f766562672d707265766965772e706e67)](https://www.youtube.com/@wne9838)