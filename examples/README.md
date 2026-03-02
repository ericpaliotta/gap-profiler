# Examples of Profiler Functionality

Within this directory are several sets of files for different kinds of examples of profiler use. These profilers are used for demonstrating several kinds of parser functionality as well as end-to-end by hand testing.
<br>
In each sub-directory of this directory there should be one file when the repository is cloned:
- dirname.g
two more files will be generated upon running gen_examples.sh
- dirname.json
- dirname.zip
to generate all such files, run the following commands
```
export PATH=$PATH:/path/to/your/gap/distribution
source gen_examples.sh
```
to clear the files run 
```
source clear_examples.sh
```

**NOTES** 
- these .zip and .json files should never be committed to the repository as their data is specific to the machine they are run on
- the above scripts will not work on windows, for information on manual example generation nsee the below sections

## dirname.g
This file is the gap code being profiled for the example. These files should be able to be run using the usual command `<path to gap distribution> dirname.g`. For uniformity, all of these files should follow the same general outline

```
ProfileLineByLine("dirname.json");

## insert code here ##

UnprofileLineByLine();
QUIT;
```

## dirname.json
This file is the output line-by-line profile of the gap code run previously. This is an intermediate output file which is not directly usable. Do not alter this file, as it will corrupt the ability of the parser module to generate anything useful from it. To parse this file use the commmand `<path to parser.py> dirname.json dirname.zip <(optional) path to current directory>`.

## dirname.zip
This is the final profile as output by the parser module. This zip file contains all of the files used by the program being run as well as some Json files containing metadata necessary for profile visualization. To visualize the final profile run `<path to main.py> dirname.zip`
