from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from main import MangaScrapper
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from usefulfuncs import ImageOperator,DataBaseConnection
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.loader import Loader
import io
import threading
from functools import partial


class MangasLabel(Label):
    def rgba_converter(self,rgba):
        rgba = list(map(lambda x: x/255,rgba[:-1]))
        rgba.append(rgba[-1])
        return rgba


class AvMangas(BoxLayout):
    def __init__(self):
        pass


class LayoutManager(ScreenManager):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)



class MainLayout(Screen):
    availablemangas = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mangadb = DataBaseConnection('assets/mangadata.db')

        self.mangas_available = self.mangadb.select('availableMangas','manganame,mangaimage')

        if self.mangas_available == []:
            self.availablemangas.add_widget(MangasLabel(text='Empty', font_size= dp(20)))
            self.availablemangas.size_hint = (1,1)


    def onstate(self,widget):
        print(self.availablemangas)


class Collector:
    def __init__(self):
        self.message = 'Success'
        self.collections = {}
        self.widgets_collection = []
    

    #Method for the GUI
    def decode_chapter(self,chapter):
        chapnum = float(chapter[1:-1] + '.' + chapter[-1])
        if (chapnum.is_integer()):
            chapnum = int(chapnum)
        return str(chapnum)


    def collectMangaData(self,widget):
        scrapper = MangaScrapper(widget.text)
        self.message = scrapper.message
        poster = scrapper.poster[1].content
        self.collections['poster'] = poster
        self.collections['chapters'] = scrapper.chapters
    

    def data_merger(self,mangadatawidget):

        if (self.collections.get('poster')) != None:
            poster = Image(texture=CoreImage(io.BytesIO(self.collections.get('poster')),ext='jpg').texture,width=100)
            print(type(poster))
            print(poster,mangadatawidget)
            mangadatawidget.add_widget(poster)
            del self.collections['poster']

        if self.collections.get('chapters') != None:
            for chapter in self.collections['chapters']:
                chapter_number = chapter['Type'] + " " + self.decode_chapter(chapter['Chapter'])
                wid = MangasLabel(text=chapter_number,font_size=22)
                mangadatawidget.add_widget(wid)

            del self.collections['chapters']

        if self.message != 'Success':
            wid = MangasLabel(text=self.message)
            self.widgets_collection.append(wid)
            mangadatawidget.add_widget(wid)


class DownloadingLayout(Screen,Collector):
    mangadata = ObjectProperty(None)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(lambda dt:self.data_merger(self.mangadata),0.5)

    
    def clicked_view(self,widget,mangadatawidget):
        for widget in self.widgets_collection:
            mangadatawidget.remove_widget(widget)

            
        threaddownload = threading.Thread(target=partial(self.collectMangaData,widget=widget))
        threaddownload.start()


Builder.load_file('assets/mainlayout.kv')

class MainApp(App):
    def build(self):
        lm = LayoutManager()
        lm.add_widget(DownloadingLayout())
        lm.add_widget(MainLayout())
        return lm
        

if __name__ == "__main__":
    MainApp().run()