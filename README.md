# p05 by SARDines
## Roster:
Rohan Sen - Project Manager (PM) </br>
David Lee - F Student (innovator) </br>
Sean Zheng - A Student (blue collar) </br>
Araf Hoque - D Student (entrepeneur) </br>

## Description
A one-stop shop for frequent nyc commuters, or in other words, a multi-purpose transit system guide targetting city folks. Simple transit maps provided by apps such as Google or Apple Maps provide limited functionality. We are solving this limited functionality through incorporating visualization of trains' live positions, live delays, elevator/escalator status, and more specific details.

#### Visit our live site at [https://softdev.rohansen.com/]()

## Install guide
1) Clone the repo into a local directory:
```
git clone git@github.com:dlee08/SARDines-szhang60stuy-araf215-rohansen08-dlee08.git SARDines
```
2) Enter the app directory:
```
cd SARDines
```
3) Open a virtual environment:
```
python3 -m venv venv
```
4) Activate virtual env for Linux, Windows, or Mac:

i. Linux
```
. venv/bin/activate
```
ii. Windows
```
venv\Scripts\activate
```
iii. Mac
```
source venv/bin/activate
```
5) Install necessary modules:
```
pip install -r requirements.txt
```  
6) After running the launch codes and utilizing the app, exit the virtual environment:
```
deactivate
```

## Launch codes
1) Run the app through Flask:
```
python app/__init__.py
