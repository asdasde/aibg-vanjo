import sys
from nidzobot import Bot
import time

bot = Bot()
while True:
    line = sys.stdin.readline()
    start_time = time.time()
    bot.parse_line(line)
    bot.calculate_next_move()
    bot.play_move()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time}", file=sys.stderr, flush=True)
    print(f"turn {bot.turn} : {bot.players[bot.us].energy} xp: {bot.players[bot.us].xp}", file=sys.stderr, flush=True)