#   Author: Sean Saathoff
#   Goal:   Crawl a small social-graph of Twitter users via Twitter's public
#           API, and use your PageRank implementation to find influential users in
#           the social-graph.

from urllib2 import *
import json
import numpy as np
import time


# Crawl a Twitter user's profile given the user's ID
def get_user(user_id):

    # The API to get user profile
    url = "http://api.twitter.com/1/users/show.json?user_id=%d&include_entities=true" %(user_id)
    f = urlopen(url)
    
    # Transfer the data to JSON format
    user_dict = json.loads(f.read())
    #print user_dict
    
    f.close()
    return user_dict

# Crawl a Twitter user's friend IDs given the user's ID
def get_friend_ids(user_id):

    # The API to get user profile
    url = "http://api.twitter.com/1/friends/ids.json?user_id=%d&include_entities=true" %(user_id)
    f = urlopen(url)
    
    # Transfer the data to JSON format
    friend_ids = json.loads(f.read())
    #print friend_ids

    f.close()
    return friend_ids

# Crawl a Twitter user's follower IDs given the user's ID
def get_follower_ids(user_id):
    
    # The API to get user profile
    url = "http://api.twitter.com/1/followers/ids.json?user_id=%d&include_entities=true" %(user_id)
    f = urlopen(url)
    
    # Transfer the data to JSON format
    follower_ids = json.loads(f.read())
    #print follower_ids
    
    f.close()
    return follower_ids

# Show current status of rate limit
def get_rate_limit():
    url = "http://api.twitter.com/1/account/rate_limit_status.json"
    f = urlopen(url)

    rate_limit_status = json.loads(f.read())

    f.close()
    return rate_limit_status

#create link matrix from a file
def create_link_matrix(transition_matrix_filename):
    f = open(transition_matrix_filename, 'rU')
    num_rows = 0
    for line in f:
        line = line.split()
        if int(line[0]) > num_rows:     #count number of nodes in graph
            num_rows = int(line[0])
        elif int(line[1]) > num_rows:
            num_rows = int(line[1])
    
    link_matrix = np.zeros(shape=(num_rows, num_rows))  #create graph
    f.close()
    f = open(transition_matrix_filename, 'rU')
    for line in f:
        line = line.split()
        link_matrix.itemset((int(line[0])-1,int(line[1])-1), int(line[2]))  #insert edges
    row_count = 0
    for row in link_matrix:
        column_count = 0;
        row_sum = sum(row)
        if row_sum != 0:
            for item in row:            #normalize each row
                item = item/row_sum
                link_matrix.itemset(row_count,column_count, item)
                column_count += 1
        elif row_sum == 0:
            for item in row:
                item = 1/num_rows
        row_count += 1
        
    return link_matrix              #return link matrix



def main():

        seed_user_id = 55858928

        friend_ids = get_friend_ids(seed_user_id)   #get root's friends
        follower_ids = get_follower_ids(seed_user_id)   #get root's followers
        friend_ids.extend(follower_ids)
        all_ids = set(friend_ids)       #get rid of duplicates
        user_dict_key_node = {}         #key = node (1,2,3) value = twitter id
        user_dict_key_id = {}           #key = twitter id, value = node
        count = 0
        for id in all_ids:              #create dictionaries
            user_dict_key_node[count] = id
            user_dict_key_id[id]=count
            count += 1
        
        #add root user to dictionaries
        user_dict_key_node[count] = seed_user_id
        user_dict_key_id[seed_user_id] = count

        tele_matrix = np.zeros(shape=(len(user_dict_key_node)-1,len(user_dict_key_node)-1))
        tele_matrix.fill(1.0/len(user_dict_key_node))
                
        #file to write crawling results to, later to be read to create link matrix
        f = open("crawler.txt", "w")
    
        for temp_id in user_dict_key_node:
    
            print temp_id
            time.sleep(28)  #There is a rate limit on Twitter API calls. This ensures we don't go above it.
            #get friend ids
            try:
                temp_friend_ids = get_friend_ids(user_dict_key_node[temp_id])
                if len(temp_friend_ids) < 1000:
                    for friend_id in temp_friend_ids:       #if in the set_first_hop, store link from id
                        if friend_id in user_dict_key_id:
                            f.write("%s %s 1\n"  % (str(temp_id), str(user_dict_key_id[friend_id])))
        
                time.sleep(28) #There is a rate limit on Twitter API calls. This ensures we don't go above it.
                #get follower ids
                temp_followers_ids = get_follower_ids(user_dict_key_node[temp_id])
                if len(temp_followers_ids) < 1000:
                    for follower_id in temp_followers_ids:    #if in the set_first_hop, store link to id
                        if follower_id in user_dict_key_id:
                            f.write("%s %s 1\n"  % (str(user_dict_key_id[follower_id]), str(temp_id)))
        
                print get_rate_limit()
    
            except:
                pass

        f.close()
                    
        link_matrix = create_link_matrix("crawler.txt")

        link_matrix = .9*link_matrix            #multiply by 1-alpha
        tele_matrix = .1*tele_matrix

        trans_prob_matrix = link_matrix + tele_matrix       #get final transistion matrix
                
        vector_mat = np.zeros(shape=(1, len(user_dict_key_node)-1)) #initial vector 
        vector_mat.itemset(0, 0, 1)

        count = 0;
        while True:     #loop through until vector converges
            count += 1
            next_vect = np.dot(vector_mat,trans_prob_matrix)
            if (np.around(next_vect, decimals = 3) == np.around(vector_mat, decimals = 3)).all():   #check convergence to 3 decimal points
                break
            vector_mat = next_vect
        
        pagerank_scores = []
        top_pagerank_scores = []
        bottom_pagerank_scores = []

        count = 0
        for item in next_vect[0]:       #create list of tuples with node number and PR score
            pagerank_scores.append((count, item))
            count += 1

        pagerank_scores = sorted(pagerank_scores, key=lambda x: x[1], reverse = True)   #sort high to low
        for i in range(0,10):
            id = user_dict_key_node[pagerank_scores[i][0]+1]    #get twitter id's for top 10 scores
            top_pagerank_scores.append((id, pagerank_scores[i][1]))

        print "Top 10 PageRank scores:"
        print top_pagerank_scores

        pagerank_scores = sorted(pagerank_scores, key=lambda x: x[1], reverse = False)  #sort low to high
        for i in range(0,10):
            id = user_dict_key_node[pagerank_scores[i][0]+1]    #get twitter id's for bottom 10 scores
            bottom_pagerank_scores.append((id, pagerank_scores[i][1]))

        print "Bottom 10 PageRank scores:"
        print bottom_pagerank_scores


if __name__ == '__main__':
    main()
