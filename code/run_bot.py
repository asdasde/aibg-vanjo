import sys
from nidzobot import Bot

bot = Bot()
while True:
    line = sys.stdin.readline()
    bot.parse_line(line)
    bot.calculate_next_move()
    bot.play_move()