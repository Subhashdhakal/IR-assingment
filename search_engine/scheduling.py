import schedule
import time
import subprocess

def job():
    subprocess.run(["cmd", "/c", "myenv\\Scripts\\activate && python scrapping.py"])
    
schedule.every().monday.at("10:30").do(job) 

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
