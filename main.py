import csv
import sys

from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from Punch_detection_game import *
from threading import Thread
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

import random
import time
from datetime import datetime
import soundfile as sf

# Load the audio file
data, samplerate = sf.read('beep2.wav')




class Home(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.res_scr = None
        self.thread_running=True
        self.data_tables=None
        self.exit_dialog = None


    def show_exit_confirmation(self):
        app = MDApp.get_running_app()  # Correctly get the instance of the running app
        if not self.exit_dialog:
            self.exit_dialog = MDDialog(
                title="Exit Application?",
                text="Do you really want to exit?",
                size_hint=(0.8, 0.3),
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,  # Use app variable here
                        on_release=lambda x: self.exit_dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="Exit",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,  # Use app variable here
                        on_release=lambda x: app.stop()
                    )
                ]
            )
        self.exit_dialog.open()

    def run_punch(self):
        self.app = MDApp.get_running_app()
        self.manager.current = 'result'
        self.res_scr = self.manager.get_screen('result')
        self.res_scr.btn = False
        self.xa = Thread(target=self.start_punch)
        self.xa.start()

    def start_punch(self, *args):
        reaction_times = []  # Array to store reaction times
        for punch_num in range(1, 6):
            punch_detected = False

            while not punch_detected and self.thread_running:
                print(f"Get ready to throw punch {punch_num}...")
                self.change(f"Get ready to throw punch {punch_num}...")
                time.sleep(random.uniform(2, 4))  # Random delay before the signal
                # Play the audio
                sd.play(data, samplerate)
                # time.sleep(0.5)

                pun = f"Throw punch {punch_num}!"
                print(pun)
                self.change(pun)
                reaction_start = time.time()
                audio_data, punch_detected = record_audio()

                if punch_detected:
                    reaction_time = time.time() - reaction_start
                    print(f"Punch {punch_num} detected. Reaction time: {reaction_time:.2f} seconds.")
                    self.change(f"Punch {punch_num} detected.")
                    reaction_times.append(round(reaction_time, 2))
                else:
                    self.change(f"punch {punch_num} not detected. Please try again.")
                    time.sleep(2)
                    print(f"No punch detected for punch {punch_num} within the time limit. Please try again.")

        # Calculate and append the average reaction time
        average_reaction_time = sum(reaction_times) / len(reaction_times)
        reaction_times.append(round(average_reaction_time, 2))

        print("All punches thrown. Reaction times:", reaction_times)
        self.show_result(reaction_times)
        # Calculate the current date and time
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Convert reaction_times list to a string
        reaction_times_str = ','.join(map(str, reaction_times))

        # Write the date and reaction times string to a single line in the text file
        with open('reaction_times.txt', 'a') as file:
            file.write(f"{current_date}, {reaction_times_str}\n")


    @mainthread
    def change(self, data):

        self.res_scr.ids._punch_no.text = data

    @mainthread
    def show_result(self, r_t):
        avg = round(sum(r_t) / len(r_t), 2)
        self.res_scr.avg = str(avg)
        result_data = f'{r_t[0]}, {r_t[1]}, {r_t[2]}, {r_t[3]}, {r_t[4]}'
        self.res_scr.show_result_dialog()
        self.res_scr.dialog.content_cls.ids.result_reflex.text = result_data
        self.res_scr.dialog.content_cls.ids.avg_reflex.text = str(avg)
        self.res_scr.btn = True

    def get_tracker_data(self):
        self.tracker_data = []
        with open('reaction_times.txt', 'r') as f:
            data = f.readlines()
        for i in data:
            if i:
                d = i.replace('\n', '')
                time_ = d[:16]
                score = d[18:41].replace(',', ', ')
                avg = d[-4:] if not d[-4:].startswith(',') else d[-3:]

                self.tracker_data.append([time_, score, avg])
        print(self.tracker_data)
        print(self.data_tables)
        if self.data_tables:
            self.data_tables.rows_num = len((self.tracker_data))
            self.data_tables.row_data = self.tracker_data


    def datatable_view(self):
        self.get_tracker_data()
        self.data_tables = MDDataTable(
            height=30,
            column_data=[
                ("Date", dp(30)),
                ("Reflex time", dp(60),  self.sort_on_avg),
                ("AVG", dp(15))
            ],
            rows_num=len((self.tracker_data)),
            row_data=self.tracker_data,
            elevation=2,
        )

    def sort_on_avg(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][-1]))

    def _kv_post(self):
        self.datatable_view()
        self.ids.datatable.add_widget(self.data_tables)

    def leave(self, *args):
        print('leaving Tracker')
        self.ids.datatable.remove_widget(self.data_tables)



class Content(MDBoxLayout):
    pass


class Result(Screen):
    punch_no = StringProperty('')
    dialog = None
    result_data = None
    avg = None
    btn = False

    def show_result_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                type="custom",
                content_cls=Content(),
                auto_dismiss=False,
                md_bg_color='grey',
                buttons=[
                    MDRaisedButton(
                        text="Back",
                        on_press=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.open()


class PunchApp(MDApp):
    def build(self):
        self.kv = Builder.load_file('main.kv')
        return self.kv

    def on_stop(self):
        self.kv.get_screen('home').thread_running = False
        sys.exit()
        
if __name__ == '__main__':
    PunchApp().run()
