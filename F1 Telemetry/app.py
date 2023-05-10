import subprocess
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from process.analyze import Analyze


"""
    Classes that allow visuals from kivy file to be represented.
"""

class IntroWindow(Screen):
    pass
            
class LeagueWindow(Screen):
    def btn(self, choice):
        if choice.text != "":
            sm.league_name = str(choice.text).upper()

class DayWindow(Screen):
    def btn(self, choice):
        sm.day = choice
    
class SprintWindow(Screen):
    def btn(self, choice):
        sm.sprint_race = choice
        
class RaceWindow(Screen):
    def btn(self, choice):
        if choice.text != "":
            sm.race_name = str(choice.text).upper()
        
class SubmitWindow(Screen):
    pass

# Manages data.
class CollectingWindow(Screen):
    def on_enter(self):
        
        # Collects data.
        subprocess.run(["node", "process/collect.js", sm.day, sm.sprint_race, sm.race_name])
    
        # Analyzes data.
        a = Analyze(sm.league_name, sm.day, sm.race_name)
        a.ReadData()
        a.ProcessData()
        a.SaveData()
        
        sm.current = "finish"
        
class FinishWindow(Screen):
    pass


# Saves data to be used in collection process.
class WindowManager(ScreenManager):
    league_name = ""
    day = ""
    sprint_race = ""
    race_name = ""


kv = Builder.load_file("my.kv")
sm = WindowManager()

# Initialises screens
screens = [IntroWindow(name="intro"), 
           LeagueWindow(name="league"), DayWindow(name="day"), SprintWindow(name="sprint"), RaceWindow(name="race"), 
           SubmitWindow(name="submit"), CollectingWindow(name="collecting"),
           FinishWindow(name="finish")]
for screen in screens:
    sm.add_widget(screen)


class MyApp(App):
    def build(self):
        return sm


# Runs app.
if __name__ == "__main__":
    MyApp().run()
