# Tools for data analysis on Omnet++
The following tools are provided:
- install_tools.py
- update_template.py
- make_runfile.py
- parse_data.py
- analyze_data.py
- scan_datafile.py

## install_tools
Script used to install the present tools in the Omnet++ directories. The Omnet++ environment variables must be set (invoke .setenv script in Omnet++ before attemptint to install). The tools will be installed in the bin/ diretory of the Omnet installation in the form of symlinks.

## update_template
Tool to create files from a directory containing .mako templates. All found .mako templates will be processed.
The name of the created file will be based on the template name, stripping the .mako extension. For example:
- file1.ned.mako -> file1.ned
- file2.ini.maki -> file2

If the file already exists, the file will be re-created only if the tempalte is newer than the file or if the *-f* switch is used.

Relevant paramters:
-  *-h*, *--help*: show help and exit
-  *-f*, *--force*: force update
-  *-r*, *--recursive*: enable recursive search of tempalted in sub-directories
-  *-d DIR*, *--dir DIR*: directory to work on (default ./)
-  *-c CONFIG*, *--config CONFIG*: YAML Configuration file (default None). The dta structure of the YAML file will be made available in the confiuguration dictioary to all the templates processed. Useful if multiple tempaltes must rely on the same configurations (e.g., .ini files and .json file for data analysis)

## make_runfile
Create Runfile (it is baically a Makefile) to tun multiple Omnet++ experiments in parallel (using the make command and its -j option). The script reads the configuration for a Omnet++ .ini file and generates the command to run all the exeriemnts for every considered configuration (excluding configuration cotaining the *NORUN* string in their name).

Relevant paramters:
-  *-h*, *--help*: show help and exit
-  *-z*, *--zip*: The output of the simulation (.sca file) will be automatically compressed with gzip. This paamter can save lot of disk space when running large experimental campaigns
-  *-o OUTPUT*, *--output OUTPUT* output file (efault: *Runfile*)
-  -f FILE, --file FILE  input file (default *omnetpp.ini*)

## parse_data
Parse a set of .sca files (related to multiple runs and configurations of the same experiment) and store the relevant results in a database.

The results are organized as *sceanrios* and *runs* of the same sceanrio. A sceanrio is identified by a set of parameters that set the sceantios apart frome each other. For example if we are studying a server load surve the sceanrios can be set apart by the *rho* load parameter or by the *lambda* incoming request rate.
For each experiment we collect several *metrics* that can be aggregated (for example if we have several computing nodes, the utilization metric would be referred to each node, but we may be interested in collecting only the average a standard deviation of this metric).

The tools can alo collect data in the form of histograms

Relevant paramters:
-  *-h*, *--help*: show help and exit
-  *-r*, *--reset*: re-create database
-  *-c CONFIG*, *--config CONFIG*: .json config file with the definition of every sceanrio and metric (default *config.json*)
-  *-d DB*, *--db DB*: database file (default *test.db*)
-  *-j JOBS*, *--jobs JOBS*: number of parallel tasks to parse .sca files (default 1)
-  *F*: list of .sca files to process

## analyze_data
Second step of data processing tools. From the database crated with *parse_data* we create a set of data files ready to plot or to further process with pandas or R. The configuration is in the same .json file used for parse_data. For each analysis we reprt the output files, the parameters in the sceanrio that are to be kept fixed and the sceanrio parameter to scan (thay will beused to crate the rows of the data file). The output will have a set of column describing the trajectory in the sceanrio space and a set of columns for the selected metrics. For each metric we provide the value (averaged over the runs of the same scenario) and the standard deviation of the parameter over the runs (sigma-labelled column).

Also histograms can be extracted from the database.

Relevant paramters:
-  *-h*, *--help*: show help and exit
-  *-c CONFIG*, *--config CONFIG*: .json config file with the definition of sceanrios, metrics and analyses (default *config.json*)
-  *-d DB*, *--db DB*: database file (default *test.db*)
-  *-v*: verbose mode

## scan_datafile
Simple tools to list the columns of a data file creted by *analyze_data*.