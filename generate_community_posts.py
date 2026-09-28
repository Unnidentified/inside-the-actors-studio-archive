import os

base_file = "/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes/reddit_post_global-new.txt"

with open(base_file, "r", encoding="utf-8") as f:
    base_text = f.read()

# 1. r/lostmedia version
text_lostmedia = base_text.replace(
    "I've already posted it to r/lostmedia (post now deleted), r/ForgottenTV ([post](https://www.reddit.com/r/ForgottenTV/comments/1wem0ga/inside_the_actors_studio_1994_an_almost_complete/)) and r/DHExchange. ([post](https://www.reddit.com/r/DHExchange/comments/1wem2qq/inside_the_actors_studio_1994_an_almost_complete/)), and to r/acting ([post](https://www.reddit.com/r/acting/comments/1wenhsn/inside_the_actors_studio_1994_an_almost_complete/))",
    "I've already posted it to r/ForgottenTV ([post](https://www.reddit.com/r/ForgottenTV/comments/1wem0ga/inside_the_actors_studio_1994_an_almost_complete/)) and r/DHExchange. ([post](https://www.reddit.com/r/DHExchange/comments/1wem2qq/inside_the_actors_studio_1994_an_almost_complete/)), and to r/acting ([post](https://www.reddit.com/r/acting/comments/1wenhsn/inside_the_actors_studio_1994_an_almost_complete/))"
)
with open("/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes/reddit_post_lostmedia.txt", "w", encoding="utf-8") as f:
    f.write(text_lostmedia)

# 2. r/ForgottenTV version
text_forgottentv = base_text.replace(
    "r/ForgottenTV ([post](https://www.reddit.com/r/ForgottenTV/comments/1wem0ga/inside_the_actors_studio_1994_an_almost_complete/)) and ",
    ""
)
with open("/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes/reddit_post_forgottentv.txt", "w", encoding="utf-8") as f:
    f.write(text_forgottentv)

# 3. r/DHExchange version
text_dhexchange = base_text.replace(
    " and r/DHExchange. ([post](https://www.reddit.com/r/DHExchange/comments/1wem2qq/inside_the_actors_studio_1994_an_almost_complete/))",
    ""
)
with open("/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes/reddit_post_dhexchange.txt", "w", encoding="utf-8") as f:
    f.write(text_dhexchange)

print("Generated community variants successfully from reddit_post_global-new.txt.")
