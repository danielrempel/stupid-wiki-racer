WikiGamer  
A python script to perform wiki-racing in the English Wikipedia.  
  
There are two variations of the script:
* wg.py, which is the single-threaded and very slow version and
* wg-parallel.py, which is the multiple-threaded version which works a lot faster
As of now they have different output and wg.py is expected to have a lot more bugs, if there are any.  
  
The script tries to cheat and checks the Main_Page also.;)  
  
To run both of the scripts you must provide two *proper* names of articles:  
```
python wg[-parallel].py "Rifle" "Philosophy"
```
  
P.S.: the script eats memory on big depth levels for obvious reasons. And the amount of threads (wg-parallel.py:35)  must be set somewhere between your processors count and your Internet connection capabilities.
