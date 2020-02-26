import requests
import json
import pygame
from string import ascii_lowercase
pygame.init()


class Searcher:
    def __init__(self):
        self.url = "https://wordsapiv1.p.rapidapi.com/words/"
        self.headers = {
            "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
            "x-rapidapi-key": ""
        }

    def req(self, word: str) -> dict:
        """
        Requests word provided
        :param word: Word to search
        :return: Dict containing all info about the word
        """
        res = json.loads(requests.get(f"{self.url}{word}", headers=self.headers).text)
        if res.get("word"):
            word = res.get("word")
            if "syllables" in res:
                syl = res.get("syllables").get("count")
            else:
                syl = "N/A"
            pro = res.get("pronunciation") if isinstance(res.get("pronunciation"), str) else res.get("pronunciation").get("all")
            if res.get("results"):
                defs = [
                    (
                        i.get("definition"),
                        i.get("synonyms") if i.get("synonyms") is None else [k.replace(" ", "-") for k in i.get("synonyms")],
                        i.get("partOfSpeech")
                     ) for i in res.get("results")
                ]
            else:
                defs = []
            return {"word": word, "pronunciation": str(pro), "syl": str(syl), "defs": defs}
        else:
            return {"word": "Word not found", "pronunciation": "N/A", "syl": "N/A", "defs": []}


def word_wrapper(words: list, length: int, space_char: str) -> list:
    """
    Wraps words for a certain length
    :param words: Words to use
    :param length: Max length of line
    :return: List of wrapped words
    """
    wrapped = []
    start = 0
    for pos, word in enumerate(words):
        if len(space_char.join(words[start:pos + 1])) > length:
            wrapped.append(space_char.join(words[start:pos]))
            start = pos
        if pos == len(words) - 1:
            wrapped.append(space_char.join(words[start:]))
    return wrapped


# Get width and height of monitor
width, height = 1920, 1080
display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Creating word searcher
s = Searcher()

# GUI fonts
normal_font = pygame.font.SysFont("Courier", 30, bold=True)
main_word_font = pygame.font.SysFont("Courier", 80, bold=True)
small_main_word_font = pygame.font.SysFont("Courier", 60, bold=True)

# Misc variables
running = True
typed_txt = ""
data = None

# GUI object positions
search_box = pygame.Rect(0, 0, 800, 60)
search_box.center = (width // 2, height - 100)
main_word_rect = pygame.Rect(10, 10, 1000, 100)
pronun_rect = pygame.Rect(1020, 10, 700, 100)
syl_rect = pygame.Rect(1730, 10, 180, 100)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            for asc, pressed in enumerate(pygame.key.get_pressed()):
                if pressed and chr(asc).lower() in ascii_lowercase and len(typed_txt) <= 40:
                    typed_txt += chr(asc).lower()
            if event.key == pygame.K_BACKSPACE:
                typed_txt = typed_txt[:len(typed_txt) - 1]
            if event.key == pygame.K_RETURN:
                data = s.req(typed_txt)
                typed_txt = ""

    display.fill((255, 255, 255))

    # |                            |
    # | Anything drawn write below |
    # V                            V

    # Drawing search box and text
    pygame.draw.rect(display, (0, 128, 255), search_box)
    display.blit(normal_font.render(typed_txt, True, (0, 0, 0)), ((search_box.x + (search_box.width // 2)) - ((len(typed_txt) * 18) // 2), search_box.y + (search_box.height // 4)))

    # Drawing search results area
    pygame.draw.rect(display, (0, 255, 128), main_word_rect)
    pygame.draw.rect(display, (0, 255, 128), pronun_rect)
    pygame.draw.rect(display, (0, 255, 128), syl_rect)

    if data is not None:
        display.blit(main_word_font.render(data["word"], True, (0, 0, 0)), main_word_rect)
        display.blit(small_main_word_font.render(data["pronunciation"], True, (0, 0, 0)), (pronun_rect.x, 20))
        display.blit(main_word_font.render(data["syl"], True, (0, 0, 0)), (syl_rect.x, 10))

        for pos, def_ in enumerate(data["defs"]):
            if pos > 7:
                break
            # Creating background shapes for text
            pygame.draw.rect(display, (0, 255, 255), pygame.Rect(10, (100 * (pos + 1)) + 20, 1000, 80))
            pygame.draw.rect(display, (0, 255, 255), pygame.Rect(1020, (100 * (pos + 1)) + 20, 700, 80))
            pygame.draw.rect(display, (0, 255, 255), pygame.Rect(1730, (100 * (pos + 1)) + 20, 180, 80))

            # Looping through definitions and writing them
            for occr, txt in enumerate(word_wrapper(def_[0].split(" "), 55, " ")):
                display.blit(normal_font.render(txt, True, (0, 0, 0)), (10, (100 * (pos + 1)) + 20 + (occr * 25)))

            # Writing synonyms
            if def_[1]:
                for line, word in enumerate(word_wrapper(def_[1], 40, ", ")):
                    display.blit(normal_font.render(word, True, (0, 0, 0)), (1020, (100 * (pos + 1)) + 20 + (line * 25)))

            # Writing word type
            if def_[2]:
                for line, word in enumerate(word_wrapper(def_[2].split(" "), 10, " ")):
                    display.blit(normal_font.render(word, True, (0, 0, 0)), (1730, (100 * (pos + 1)) + 20 + (line * 25)))

    pygame.display.update()
    clock.tick(60)


pygame.quit()
