import os
import discord
import asyncio
import yfinance as yf

from datetime import datetime, time, timedelta

from myserver import server_on

# ตั้งค่า token ของบอทที่นี่

CHANNEL_ID = '1281951649845477418'  # ID ของ channel ที่จะให้บอทส่งข้อความ

client = discord.Client()

# ฟังก์ชันคำนวณเวลาที่เหลือก่อนถึงช่วงเวลาที่ต้องการส่งข้อมูล
def time_until_next_target(target_time):
    now = datetime.now()
    target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
    
    if now > target:
        target = target.replace(day=now.day + 1)  # ถ้าเวลาปัจจุบันเกินเป้าหมาย ให้เลื่อนไปส่งวันถัดไป
    return (target - now).total_seconds()

async def send_exchange_rate():
    await client.wait_until_ready()
    channel = client.get_channel(int(CHANNEL_ID))
    times_to_send = [time(8, 0), time(10, 0), time(12, 0), time(14, 0), time(16, 0), time(18, 0), 
                     time(20, 0), time(22, 0), time(0, 0), time(2, 0), time(4, 0), time(6, 0)]  # กำหนดเวลาที่จะส่ง

    while not client.is_closed():
        now = datetime.now().time()

        # ตรวจสอบว่าเวลาปัจจุบันตรงกับหนึ่งในเวลาที่ต้องการส่งหรือไม่
        for target_time in times_to_send:
            if now >= target_time and now < (datetime.combine(datetime.today(), target_time) + timedelta(minutes=1)).time():
                try:
                    # ดึงข้อมูลจาก yfinance สำหรับค่าเงิน USD/THB
                    data = yf.download('USDTHB=X', period='1d', interval='1m')
                    last_rate = data['Close'][-1]  # ดึงค่าล่าสุด

                    # ดึงวันที่และเวลาปัจจุบัน
                    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # ส่งข้อความพร้อมการตกแต่ง
                    message = (
                        f"```css\n"
                        f"=============================\n"
                        f"★ ค่าเงิน Bath/USD ★\n"
                        f"=============================\n"
                        f"⏰ เวลา: {now_str}\n"
                        f"💵 อัตรา: {last_rate:.4f} บาท/USD\n"
                        f"=============================\n"
                        f"```"
                    )
                    await channel.send(message)
                except Exception as e:
                    await channel.send(f"เกิดข้อผิดพลาดในการดึงข้อมูลค่าเงิน: {str(e)}")

        # รอจนถึงเวลาถัดไปที่กำหนด
        next_target_time = min(times_to_send, key=lambda t: time_until_next_target(t))
        sleep_duration = time_until_next_target(next_target_time)
        await asyncio.sleep(sleep_duration)

@client.event
async def on_ready():
    print(f'บอท {client.user} เข้าสู่ระบบแล้ว!')

client.loop.create_task(send_exchange_rate())

server_on()

client.run(os.getenv('TOKEN'))