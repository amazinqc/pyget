这是pyget
coredown.py是下载包，实现断点续传
fetchMusic.py是blogMusic专用下载程序（外围爬虫程序）
v1.0.0
单进程同步下载，断点自动续传，已存在文件自动跳过下载，实时显示下载大小，但不能实时显示下载速度，结束或断点时显示期间平均下载速度。文件默认以起始时间戳命名，断点缓存文件命名后缀".downtemp"。爬取所有可下载音乐，下载期间可手动"Ctrl"+"C"中断进程，下载已经开始时自动建立断点。
