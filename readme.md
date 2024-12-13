# Final Project: User Management
### by Lydia Daids

## New Feature: User Profile Management
Added a user profile management feature that does the following:
- Designed and implemented a feature that enables users to seamlessly update profile details, including name, bio, and location, through an intuitive and flexible API.
API endpoint: /users/updateProfile

- Developed a robust functionality that permits managers and administrators to elevate a user's status to "professional."
API Endpoint: /users/{user_id}/updateToProfessional

- Introduced an automated email notification system to inform users when their status is upgraded to "professional," ensuring they are promptly notified of changes.

## 5 Issues Fixed
### Issue 1
ANONYMOUS UserRole and None showing in email verification link
[Fixed Issue 1 Linked Here](https://github.com/LydD20/user_management/issues/1)

### Issue 2
Issue with building Docker Container due to libr code
[Fixed Issue 2 Linked Here](https://github.com/LydD20/user_management/issues/2)

### Issue 3
Issue with Github Actions not working, no workflow running
[Fixed Issue 3 Linked Here](https://github.com/LydD20/user_management/issues/3)

### Issue 4
There was no password validation which is considered a security issue
[Fixed Issue 4 Linked Here](https://github.com/LydD20/user_management/issues/4)

### Issue 5
Found a vulnerability in requirements.txt with python-multipart
[Fixed Issue 4 Linked Here](https://github.com/LydD20/user_management/issues/5)

## 10 New Tests
For tests, I added in new tests for the new feature as well as some tests for current code to improve coverage.
### Links to Test Code Below:
https://github.com/LydD20/user_management/commit/70a82ec4772b0b4db686f27302f98952e793efb3
https://github.com/LydD20/user_management/commit/7425674b6595424bcfeac0300d80ef5c00519906
https://github.com/LydD20/user_management/commit/5ec7a0af6ebc00a5c42ab6265c4b241f95fa698d
https://github.com/LydD20/user_management/commit/0a1afe57f04d0cb47ed09a531fd9a510226f8752

## Reflection
[Final Reflection Paper.docx](https://github.com/user-attachments/files/18127243/Final.Reflection.Paper.docx)

## Docker Repository
https://hub.docker.com/repository/docker/lydiadaids/user_management/general
