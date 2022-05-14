# CSE312

# Installation
* STEP 1: Clone the repo to your local machine 
* STEP 2: Open your termanal and navigate to the project directory
* STEP 3: Run `docker compose up --build`
* STEP 4: Open FireFox or Chrome, and navigate to http:localhost:8080

# Testing Procedure for Grading Purpose

## User Accounts with Secure Authentication
<p>The initial page is the sign in page. Click sign up button to create an account. </p>
<p>Use the created account to login.</p>
<p>Our backend will set up a cookie for user. Check within the browser console.</p>
<p>If you delete the cookie and refresh the page, that will give you Internal Server Error</p>

## See all users who are currently logged in
<p>After logining your account, you enter our home page, which includes event seciton and Current online logged in user section </p>

## Users can send direct messages (DM) to other users with notifications when a DM is received
<p>Create two or more account and sign in the home page</p>
<p>Click `Start Chat!` button, chat panel will appear at the end of the page.</p>
<p>User can send direct message to public or private message(excepts themselves)</p>
<p>When user receives the private message, the nofitication will appear on the buttom right of the page for the receiver</p>

## Users can share some form of multimedia content which is stored and hosted on your server

<p>User can  watch the video and chat with each other, as well as emoji</p>
<p>User can aslo upload the image as their profile avatar(support gif,jpg,png,etc)</p>

## Live interactions between users via WebSockets (Cannot be text)

<p>In current online user section of the home page, there is a `video` button.</p>
<p>Before testing the video chat, make sure your broswer has access to the camera.</p>
<p>Choose a online user other than you, click `Video` button, and that will FORCE open your camera and targeted user camera. (LOL Just for your testing convenience)</p>




# University at Buffalo, CSE312
# Author:
### weidajia
### lchen78
### esenche
### rlin27
### yajinghu

# Reference:
* [Flask](https://flask.palletsprojects.com/en/2.1.x/)
* [Bootstrap 4.3](https://getbootstrap.com/docs/4.3/getting-started/introduction/)
* [MongoDB](https://www.mongodb.com/)
