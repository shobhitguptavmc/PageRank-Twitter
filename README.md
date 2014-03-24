PageRank-Twitter
================

Crawl a small social-graph of Twitter users via Twitter's public API, and use your PageRank implementation to find influential users in the social-graph.

This was a school assignment for the class Information Storage and Retrieval taught by Dr. Caverlee. This function takes a twitter user id (the variable in the function is seed_user_id) and then calculates the top and bottom pagerank scores based on the seed user's friends and followers, and those user's friends and followers.  Because of Twitter's rate limiting on API calls, this code takes a LONG time to run so I do not recommend running it.
