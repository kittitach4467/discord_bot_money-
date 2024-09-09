import discord
import asyncio
import yfinance as yf
from datetime import datetime, time, timedelta

from myserver import server_on

# ตั้งค่า token ของบอทที่นี่
TOKEN = 'MTI3Njk1MjE0OTI0NjM0OTQxMg.GEiOqb.RSCl2e9_S5DV7o_wIoKN7bDUptxNyNqn3YIjvo'
CHANNEL_ID = '1276946209499512933'  # ID ของ channel ที่จะให้บอทส่งข้อความ

client = discord.Client()

# ฟังก์ชันคำนวณเวลาที่เหลือก่อนถึงช่วงเวลาที่ต้องการส่งข้อมูล
def time_until_next_target(target_time):
    now = datetime.now()
    target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
    
    if now > target:
        target = target.replace(day=now.day + 1)  # ถ้าเวลาปัจจุบันเกินเป้าหมาย ให้เลื่อนไปส่งวันถัดไป
    return (target - now).total_seconds()

async def send_gold_price():
    await client.wait_until_ready()
    
    channel = client.get_channel(int(CHANNEL_ID))
    times_to_send =  [  time(8, 0),time(9, 0), time(10, 0),time(11, 0), time(12, 0),time(13, 0), time(14, 0),time(15, 0),
                        time(16, 0),time(17, 0), time(18, 0),time(19, 0), time(20, 0),time(22, 0), time(23, 0),
                        time(0, 0),  time(1, 0), time(2, 0), time(3, 0), time(4, 0),  time(5, 0), time(6, 0), time(7, 0)]  # กำหนดเวลาที่จะส่ง

    while not client.is_closed():
        now = datetime.now().time()

        # ตรวจสอบว่าเวลาปัจจุบันตรงกับหนึ่งในเวลาที่ต้องการส่งหรือไม่
        for target_time in times_to_send:
            if now >= target_time and now < (datetime.combine(datetime.today(), target_time) + timedelta(minutes=1)).time():
                try:
                    # ดึงข้อมูลราคาทอง (XAU/USD) จาก yfinance
                    data = yf.download('XAUUSD=X', period='1d', interval='1m')
                    last_price = data['Close'][-1]  # ดึงราคาล่าสุด

                    # ดึงวันที่และเวลาปัจจุบัน
                    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # ส่งข้อความพร้อมการตกแต่ง
                    message = (
                        f"```css\n"
                        f"=============================\n"
                        f"★ ราคาทองคำ (XAU/USD) ★\n"
                        f"=============================\n"
                        f"⏰ เวลา: {now_str}\n"
                        f"💰 ราคา: {last_price:.2f} USD/ออนซ์\n"
                        f"=============================\n"
                        f"```"
                    )
                    await channel.send(message)
                except Exception as e:
                    await channel.send(f"เกิดข้อผิดพลาดในการดึงข้อมูลราคาทอง: {str(e)}")

        # รอจนถึงเวลาถัดไปที่กำหนด
        next_target_time = min(times_to_send, key=lambda t: time_until_next_target(t))
        sleep_duration = time_until_next_target(next_target_time)
        await asyncio.sleep(sleep_duration)

@client.event
async def on_ready():
    print(f'บอท {client.user} เข้าสู่ระบบแล้ว!')

client.loop.create_task(send_gold_price())

server_on()

client.run(TOKEN)

TOKEN = 'MTI3Njk1MjE0OTI0NjM0OTQxMg.GEiOqb.RSCl2e9_S5DV7o_wIoKN7bDUptxNyNqn3YIjvo'
