import requests
import json
import time

print("Enter studio ID:")

studio_id = input()

print("Enter offset to start with:")

offset = int(input())

def get_comment(studio_id, offset):
    return json.loads(requests.get(f"https://api.scratch.mit.edu/studios/{studio_id}/comments/?offset={offset}").text)

reply_depth = 100

wait_time = 0.1

i = 0

comments_shown = -1

while(comments_shown != 0):
    comments_shown = len(get_comment(studio_id, offset))

    print(offset)

    time.sleep(wait_time)

    offset = offset * 2

    i += 1

low = int(offset / 4)
high = int(offset / 2)

while(low != int((low + high) / 2)  ):
    offset = int((low + high) / 2)

    if (len(get_comment(studio_id, offset)) == 0):
        high = offset

    else:
        low = offset

    print(offset)

    time.sleep(wait_time)

top_level_comments = offset

counted_replies = 0

for i in range(reply_depth):
    counted_replies += get_comment(studio_id, int((i / reply_depth) * top_level_comments))[0]["reply_count"]

    print(i)

    time.sleep(wait_time)

average_replies = counted_replies / reply_depth

estimated_comments = top_level_comments * (average_replies + 1)

print(f"Number of top-level-comments: {top_level_comments}")

print(f"Estimated average number of replies: {average_replies}")

print(f"Estimated number of comments: {estimated_comments}")