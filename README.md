# Project :- File Transfer Protocol (Python 3 Implementation)


* Implemented File Transfer Protocol and some of its commands using Python 3 programming language
* Project consists of FTP server which is multithreaded so that multiple clients can connect at a time
* And FTP client part which can connect to server after its authentication
* Implemented commands like **get**, **put**, **mget**, **mput**, **hash**, **mkdir**, **delete**, **mdelete**, **ls**, **lcd**, **cd**, **exit**, etc.



### Instructions to run the project:-


* **python server.py PORT_NUMBER**

* In second terminal, **python client.py SERVER_IP SERVER_PORT_NUMBER**
  * You will be asked for username and password for authentication, which should be present in users.txt
  
* In FTP client, type **help**, to list all the available commands and their purpose

* **ServerFolder** & **ClientFolder** are the directories simulating server and clients file storages
