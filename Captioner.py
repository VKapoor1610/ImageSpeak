
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2

# from plyer import storagepath
import pygame

import gtts
from playsound import playsound
import torch


class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        buf = cv2.flip(frame, 0).tobytes()
        img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.texture = img_texture
        

        
class CamApp(App):
    

    def __init__(self , **kwargs):
        super(CamApp, self).__init__(**kwargs)
        from transformers import AutoModelForCausalLM
        from transformers import AutoProcessor
        from translate import Translator
        from PIL import Image as Img

        self.Img = Img
        self.translator = Translator(to_lang="hi")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/git-base")
        self.processor = AutoProcessor.from_pretrained("microsoft/git-base")

        # print(self.model.device)

    
    def build(self):
        
    
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=30)
        self.button = Button(text="Select Language", size_hint_y=None, height=220, font_size=30, 
                             background_color=(140/255, 3/255, 252/255, 1), color=(1, 1, 1, 1))


        self.box_layout = BoxLayout(orientation='vertical')
               

        self.box_layout.add_widget(self.my_camera)
        # self.box_layout.add_widget(Label(text='Text Area'))

        self.box_layout.add_widget(self.button)

        
        self.language_variable = None
        self.play_initial_message()

        def on_button_press(instance):
            if self.language_variable is None:
                if instance.text == "Language Select":
                    instance.text = "Press Again For Hindi"
                    Clock.schedule_once(self.check_second_click, 1)
                elif instance.text == "Press Again For Hindi":
                    self.language_variable = 'Hindi'
                    instance.text = "Capture"
                    self.thank_you_message('Hindi')
                else:
                    self.language_variable = 'English'
                    instance.text = "Capture"
                    self.thank_you_message('English')
            else:
                if instance.text == "Capture":
                    self.capture_image(instance)

        self.button.bind(on_press=on_button_press)

        return self.box_layout

    def play_initial_message(self):
        myobj = gtts.gTTS(text="Press Once For English. Hindi ke liye do    baar dabayen", lang='en', slow=False)
        
        
        myobj.save("initial_message.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("initial_message.mp3")
        pygame.mixer.music.play()

    def check_second_click(self, dt):
        if self.language_variable is None:
            self.button.text = "Language Select"
            Clock.unschedule(self.check_second_click)
            self.language_variable = 'English'
            self.button.text = "Capture"
            self.thank_you_message('English')

    def thank_you_message(self, language):
        if language == 'English':
            myobj = gtts.gTTS(text="Welcome to ImageSpeak english, tap to capture", lang='en', slow=False)
        else:
            myobj = gtts.gTTS(text="आपका इमेजस्पीक हिन्दी भाषा में स्वागत है, कृपया टैप करें।", lang='hi', slow=False)

        myobj.save("thank_you_message.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("thank_you_message.mp3")
        pygame.mixer.music.play()

    def capture_image(self, instance):
        ret, frame = self.capture.read()
        cv2.imwrite('captured_image.jpg', frame)
        self.generate_captions('captured_image.jpg', self.language_variable)

    
    def generate_captions(self, image_path, language):
        # Your code to generate captions goes here

        image = self.Img.open(image_path)

        image = image.convert("RGB")

        # print(image.size)

        inputs = self.processor(images=image, return_tensors="pt")
        pixel_values = inputs.pixel_values

        generated_ids = self.model.generate(pixel_values=pixel_values, max_length=1000)
        generated_caption = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        # print(generated_caption)
        ###
        
        
        # print(f"Generating captions for {image_path} in {language}")
        caption = generated_caption  # Replace with your generated caption
        
        if language == 'English':
            lang_code = 'en'
        elif language == 'Hindi':
            caption = self.translator.translate(caption)
            print(caption)
            lang_code = 'hi'
            
        
            
        myobj = gtts.gTTS(text=caption, lang=lang_code, slow=False)

        import random 
        t = random.randint(1, 100)
        
        myobj.save(f"caption{t}.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load(f"caption{t}.mp3")
        pygame.mixer.music.play()
        

if __name__ == '__main__':
    CamApp().run()