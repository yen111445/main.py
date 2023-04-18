import os
import sys
import time, datetime
import numpy as np

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials as SAC
except:
    os.system('pip install gspread oauth2client')
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials as SAC
    
    
class GoogleSheet():
    def __init__(self, json_file, sheet_name):
        self.json = json_file
        self.sheet = sheet_name
        self.connect_sheet()
    
    def connect_sheet(self):
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            key = SAC.from_json_keyfile_name(self.json, scope)
            gc = gspread.authorize(key)
            self.worksheet = gc.open(self.sheet).sheet1
        except Exception as e:
            print('fail connect google sheet')
            print(e)
            sys.exit(0)
    
    def set_time(self, set_time):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).split(' ')
        now[1] = GoogleSheet.Time2num(now[1])
        now.append(GoogleSheet.Time2num(set_time))
        self.worksheet.append_row(now)
        
    def wake_up(self, test_time = None):
        if test_time is None:
            now = datetime.datetime.now().replace(microsecond=0)
        else:
            now = datetime.datetime.strptime(test_time, '%Y-%m-%d %H:%M:%S')
        r = len(self.worksheet.col_values(1))
        rec_time = self.worksheet.row_values(r)
        # calculate sleep time
        temp = datetime.datetime.strptime(rec_time[0]+' '+rec_time[1], '%Y-%m-%d %H:%M:%S')
        temp = GoogleSheet.Time2num(str(now-temp))
        now = GoogleSheet.Time2num(now.strftime('%Y-%m-%d %H:%M:%S').split(' ')[1])
        real_time = [now, temp]
        self.worksheet.update('D'+str(r), [real_time])
    
    @staticmethod
    def Time2num(t):
        t = t.split(':')
        num_time = int(t[0])/24+int(t[1])/24/60+int(t[2])/24/60/60
        return num_time
    
def main():
    ws = GoogleSheet('python-digit-aa0bcbb1a168.json', 'digit')
    for i in range(16, 20):
        ws.set_time('7:00:00')
        ws.wake_up('2021-08-02 07:'+str(i)+':15')

if __name__ == '__main__':
    main()