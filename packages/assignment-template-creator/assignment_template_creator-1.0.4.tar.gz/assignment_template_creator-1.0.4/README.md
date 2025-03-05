# Project-Template
Behold : the ultimate tool for CS students when it comes to creating the same directory structure and report template for EVERY. SINGLE. ASSIGNMENT. I'm sure you're tired of that too. Hopefully. Becaude I just spent an embarrasingly long amout of times automating this, and, quite frankly, I would have saved so much time just doing it manually for the rest of my academic career.But here you go anyway. 

# Features 

Now, onto the fun stuff. 

### Language Support
This template builder supports the following languages : 
- Java 
- Python 
- C++
- C 
- JavaScript 
- Haskell

The user can aslo choose to not select any of the above, in whichcase no language-specific files are going to be created in the `src/` directory. 

When filling in your project details, you can select to either build a group or individual project. 
### Individual Project Setup
```bash
|---- src
|      \_____ main.xx # main, language-specific file
|      \_____ runXX.sh # script or Makefile to run your files
|      \_____ run_tests.py # optional testing file (see 'Testing Options')
|      \_____ Custom-Tests # optional testing folder (see 'Testing Options')
|               \_____ test1.in # sample test files 
|               \_____ test1.out
|               \_____ test2.in
|               \_____ test2.out
|---- W0X-Report.md
```
### Group Project Setup
```bash
|---- Code
|      \_____ src
|              \_____ main.xx # main, language-specific file
|              \_____ runXX.sh # script or Makefile to run your files
|              \_____ run_tests.py # optional testing file (see 'Testing Options')
|              \_____ Custom-Tests # optional testing folder (see 'Testing Options')
|                       \_____ test1.in # sample test files 
|                       \_____ test1.out
|                       \_____ test2.in
|                       \_____ test2.out
|---- Reports 
|       \____ Individual-Report.md
|       \____ Group-Report.md
```

### Report Formats 
This template supports both .md and .docx repoort formats.

### Testing Options
The user can choose to select one of the two testing options : 

1. Automatic Testing Table Generation : The testing table in the report will be populated automatically by test names, expected outputs, and actual outputs, extracted form the Custom-Tests directory, which the user can fill with their own `.in` and `.out` files. The testing table can be updated by running `python3 run_tests.py`
2. Custom stacscheck Output : running `python3 run_tests.py` will print out a stacscheck-style output, based on the contents of your Custom-Tests foler.

The user can also skip this stet, in which case no `Custom-Tests` directory and `run_tests.py` file will be generated. If the user did not select a language proir to selecting one of the testing options, the script will fail, and will need to be modified to compile and run the project's language. 

# Installation 
This package is available on PyPI. Just run
```
pip install assignment-template-creator==1.0.3
```
Then, to run it
```
create_template
```
And you're all set ! I hope someone actually uses this. 
