#pastewits
Python script to follow and scrape all links posted by a pastebin bot with additional code written to specifically scrape username:password and email address names from pastes in the most common formats then save those files as bson data to a mongodb collection on localhost.

Usage: python ./pastewits username

Note:
MongoDB insert code is not completed and was written as to work with arbitrary test accounts. If processed text is incompatible with MongoDB BSON architecture, it will throuw errors. In it's current state one may decide to either save the file as plaintext or CSV for immediate use. The intended goal of this project is to process and discover the usage type of input data (email,user name,password,& ) using natural language algorithms to create mongobdb collections as standardized repositiries of discovered data while parsing inputs through tests for compatability with javascript object notation ergo BSON storage.
