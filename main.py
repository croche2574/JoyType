import argparse
from random import random
import string
import keyboardlayout as kl
import keyboardlayout.pygame as klp
from keyboardlayout import Key
import pygame
import pygame_menu
import random
import math
import time
from datetime import date, datetime, timedelta
import json
import sys
import difflib as dl

grey = pygame.Color('grey')
dark_grey = ~pygame.Color('grey')


class JoyCursor():
    def __init__(self, id, index, keyboard) -> None:
        self.id = id
        self.index = index
        self.keyboard = keyboard
        self.previndex = 0

    def moveX(self, direction):
        self.previndex = self.index
        self.index += direction
        if self.index > 60:
            self.index = 60
        if self.index < 0:
            self.index = 0
        self.index = int(self.index)

    def moveY(self, direction):  # Fix wonky cursor movement
        self.previndex = self.index
        if direction >= 0:
            if self.index == 0:
                self.index = 14
            elif self.index == 13:
                self.index = 27
            elif self.index == 14:
                self.index = 28
            elif self.index in range(0, 26):
                self.index += direction*14
            elif self.index == 26:
                self.index = 40
            elif self.index == 40:
                self.index = 52
            elif self.index == 41:
                self.index = 53
            elif self.index == 42:
                self.index = 54
            elif self.index == 43:
                self.index = 55
            elif self.index in range(44, 49):
                self.index = 56
            elif self.index == 49:
                self.index = 57
            elif self.index == 50:
                self.index = 58
            elif self.index == 51:
                self.index = 58
            elif self.index in range(53, 60):
                self.index = self.index
            else:
                self.index += direction*13
        else:
            if self.index in range(0, 14):
                self.index = self.index
            elif self.index == 14:
                self.index = 0
            elif self.index == 27:
                self.index = 13
            elif self.index == 28:
                self.index = 14
            elif self.index in range(0, 40):
                self.index += direction*14
            elif self.index == 52:
                self.index = 40
            elif self.index == 53:
                self.index = 41
            elif self.index == 54:
                self.index = 42
            elif self.index == 55:
                self.index = 43
            elif self.index == 56:
                self.index = 46
            elif self.index == 57:
                self.index = 49
            elif self.index == 58:
                self.index = 51
            elif self.index == 59:
                self.index = 52
            elif self.index == 60:
                self.index = 52
            else:
                self.index += direction*13

        if self.index > 60:
            self.index = 60
        if self.index < 0:
            self.index = 0
        self.index = int(self.index)
        print(self.index)

# Main Class


class TypingTool():
    def __init__(self, layout_name: kl.LayoutName, mode: string) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Joystick Typing Tool')
        self.MOVEEVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MOVEEVENT, 200)
        self.canmove = True

        self.userid = ''
        self.usertext = ''
        self.hovertext = ''
        self.starttime = time.time()
        self.endtime = 0
        self.userresults = {}
        self.currentrun = {}
        self.interactedkeys = []
        self.runnum = 0

        self.sentences = [line.rstrip() for line in open("phrases2.txt", "r")]

        # print(self.MOVEEVENT)
        # block events that we don't want
        pygame.event.set_blocked(None)
        pygame.event.set_allowed([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT,
                                 pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, self.MOVEEVENT])
        self.mode = mode
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            # No joysticks!
            print("Error, I didn't find any joysticks.")
        else:
            # Use joystick #0 and initialize it
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()
            print('Joystick initialized')
        self.key_size = 60
        self.key_info = kl.KeyInfo(
            margin=10,
            color=grey,
            txt_color=dark_grey,
            txt_font=pygame.font.SysFont('Arial', self.key_size//4),
            txt_padding=(self.key_size//6, self.key_size//10)
        )
        self.keyboard = self.get_keyboard(
            layout_name, self.key_size, self.key_info)
        # print(keyboard.rect.height)
        self.w = self.keyboard.rect.width
        self.h = self.keyboard.rect.height*2
        self.screen = pygame.display.set_mode(
            (self.keyboard.rect.width, self.keyboard.rect.height*2))
        self.screen.fill(pygame.Color('White'))
        self.keyboard.draw(self.screen)
        pygame.display.update()

        self.prepare_results()
        self.start_menu()

    def start_menu(self):
        menu = pygame_menu.Menu('Typing Tool', self.w,
                                self.h, theme=pygame_menu.themes.THEME_BLUE)
        menu.add.text_input('User ID: ', onchange=self.set_userid)
        menu.add.selector(
            'Mode :', [('Left', 1), ('Right', 2), ('Both', 3)], onchange=self.set_mode)
        menu.add.button('Start', self.run_until_user_closes_window)
        menu.add.button('Quit', self.save_and_quit)
        menu.mainloop(self.screen)

    def set_mode(self, mode, num):
        print(mode[0][0])
        self.mode = mode[0][0]

    def set_userid(self, value):
        self.userid = value

    def prepare_results(self):
        self.userresults["start_time"] = str(
            timedelta(seconds=round(time.time())))
        self.userresults["date"] = date.today()

    def tabulate(self):
        r = "Run " + str(self.runnum)
        print(r)
        self.endtime = time.time()
        totaltime = self.endtime - self.starttime
        error_count = 0
        comparison = dl.SequenceMatcher(None, self.sentence, self.usertext)
        for tag, i1, i2, j1, j2 in comparison.get_opcodes():
            print(
                f'{tag:7} s1[{i1}:{i2}] --> s2[{j1}:{j2}] {self.sentence[i1:i2]!r:>6} --> {self.usertext[j1:j2]!r}')
            if tag != 'equal':
                error_count += (j2-j1)

        self.currentrun["sentence"] = self.sentence
        self.currentrun["submitted_text"] = self.usertext
        self.currentrun["mode"] = self.mode
        self.currentrun["percent_incorrect"] = (
            error_count*100)/len(self.sentence)
        self.currentrun["wpm"] = (len(self.usertext)*60)/(5*totaltime)
        self.currentrun["net_wpm"] = (
            (len(self.usertext)*60)/(5*totaltime) - (error_count/(totaltime/60)))
        self.currentrun["cps"] = (len(self.usertext)/(totaltime))
        if len(self.sentence) <= self.total_count:
            self.currentrun["accuracy"] = (
                (len(self.usertext) - error_count)/self.total_count)*100
        else:
            self.currentrun["accuracy"] = (
                (len(self.usertext) - error_count)/len(self.sentence))*100
        self.currentrun["interacted_keys"] = self.interactedkeys
        self.userresults[r] = self.currentrun
        # print(self.userresults)
        self.reset_values()

    def reset_values(self):
        self.usertext = ''
        self.hovertext = ''
        self.starttime = 0
        self.endtime = 0
        self.currentrun = {}
        self.interactedkeys = []

    def save_and_quit(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        with open('./output/' + self.userid + '-' + timestr + '.json', 'w') as convert_file:
            convert_file.write(json.dumps(
                self.userresults, indent=4, default=str))
        print('quit')
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def get_keyboard(
        self,
        layout_name: kl.LayoutName,
        key_size: int,
        key_info: kl.KeyInfo
    ) -> klp.KeyboardLayout:
        keyboard_info = kl.KeyboardInfo(
            position=(0, 294),
            padding=2,
            color=~grey
        )
        letter_key_size = (key_size, key_size)  # width, height
        keyboard_layout = klp.KeyboardLayout(
            layout_name,
            keyboard_info,
            letter_key_size,
            key_info
        )
        return keyboard_layout

    def write_text(self, screen, title, y, f_size, text_color):
        font_family = pygame.font.SysFont('Arial', f_size)
        text = font_family.render(title, 1, text_color)
        text_box = text.get_rect(center=(self.w/2, y))
        screen.blit(text, text_box)
        pygame.display.update()

    def add_key_L(self, curkeyR, interact_type):
        try:
            self.interactedkeys[self.key_index - 1]['time_hovered'] = (
                time.time() - self.last_interact_time_L)
        except:
            pass
        key = {'key_value': curkeyR,
               'interact_type': interact_type, 'cursor': 'Left'}
        print(key)
        self.interactedkeys.insert(self.key_index, key)
        self.key_index += 1
        self.last_interact_time_L = time.time()

    def add_key_R(self, curkeyR, interact_type):
        try:
            self.interactedkeys[self.key_index - 1]['time_hovered'] = (
                time.time() - self.last_interact_time_L)
        except:
            pass
        key = {'key_value': curkeyR,
               'interact_type': interact_type, 'cursor': 'Right'}
        print(key)
        self.interactedkeys.insert(self.key_index, key)
        self.key_index += 1
        self.last_interact_time_L = time.time()

    def update_usertext(self, text, increment=False):
        self.usertext += text
        if increment:
            self.total_count += 1

    def run_until_user_closes_window(self):  # main loop
        self.userresults["user_id"] = self.userid
        self.starttime = time.time()
        self.runnum += 1
        self.screen.fill(pygame.Color('White'))
        # key styles
        hovered_key_info_L = kl.KeyInfo(
            margin=14,
            color=pygame.Color('Orange'),
            txt_color=pygame.Color('black'),
            txt_font=pygame.font.SysFont('Arial', self.key_size//4),
            txt_padding=(self.key_size//6, self.key_size//10)
        )
        pressed_key_info_L = kl.KeyInfo(
            margin=14,
            color=pygame.Color('DarkOrange'),
            txt_color=pygame.Color('white'),
            txt_font=pygame.font.SysFont('Arial', self.key_size//4),
            txt_padding=(self.key_size//6, self.key_size//10)
        )
        hovered_key_info_R = kl.KeyInfo(
            margin=14,
            color=pygame.Color('Blue'),
            txt_color=pygame.Color('black'),
            txt_font=pygame.font.SysFont('Arial', self.key_size//4),
            txt_padding=(self.key_size//6, self.key_size//10)
        )
        pressed_key_info_R = kl.KeyInfo(
            margin=14,
            color=pygame.Color('DarkBlue'),
            txt_color=pygame.Color('white'),
            txt_font=pygame.font.SysFont('Arial', self.key_size//4),
            txt_padding=(self.key_size//6, self.key_size//10)
        )
        disabled_key_info = kl.KeyInfo(
            margin=10,
            color=pygame.Color('LightGray'),
            txt_color=pygame.Color('DarkGray'),
            txt_font=pygame.font.SysFont('Arial', self.key_size//4),
            txt_padding=(self.key_size//6, self.key_size//10)
        )
        disabled_keys = [0, 1, 2, 3, 4, 5, 6,
                         7, 8, 9, 10, 11, 12, 14, 28, 41, 52, 53, 54, 55, 57, 58, 59, 60]

        released_key_info = self.key_info

        self.sentence = random.choice(self.sentences).lower()
        self.write_text(self.screen, self.sentence,
                        65, 35, pygame.Color('Black'))

        joycur = []
        joycur.append(JoyCursor(0, 15, self.keyboard))
        joycur.append(JoyCursor(1, 24, self.keyboard))
        try:
            curkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                joycur[0].index][0]
            curprevkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                joycur[0].previndex][0]
            self.keyboard.update_key(curprevkeyL, released_key_info)
        except:
            pass
        try:
            curkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                joycur[1].index][0]
            curprevkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                joycur[1].previndex][0]
            self.keyboard.update_key(curprevkeyR, released_key_info)
        except:
            pass
        try:
            if self.mode == 'Left' or self.mode == 'Both':
                self.keyboard.update_key(curkeyL, hovered_key_info_L)
        except:
            pass
        try:
            if self.mode == 'Right' or self.mode == 'Both':
                self.keyboard.update_key(curkeyR, hovered_key_info_R)
        except:
            pass

        self.keyboard.draw(self.screen)
        correction_count = 0
        self.total_count = 0
        self.key_index = 0
        self.last_interact_time_L = 0
        self.last_interact_time_R = 0
        running = True

        # print(keyboard._rect_by_key_and_loc)
        for keyindex in disabled_keys:
            curkey = list(self.keyboard._rect_by_key_and_loc.items())[
                keyindex][0]
            self.keyboard.update_key(curkey, disabled_key_info)

        while running:
            try:
                curkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                    joycur[0].index][0]
            except:
                pass
            try:
                curkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                    joycur[1].index][0]
            except:
                pass

            for event in pygame.event.get():
                # print(event.type)
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break

                # print(list(keyboard._key_to_actual_key.values()))
                # print(curkey)
                # print(next(value for value in list(keyboard._key_to_actual_key.values())))
                # print(keyboard._key_to_actual_key.get(curkey, curkey).value)

                if event.type == pygame.JOYBUTTONDOWN:
                    # print(event.button)
                    if (event.button == 4 or event.button == 8) and self.mode != 'Right':
                        self.keyboard.update_key(curkeyL, pressed_key_info_L)
                        self.add_key_L(curkeyL, 'pressed')

                        if curkeyL == Key.BACKSPACE:
                            self.usertext = self.usertext[:-1]
                            correction_count += 1
                        elif curkeyL == Key.SPACE:
                            self.usertext += ' '
                            self.total_count += 1
                        elif curkeyL == Key.TAB:
                            self.usertext += ''
                        elif curkeyL == Key.LEFT_SHIFT:
                            self.usertext += ''
                        elif curkeyL == Key.RIGHT_SHIFT:
                            self.usertext += ''
                        elif curkeyL == Key.CAPSLOCK:
                            self.usertext += ''
                        elif curkeyL == Key.RIGHT_CONTROL:
                            self.usertext += ''
                        elif curkeyL == Key.LEFT_CONTROL:
                            self.usertext += ''
                        elif curkeyL == Key.CONTEXT_MENU:
                            self.usertext += ''
                        elif curkeyL == Key.RIGHT_META:
                            self.usertext += ''
                        elif curkeyL == Key.RIGHT_ALT:
                            self.usertext += ''
                        elif curkeyL == Key.LEFT_META:
                            self.usertext += ''
                        elif curkeyL == Key.LEFT_ALT:
                            self.usertext += ''
                        elif curkeyL == Key.RETURN:
                            running = False
                            self.keyboard.update_key(
                                curkeyL, released_key_info)
                            self.keyboard.update_key(
                                curkeyR, released_key_info)
                            self.tabulate()
                        else:
                            self.usertext += curkeyL.value
                            self.total_count += 1

                    if (event.button == 5 or event.button == 9) and self.mode != 'Left':
                        self.keyboard.update_key(curkeyR, pressed_key_info_R)

                        self.add_key_R(curkeyR, 'pressed')

                        if curkeyR == Key.BACKSPACE:
                            self.usertext = self.usertext[:-1]
                            correction_count += 1
                        elif curkeyR == Key.SPACE:
                            self.usertext += ' '
                            self.total_count += 1
                        elif curkeyR == Key.TAB:
                            self.usertext += ''
                        elif curkeyR == Key.LEFT_SHIFT:
                            self.usertext += ''
                        elif curkeyR == Key.RIGHT_SHIFT:
                            self.usertext += ''
                        elif curkeyR == Key.CAPSLOCK:
                            self.usertext += ''
                        elif curkeyR == Key.RIGHT_CONTROL:
                            self.usertext += ''
                        elif curkeyR == Key.LEFT_CONTROL:
                            self.usertext += ''
                        elif curkeyR == Key.CONTEXT_MENU:
                            self.usertext += ''
                        elif curkeyR == Key.RIGHT_META:
                            self.usertext += ''
                        elif curkeyR == Key.RIGHT_ALT:
                            self.usertext += ''
                        elif curkeyR == Key.LEFT_META:
                            self.usertext += ''
                        elif curkeyR == Key.LEFT_ALT:
                            self.usertext += ''
                        elif curkeyR == Key.RETURN:
                            running = False
                            self.keyboard.update_key(
                                curkeyL, released_key_info)
                            self.keyboard.update_key(
                                curkeyR, released_key_info)
                            self.tabulate()
                        else:
                            self.usertext += curkeyR.value
                            self.total_count += 1
                            print('select r')
                    print(self.interactedkeys)
                    self.screen.fill(pygame.Color('White'))
                    self.write_text(self.screen, self.sentence, 65,
                                    35, pygame.Color('Black'))
                    self.write_text(self.screen, self.usertext, 100,
                                    25, pygame.Color('Black'))
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == 4 or event.button == 8:
                        self.keyboard.update_key(curkeyL, hovered_key_info_L)
                    if event.button == 5 or event.button == 9:
                        self.keyboard.update_key(curkeyR, hovered_key_info_R)

                if event.type == self.MOVEEVENT:
                    self.canmove = True

            if self.my_joystick and self.canmove:  # move cursors
                for x in range(0, 4):
                    isleft = False
                    isright = False
                    if abs(self.my_joystick.get_axis(x)) > .4:
                        # print('Axis: %', x)
                        if x == 0 and self.mode != 'Right':
                            joycur[0].moveX(math.copysign(
                                1, self.my_joystick.get_axis(x)))
                            isleft = True
                        elif x == 1 and self.mode != 'Right':
                            joycur[0].moveY(math.copysign(
                                1, self.my_joystick.get_axis(x)))
                            isleft = True
                        elif x == 2 and self.mode != 'Left':
                            joycur[1].moveX(math.copysign(
                                1, self.my_joystick.get_axis(x)))
                            isright = True
                        elif x == 3 and self.mode != 'Left':
                            joycur[1].moveY(math.copysign(
                                1, self.my_joystick.get_axis(x)))
                            isright = True
                        # print(key)
                        # print(c.index)
                        if self.mode == 'Right':
                            curkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[1].index][0]
                            curprevkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[1].previndex][0]
                            if joycur[1].previndex in disabled_keys:
                                self.keyboard.update_key(
                                    curprevkeyR, disabled_key_info)
                            else:
                                self.keyboard.update_key(
                                    curprevkeyR, released_key_info)
                            self.keyboard.update_key(
                                curkeyR, hovered_key_info_R)
                            self.add_key_R(curkeyR, 'hovered')

                        elif self.mode == 'Left':
                            curkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[0].index][0]
                            curprevkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[0].previndex][0]
                            if joycur[0].previndex in disabled_keys:
                                self.keyboard.update_key(
                                    curprevkeyL, disabled_key_info)
                            else:
                                self.keyboard.update_key(
                                    curprevkeyL, released_key_info)
                            self.keyboard.update_key(
                                curkeyL, hovered_key_info_L)
                            self.add_key_L(curkeyL, 'hovered')

                        elif self.mode == 'Both':
                            curkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[0].index][0]
                            curprevkeyL = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[0].previndex][0]
                            curkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[1].index][0]
                            curprevkeyR = list(self.keyboard._rect_by_key_and_loc.items())[
                                joycur[1].previndex][0]
                            self.keyboard.update_key(
                                curprevkeyR, released_key_info)
                            self.keyboard.update_key(
                                curprevkeyL, released_key_info)
                            self.keyboard.update_key(
                                curkeyR, hovered_key_info_R)
                            self.keyboard.update_key(
                                curkeyL, hovered_key_info_L)
                            print(
                                f'curkeyL: {curkeyL} prevkeyL: {curprevkeyL}')
                            print(
                                f'curkeyR: {curkeyR} prevkeyR: {curprevkeyR}')
                            if isleft:
                                self.add_key_L(curkeyL, 'hovered')
                            elif isright:
                                self.add_key_R(curkeyR, 'hovered')
                            elif isleft and isright:
                                self.add_key_R(curkeyR, 'hovered')
                                self.add_key_L(curkeyL, 'hovered')
                        pygame.display.update()
                self.canmove = False

            self.keyboard.draw(self.screen)
            pygame.display.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode',
        nargs='?',
        default='Left',
        help='Cursor Mode'
    )
    parser.add_argument(
        'layout_name',
        nargs='?',
        type=kl.LayoutName,
        default=kl.LayoutName.QWERTY,
        help='the layout_name to use'
    )
    args = parser.parse_args()
    typetool = TypingTool(args.layout_name, args.mode)
